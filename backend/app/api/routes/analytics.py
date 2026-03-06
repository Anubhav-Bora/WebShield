"""
Analytics and monitoring routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta
from uuid import UUID

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.alert_rule import AlertRule, AlertHistory
from app.db.models.analytics import WebhookAnalytics, SecurityAnalytics
from app.core.auth import get_current_active_user
from app.schemas.alert import (
    AlertRuleResponse,
    AlertHistoryResponse,
    WebhookAnalyticsResponse,
    SecurityAnalyticsResponse
)

router = APIRouter()


# Alert Rules Endpoints
@router.get("/alert-rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all alert rules for current user. Requires authentication."""
    stmt = select(AlertRule).where(
        AlertRule.user_id == current_user.id
    ).order_by(AlertRule.created_at.desc())
    
    result = await db.execute(stmt)
    rules = result.scalars().all()
    
    return [AlertRuleResponse.from_orm(r) for r in rules]


@router.get("/alert-history", response_model=List[AlertHistoryResponse])
async def get_alert_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alert history for current user. Requires authentication."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    stmt = select(AlertHistory).where(
        AlertHistory.created_at >= cutoff_date
    ).order_by(
        AlertHistory.created_at.desc()
    ).limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    history = result.scalars().all()
    
    return [AlertHistoryResponse.from_orm(h) for h in history]


# Analytics Endpoints
@router.get("/analytics/webhooks", response_model=List[WebhookAnalyticsResponse])
async def get_webhook_analytics(
    provider_id: UUID = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get webhook analytics. Requires authentication."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    stmt = select(WebhookAnalytics).where(
        WebhookAnalytics.hour >= cutoff_date
    )
    
    if provider_id:
        stmt = stmt.where(WebhookAnalytics.provider_id == provider_id)
    
    stmt = stmt.order_by(WebhookAnalytics.hour.desc())
    
    result = await db.execute(stmt)
    analytics = result.scalars().all()
    
    return [WebhookAnalyticsResponse.from_orm(a) for a in analytics]


@router.get("/analytics/security", response_model=List[SecurityAnalyticsResponse])
async def get_security_analytics(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get security analytics. Requires authentication."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    stmt = select(SecurityAnalytics).where(
        SecurityAnalytics.hour >= cutoff_date
    ).order_by(SecurityAnalytics.hour.desc())
    
    result = await db.execute(stmt)
    analytics = result.scalars().all()
    
    return [SecurityAnalyticsResponse.from_orm(a) for a in analytics]


@router.get("/analytics/summary")
async def get_analytics_summary(
    provider_id: UUID = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get analytics summary. Requires authentication."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    stmt = select(WebhookAnalytics).where(
        WebhookAnalytics.hour >= cutoff_date
    )
    
    if provider_id:
        stmt = stmt.where(WebhookAnalytics.provider_id == provider_id)
    
    result = await db.execute(stmt)
    analytics = result.scalars().all()
    
    if not analytics:
        return {
            "total_webhooks": 0,
            "total_successful": 0,
            "total_failed": 0,
            "avg_success_rate": 0.0,
            "avg_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "p99_latency_ms": 0.0
        }
    
    total_webhooks = sum(a.total_webhooks for a in analytics)
    total_successful = sum(a.successful_webhooks for a in analytics)
    total_failed = sum(a.failed_webhooks for a in analytics)
    avg_success_rate = sum(a.success_rate for a in analytics) / len(analytics)
    avg_latency = sum(a.avg_latency_ms for a in analytics) / len(analytics)
    p95_latency = sum(a.p95_latency_ms for a in analytics) / len(analytics)
    p99_latency = sum(a.p99_latency_ms for a in analytics) / len(analytics)
    
    return {
        "total_webhooks": total_webhooks,
        "total_successful": total_successful,
        "total_failed": total_failed,
        "avg_success_rate": avg_success_rate,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
        "p99_latency_ms": p99_latency
    }
