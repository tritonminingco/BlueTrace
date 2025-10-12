"""Tests for authentication."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import generate_api_key, hash_api_key, verify_api_key
from app.models.api_key import APIKey


class TestAuthGeneration:
    """Test API key generation."""
    
    def test_generate_api_key(self):
        """Test API key generation format."""
        full_key, prefix, key_hash = generate_api_key()
        
        assert full_key.startswith("bt_sk_")
        assert prefix.startswith("bt_sk_")
        assert len(key_hash) == 64  # SHA256 hex
        assert "." in full_key
    
    def test_hash_api_key_consistent(self):
        """Test that hashing is consistent."""
        key = "bt_sk_test.abc123"
        hash1 = hash_api_key(key)
        hash2 = hash_api_key(key)
        
        assert hash1 == hash2
        assert len(hash1) == 64


class TestAuthVerification:
    """Test API key verification."""
    
    @pytest.mark.asyncio
    async def test_verify_valid_key(self, db_session: AsyncSession, test_api_key):
        """Test verifying valid API key."""
        full_key, api_key_obj = test_api_key
        
        result = await verify_api_key(full_key, db_session)
        
        assert result is not None
        assert result.id == api_key_obj.id
        assert result.owner_email == api_key_obj.owner_email
    
    @pytest.mark.asyncio
    async def test_verify_invalid_key(self, db_session: AsyncSession):
        """Test verifying invalid API key."""
        result = await verify_api_key("bt_sk_invalid.key", db_session)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_verify_revoked_key(self, db_session: AsyncSession, test_api_key):
        """Test verifying revoked API key."""
        from datetime import datetime
        
        full_key, api_key_obj = test_api_key
        
        # Revoke the key
        api_key_obj.revoked_at = datetime.utcnow()
        await db_session.commit()
        
        result = await verify_api_key(full_key, db_session)
        
        assert result is None


class TestAuthEndpoints:
    """Test authentication on endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_without_auth(self, client: AsyncClient):
        """Test that health endpoint doesn't require auth."""
        response = await client.get("/v1/health")
        
        # Health should work without auth
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_key(self, client: AsyncClient):
        """Test protected endpoint without API key."""
        response = await client.get(
            "/v1/tides",
            params={
                "station_id": "TEST",
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z"
            }
        )
        
        assert response.status_code == 401
        assert "error" in response.json()
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_key(self, client: AsyncClient, test_api_key):
        """Test protected endpoint with valid API key."""
        full_key, _ = test_api_key
        
        response = await client.get(
            "/v1/tides",
            params={
                "station_id": "TEST",
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z"
            },
            headers={"X-Api-Key": full_key}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_admin_endpoint_requires_admin_key(self, client: AsyncClient, test_api_key):
        """Test that admin endpoint requires admin key."""
        full_key, _ = test_api_key
        
        response = await client.post(
            "/v1/admin/keys",
            json={
                "name": "New Key",
                "owner_email": "new@example.com",
                "plan": "free"
            },
            headers={"X-Api-Key": full_key}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_admin_endpoint_with_admin_key(self, client: AsyncClient, admin_api_key):
        """Test admin endpoint with admin key."""
        full_key, _ = admin_api_key
        
        response = await client.post(
            "/v1/admin/keys",
            json={
                "name": "New Key",
                "owner_email": "new@example.com",
                "plan": "pro"
            },
            headers={"X-Api-Key": full_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["plan"] == "pro"

