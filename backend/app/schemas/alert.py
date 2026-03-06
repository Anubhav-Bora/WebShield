"""
Pydantic schemas for alerts and analytics.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class AlertRuleResponse(BaseModel):
    """Response schema for alert rule."""
    id: UUID = Field(..., description="Alert rule ID")
    name: str = Field(..., description="Alert rule name")
    condition: str = Field(..., description="Condition type")
    threshold: float = Field(..., description="Threshold value")
    window_minutes: int = Field(..., description="Time window in minutes")
    is_active: bool = Field(..., description="Is rule active")
    last_triggered_at: Optional[datetime] = Field(None, description="When last triggered")
    created_at: datetime = Field(..., description="When rule was created")
    
    model_config = ConfigDict(from_attributes=True)


class AlertHistoryResponse(BaseModel):
    """Response schema for alert history."""
    id: UUID = Field(..., description="Alert history ID")
    alert_rule_id: UUID = Field(..., description="Alert rule ID")
    metric_value: float = Field(..., description="Metric value that triggered alert")
    threshold: float = Field(..., description="Threshold")
    message: str = Field(..., description="Alert message")
    created_at: datetime = Field(..., description="When alert was triggered")
    
    model_config = ConfigDict(from_attributes=True)


class WebhookAnalyticsResponse(BaseModel):
    """Response schema for webhook analytics."""
    id: UUID = Field(..., description="Analytics record ID")
    provider_id: UUID = Field(..., description="Provider ID")
    hour: datetime = Field(..., description="Hour this metric is for")
    total_webhooks: int = Field(..., description="Total webhooks")
    successful_webhooks: int = Field(..., description="Successful webhooks")
    failed_webhooks: int = Field(..., description="Failed webhooks")
    pending_webhooks: int = Field(..., description="Pending webhooks")
    success_rate: float = Field(..., description="Success rate percentage")
    avg_latency_ms: float = Field(..., description="Average latency in ms")
    p50_latency_ms: float = Field(..., description="50th percentile latency")
    p95_latency_ms: float = Field(..., description="95th percentile latency")
    p99_latency_ms: float = Field(..., description="99th percentile latency")
    
    model_config = ConfigDict(from_attributes=True)


class SecurityAnalyticsResponse(BaseModel):
    """Response schema for security analytics."""
    id: UUID = Field(..., description="Analytics record ID")
    hour: datetime = Field(..., description="Hour this metric is for")
    invalid_signatures: int = Field(..., description="Invalid signature attempts")
    replay_attempts: int = Field(..., description="Replay attempts")
    rate_limit_violations: int = Field(..., description="Rate limit violations")
    timestamp_errors: int = Field(..., description="Timestamp errors")
    total_security_events: int = Field(..., description="Total security events")
    
    model_config = ConfigDict(from_attributes=True)
