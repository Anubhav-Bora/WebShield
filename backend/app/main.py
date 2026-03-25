"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings, setup_logging
from app.db.session import engine, get_db
from app.core.error_handler import global_exception_handler, validation_exception_handler
from app.core.security_headers import SecurityHeadersMiddleware
from app.api.routes.webhook import router as webhooks_router
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.webhooks_advanced import router as webhooks_advanced_router
from app.api.routes.websocket import router as websocket_router

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

# Add global exception handlers
from fastapi.exceptions import RequestValidationError
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

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

# Include auth routes
app.include_router(
    auth_router,
    tags=["Authentication"]
)

# Include analytics routes
app.include_router(
    analytics_router,
    prefix="/admin",
    tags=["Analytics"]
)

# Include webhooks advanced routes
app.include_router(
    webhooks_advanced_router,
    prefix="/admin",
    tags=["Webhooks Advanced"]
)

# Include websocket routes
app.include_router(
    websocket_router,
    tags=["WebSocket"]
)

# Convenience endpoints for login/signup at root level
from app.schemas.user import UserCreate, LoginRequest, Token
from app.core.auth import verify_password, get_password_hash, create_access_token
from app.db.models.user import User
from sqlalchemy import select
from datetime import timedelta

@app.post("/login", response_model=Token, tags=["Authentication"])
async def root_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint at root level (convenience alias for /auth/login).
    
    Accepts email or username with password.
    Returns JWT access token.
    """
    # DEBUG: Log received credentials
    logger.info(f"Login attempt for username: '{login_data.username}'")
    logger.info(f"Password received: {len(login_data.password)} characters")
    logger.info(f"Password value: '{login_data.password}'")
    logger.info(f"Password bytes: {login_data.password.encode()}")
    
    # Find user by username or email
    result = await db.execute(
        select(User).where(
            (User.username == login_data.username) | (User.email == login_data.username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"User '{login_data.username}' not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"User found: {user.username}")
    
    # Verify password
    is_password_valid = verify_password(login_data.password, user.hashed_password)
    logger.info(f"Password valid: {is_password_valid}")
    
    if not is_password_valid:
        logger.warning(f"Invalid password for user '{login_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Login successful for user: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def root_signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Signup endpoint at root level (convenience alias for /auth/register).
    
    - **email**: Valid email address
    - **username**: Unique username (3-100 characters)
    - **full_name**: User's full name
    - **password**: Password (min 8 characters)
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "username": new_user.username,
        "full_name": new_user.full_name,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at.isoformat()
    }

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
