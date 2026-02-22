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
# These imports are done at the end to avoid circular imports
def _import_models():
    """Import all models for Alembic discovery."""
    from app.db.models import provider  # noqa: F401
    from app.db.models import webhook_event  # noqa: F401
    from app.db.models import security_log  # noqa: F401

_import_models()
