"""
Database Engine & Async Session Management for FraudLens AI.
Defaults to local SQLite for zero-setup execution,
and seamlessly switches to PostgreSQL when DATABASE_URL is configured.
"""

import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database.models import Base

logger = logging.getLogger("database_session")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./fraudlens.db")

# Convert standard postgres:// or postgresql:// to asyncpg driver if needed
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# SQLite specific connect args
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initializes tables asynchronously on startup."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database initialized with URL: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

async def get_db():
    """FastAPI dependency for database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
