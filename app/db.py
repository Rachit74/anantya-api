import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# asyncpg requires postgresql+asyncpg:// scheme
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=10,          # your previous max_size=10
    pool_pre_ping=True,    # handles Neon's auto-suspend/reconnect
    connect_args={
        "statement_cache_size": 0,  # your existing setting, kept
        "ssl": "require"
    }
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # prevents lazy-load errors after commit
)

Base = declarative_base()

# FastAPI dependency — inject this into your routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session