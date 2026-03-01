"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import logging

from app.core.config import settings, setup_logging
from app.db.session import engine
from app.api.routes.webhook import router as webhooks_router
from app.api.routes.admin import router as admin_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

redis_client: redis.Redis = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Runs when the application starts and stops.
    """
    # Startup
    logger.info("🚀 Starting Webhook Gateway...")
    
    # Initialize Redis connection
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("✓ Redis connected successfully")
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {e}")
        raise
    
    # Test database connection
    try:
        async with engine.begin() as conn:
            logger.info("✓ Database connected successfully")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise
    
    logger.info("✅ Webhook Gateway is ready!")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🔴 Shutting down Webhook Gateway...")
    
    # Close Redis connection
    try:
        await redis_client.close()
        logger.info("✓ Redis connection closed")
    except Exception as e:
        logger.error(f"✗ Error closing Redis: {e}")
    
    # Close database connections
    try:
        await engine.dispose()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Error closing database: {e}")


# Create FastAPI app
app = FastAPI(
    title="Secure Webhook Gateway",
    description="Production-grade webhook gateway with HMAC verification, rate limiting, and replay protection",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook routes
app.include_router(
    webhooks_router,
    prefix="/webhooks",
    tags=["Webhooks"]
)

# Include admin routes
app.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"]
)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "webhook-gateway",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Secure Webhook Gateway API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
