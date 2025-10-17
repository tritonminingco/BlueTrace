"""API Key authentication and validation."""

import hashlib
import hmac
import secrets

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AuthenticationError
from app.db.session import get_db
from app.models.api_key import APIKey


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key with prefix.

    Returns:
        Tuple of (full_key, prefix, key_hash)
    """
    # Generate random key material
    key_material = secrets.token_urlsafe(32)

    # Determine prefix based on key type (secret key for now)
    prefix = "bt_sk_" + secrets.token_urlsafe(8)[:8]

    # Full key format: prefix.key_material
    full_key = f"{prefix}.{key_material}"

    # Hash the full key for storage
    key_hash = hash_api_key(full_key)

    return full_key, prefix, key_hash


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using HMAC-SHA256.

    Args:
        api_key: The full API key to hash

    Returns:
        Hexadecimal hash string
    """
    return hmac.new(settings.API_KEY_SALT.encode(), api_key.encode(), hashlib.sha256).hexdigest()


async def verify_api_key(api_key: str, db: AsyncSession) -> APIKey | None:
    """
    Verify an API key against the database.

    Args:
        api_key: The API key to verify
        db: Database session

    Returns:
        APIKey model if valid, None otherwise
    """
    # Hash the provided key
    key_hash = hash_api_key(api_key)

    # Look up in database
    result = await db.execute(
        select(APIKey).where(APIKey.key_hash == key_hash, APIKey.revoked_at.is_(None))
    )

    return result.scalar_one_or_none()


async def get_current_api_key(
    x_api_key: str | None = Header(None, alias="X-Api-Key"), db: AsyncSession = Depends(get_db)
) -> APIKey:
    """
    Dependency to get and validate the current API key.

    Args:
        x_api_key: API key from X-Api-Key header
        db: Database session

    Returns:
        APIKey model if valid

    Raises:
        AuthenticationError: If key is invalid or missing
    """
    if not x_api_key:
        raise AuthenticationError(
            message="Missing API key", hint="Include X-Api-Key header with your API key"
        )

    # Verify the key
    api_key_obj = await verify_api_key(x_api_key, db)

    if not api_key_obj:
        raise AuthenticationError(
            message="Invalid or revoked API key", hint="Check your API key or generate a new one"
        )

    return api_key_obj


# Optional dependency for admin-only routes
async def get_admin_api_key(api_key: APIKey = Depends(get_current_api_key)) -> APIKey:
    """
    Dependency to ensure the API key belongs to an admin.

    Args:
        api_key: Current API key

    Returns:
        APIKey if admin

    Raises:
        AuthenticationError: If not an admin key
    """
    # For now, check if email matches admin email
    if api_key.owner_email != settings.ADMIN_SEED_EMAIL:
        raise AuthenticationError(
            message="Admin access required", hint="This endpoint requires administrator privileges"
        )

    return api_key
