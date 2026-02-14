"""
Database base class and model registry.

This file serves two purposes:
1. Provides the DeclarativeBase that all models inherit from
2. Imports all models so Alembic can discover them for migrations
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Import all models here so Alembic can discover them
# We'll add these imports as we create the models
from app.db.models.provider import Provider  # noqa: E402, F401
from app.db.models.webhook_event import WebhookEvent  # noqa: E402, F401
from app.db.models.security_log import SecurityLog  # noqa: E402, F401
