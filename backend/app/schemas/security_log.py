"""
Pydantic schemas for security logs.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime
from uuid import UUID


class SecurityLogResponse(BaseModel):
    """Response schema for security logs."""
    id: UUID = Field(..., description="Security log ID")
    provider_name: str = Field(..., description="Provider name")
    event_type: str = Field(..., description="Type of security event")
    ip_address: str = Field(..., description="Client IP address")
    request_id: str = Field(..., description="Request ID")
    details: Dict[str, Any] = Field(..., description="Event details")
    created_at: datetime = Field(..., description="When event occurred")
    
    class Config:
        from_attributes = True
