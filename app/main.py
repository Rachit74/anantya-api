"""
Anantya Foundation API - Main Application Entry Point
"""

from fastapi import FastAPI, Response, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.db import engine                        # ← replaces create_db_pool
from app.routes import members, auth
from app.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("DATABASE CONNECTED")
    yield
    await engine.dispose()                       # ← replaces pool.close()
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
    return Response('API UP', status_code=status.HTTP_200_OK)