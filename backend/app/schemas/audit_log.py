"""
Pydantic schemas for audit logs.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class AuditLogResponse(BaseModel):
    """Response schema for audit log."""
    id: UUID = Field(..., description="Audit log ID")
    user_id: Optional[UUID] = Field(None, description="User who performed action")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource")
    resource_id: Optional[str] = Field(None, description="ID of resource")
    changes: Optional[dict] = Field(None, description="What changed")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    status: str = Field(..., description="success or failure")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="When action was performed")
    
    model_config = ConfigDict(from_attributes=True)
