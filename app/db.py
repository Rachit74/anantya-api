"""
Database Connection Module

This module handles PostgreSQL database connection pool management
using asyncpg for asynchronous database operations.

The connection pool is configured with:
- Minimum 1 connection (maintained even when idle)
- Maximum 10 connections (limits resource usage)

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (required)
"""

import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


async def create_db_pool():
    """
    Create and return an asyncpg connection pool.

    The pool manages connections to the PostgreSQL database,
    allowing efficient reuse of connections across requests.

    Returns:
        asyncpg.pool.Pool: A connection pool instance

    Raises:
        Exception: If DATABASE_URL is not set or connection fails
    """
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        statement_cache_size=0
    )