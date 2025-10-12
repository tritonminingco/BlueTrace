"""Admin endpoints for API key management."""
from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import generate_api_key, get_admin_api_key
from app.db.session import get_db
from app.models.api_key import APIKey

router = APIRouter()


class CreateAPIKeyRequest(BaseModel):
    """Request model for creating API keys."""
    
    name: str = Field(..., min_length=1, max_length=255)
    owner_email: EmailStr
    plan: str = Field(default="free", pattern="^(free|pro|enterprise)$")


class CreateAPIKeyResponse(BaseModel):
    """Response model for created API keys."""
    
    id: int
    name: str
    api_key: str
    prefix: str
    owner_email: str
    plan: str
    message: str


@router.post("/keys", response_model=CreateAPIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    db: AsyncSession = Depends(get_db),
    admin: APIKey = Depends(get_admin_api_key)
) -> CreateAPIKeyResponse:
    """
    Create a new API key (admin only).
    
    Args:
        request: API key creation request
        db: Database session
        admin: Admin API key (dependency)
        
    Returns:
        Created API key details including the full key (only shown once)
    """
    # Generate new API key
    full_key, prefix, key_hash = generate_api_key()
    
    # Create database record
    new_key = APIKey(
        name=request.name,
        key_hash=key_hash,
        prefix=prefix,
        owner_email=request.owner_email,
        plan=request.plan,
    )
    
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    
    return CreateAPIKeyResponse(
        id=new_key.id,
        name=new_key.name,
        api_key=full_key,
        prefix=prefix,
        owner_email=new_key.owner_email,
        plan=new_key.plan,
        message="API key created successfully. Save this key - it won't be shown again!"
    )

