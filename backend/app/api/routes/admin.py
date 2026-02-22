"""
Admin API routes for provider management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import uuid

from app.db.session import get_db
from app.db.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderUpdate, ProviderResponse


router = APIRouter()


@router.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_data: ProviderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new webhook provider."""
    # Check if provider already exists
    stmt = select(Provider).where(Provider.name == provider_data.name)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Provider '{provider_data.name}' already exists"
        )
    
    # Create new provider
    provider = Provider(
        id=uuid.uuid4(),
        name=provider_data.name,
        secret_key=provider_data.secret_key,
        forwarding_url=provider_data.forwarding_url,
        is_active=True
    )
    
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    
    return provider


@router.get("/providers/{provider_name}", response_model=ProviderResponse)
async def get_provider(
    provider_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get provider by name."""
    stmt = select(Provider).where(Provider.name == provider_name)
    result = await db.execute(stmt)
    provider = result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )
    
    return provider


@router.put("/providers/{provider_name}", response_model=ProviderResponse)
async def update_provider(
    provider_name: str,
    provider_data: ProviderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a provider."""
    stmt = select(Provider).where(Provider.name == provider_name)
    result = await db.execute(stmt)
    provider = result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )
    
    # Update fields if provided
    if provider_data.secret_key:
        provider.secret_key = provider_data.secret_key
    if provider_data.forwarding_url:
        provider.forwarding_url = provider_data.forwarding_url
    if provider_data.is_active is not None:
        provider.is_active = provider_data.is_active
    
    await db.commit()
    await db.refresh(provider)
    
    return provider


@router.delete("/providers/{provider_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a provider."""
    stmt = select(Provider).where(Provider.name == provider_name)
    result = await db.execute(stmt)
    provider = result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )
    
    stmt = delete(Provider).where(Provider.name == provider_name)
    await db.execute(stmt)
    await db.commit()
