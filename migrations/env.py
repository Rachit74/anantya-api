# migrations/env.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_engine_from_config
from sqlalchemy import pool
from alembic import context
from app.models.models import Base   # ← your models

load_dotenv()

config = context.config

# Inject DB URL from .env at runtime
config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")
)

target_metadata = Base.metadata    # ← tells Alembic about your tables


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        connect_args={"ssl": "require", "statement_cache_size": 0}
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())