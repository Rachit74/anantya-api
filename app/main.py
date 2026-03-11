"""
Anantya Foundation API - Main Application Entry Point

This module initializes the FastAPI application for the Anantya Foundation
volunteer management system. It handles:
- Database connection pool lifecycle management
- CORS middleware configuration
- API router registration

The application manages member onboarding, unique ID generation,
and welcome email communication for volunteers.
"""

from fastapi import FastAPI, Response, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.db import create_db_pool
from app.routes import members, auth
from app.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifespan for database connection pool.

    Creates a PostgreSQL connection pool on startup and ensures
    proper cleanup on shutdown.

    Args:
        app: The FastAPI application instance

    Yields:
        None during application runtime

    Raises:
        Exception: If database connection fails during startup
    """
    try:
        app.state.pool = await create_db_pool()
        print("DATABASE CONNECTED")
        yield
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise
    finally:
        if hasattr(app.state, 'pool'):
            await app.state.pool.close()
            print("DB CONNECTION CLOSED")

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(members.router)
app.include_router(auth.router)

@app.get('/')
def home():
    """
    Health check endpoint.

    Returns:
        Response: Plain text 'API UP' with 200 status code
    """
    return Response('API UP', status_code=status.HTTP_200_OK)