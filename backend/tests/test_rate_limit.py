"""Tests for rate limiting."""

import pytest
from httpx import AsyncClient

from app.core.rate_limit import RateLimiter


class TestRateLimiter:
    """Test rate limiter functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter()
        await limiter.initialize()

        try:
            # Should allow requests within limit
            for i in range(5):
                allowed = await limiter.check_rate_limit("test_key", 10, 60)
                assert allowed is True
        finally:
            await limiter.close()

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_over_limit(self):
        """Test that requests over limit are blocked."""
        limiter = RateLimiter()
        await limiter.initialize()

        try:
            # Fill up the limit
            for i in range(5):
                await limiter.check_rate_limit("test_key_2", 5, 60)

            # Next request should be blocked
            allowed = await limiter.check_rate_limit("test_key_2", 5, 60)
            assert allowed is False
        finally:
            await limiter.close()

    @pytest.mark.asyncio
    async def test_rate_limiter_get_remaining(self):
        """Test getting remaining requests."""
        limiter = RateLimiter()
        await limiter.initialize()

        try:
            # Make some requests
            for i in range(3):
                await limiter.check_rate_limit("test_key_3", 10, 60)

            # Check remaining
            remaining = await limiter.get_remaining("test_key_3", 10, 60)
            assert remaining <= 7  # Should have ~7 remaining
        finally:
            await limiter.close()


class TestRateLimitIntegration:
    """Test rate limiting integration with API."""

    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self, client: AsyncClient, test_api_key):
        """Test that rate limit headers are present in response."""
        full_key, _ = test_api_key

        response = await client.get(
            "/v1/tides",
            params={
                "station_id": "TEST",
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z",
            },
            headers={"X-Api-Key": full_key},
        )

        assert response.status_code == 200
        # Check for rate limit headers (simplified test)
        assert "X-RateLimit-Limit" in response.headers
