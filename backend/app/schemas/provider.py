"""
Pydantic schemas for provider management.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProviderCreate(BaseModel):
    """Schema for creating a new provider."""
    name: str = Field(..., description="Provider name (e.g., 'stripe', 'github')")
    secret_key: str = Field(..., description="HMAC secret key")
    forwarding_url: str = Field(..., description="Internal service URL to forward webhooks")


class ProviderUpdate(BaseModel):
    """Schema for updating a provider."""
    secret_key: Optional[str] = Field(None, description="New HMAC secret key")
    forwarding_url: Optional[str] = Field(None, description="New forwarding URL")
    is_active: Optional[bool] = Field(None, description="Enable/disable provider")


class ProviderResponse(BaseModel):
    """Schema for provider response."""
    id: UUID = Field(..., description="Provider ID")
    name: str = Field(..., description="Provider name")
    forwarding_url: str = Field(..., description="Forwarding URL")
    is_active: bool = Field(..., description="Is provider active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
