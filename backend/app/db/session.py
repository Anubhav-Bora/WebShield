"""
Database session configuration.

Creates async SQLAlchemy engine and session factory.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings


# Create async engine
# echo=True will log all SQL queries (useful for debugging)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True in development to see SQL queries
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Number of connections to keep in pool
    max_overflow=20,  # Additional connections if pool is exhausted
)

# Session factory
# This creates new sessions for each request
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """
    Dependency function that provides a database session.
    
    Usage in FastAPI routes:
        @app.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            # Use db here
    
    The session is automatically:
    - Created at the start of the request
    - Committed if no errors occur
    - Rolled back if an exception is raised
    - Closed after the request completes
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
