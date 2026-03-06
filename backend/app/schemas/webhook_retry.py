"""
Pydantic schemas for webhook retry responses.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class WebhookRetryResponse(BaseModel):
    """Response schema for webhook retry."""
    id: UUID = Field(..., description="Retry record ID")
    webhook_event_id: UUID = Field(..., description="Webhook event ID")
    attempt_number: int = Field(..., description="Attempt number")
    next_retry_at: datetime = Field(..., description="When next retry is scheduled")
    status: str = Field(..., description="pending, delivered, failed, dead_lettered")
    response_status: Optional[int] = Field(None, description="HTTP status from last attempt")
    response_body: Optional[str] = Field(None, description="Response body from last attempt")
    error_message: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(..., description="When retry was created")
    updated_at: datetime = Field(..., description="When retry was last updated")
    
    model_config = ConfigDict(from_attributes=True)


class DeadLetterQueueResponse(BaseModel):
    """Response schema for dead letter queue item."""
    id: UUID = Field(..., description="Retry record ID")
    webhook_event_id: UUID = Field(..., description="Webhook event ID")
    attempt_number: int = Field(..., description="Number of attempts made")
    status: str = Field(..., description="dead_lettered")
    error_message: str = Field(..., description="Reason for failure")
    created_at: datetime = Field(..., description="When retry was created")
    
    model_config = ConfigDict(from_attributes=True)
