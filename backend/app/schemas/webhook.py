"""
Pydantic schemas for webhook requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class WebhookRequest(BaseModel):
    """
    Schema for incoming webhook payload.
    
    This validates the structure of webhook data.
    """
    event_type: str = Field(..., description="Type of event (e.g., 'payment.succeeded')")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: Optional[str] = Field(None, description="Event timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "payment.succeeded",
                "data": {"amount": 100, "currency": "USD"},
                "timestamp": "2025-02-22T10:30:00Z"
            }
        }


class WebhookResponse(BaseModel):
    """
    Response after webhook is processed.
    """
    status: str = Field(..., description="Status of webhook processing")
    message: str = Field(..., description="Status message")
    webhook_id: Optional[str] = Field(None, description="ID of stored webhook event")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "accepted",
                "message": "Webhook received and queued for processing",
                "webhook_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
