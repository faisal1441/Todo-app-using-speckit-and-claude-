"""
Database configuration for SQLModel and PostgreSQL with Neon DB.

This module handles:
- Database URL configuration from environment variables
- SQLAlchemy engine setup
- Session factory creation
- Database initialization
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from sqlmodel import SQLModel, Session

# Load environment variables from .env file
# Look for .env in the backend directory
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
load_dotenv(env_file)

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost/neondb"
)

print(f"[Config] Loading database configuration from: {env_file}")
print(f"[Config] Database URL: {DATABASE_URL[:50]}..." if len(DATABASE_URL) > 50 else f"[Config] Database URL: {DATABASE_URL}")

# Create async engine for async operations
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
    poolclass=NullPool,  # Don't pool connections (better for serverless/Neon)
    connect_args={
        "timeout": 10,
        "command_timeout": 30,
    }
)

# Note: We use asyncpg throughout. For synchronous operations in routes,
# we'll wrap async calls or use a thread pool if needed.
# For now, routes are kept synchronous but use the async engine via Session


async def async_init_db():
    """
    Asynchronously initialize the database by creating all tables.

    This function creates all tables defined in the SQLModel models.
    It should be called once when the application starts.

    Raises:
        Exception: If database connection or table creation fails
    """
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("[OK] Database tables created successfully")
    except Exception as e:
        print(f"[ERROR] Error creating database tables: {e}")
        raise


def init_db():
    """
    Synchronously initialize the database by creating all tables.

    Wraps async_init_db() for use in non-async contexts.
    """
    asyncio.run(async_init_db())


# Create async session maker
async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    """
    Get an async database session for dependency injection in FastAPI.

    Yields an AsyncSession for use in API endpoints.
    The session is automatically closed after the request.

    Yields:
        AsyncSession: SQLModel async session for database operations

    Example:
        @router.get("/tasks")
        async def get_tasks(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session() as session:
        yield session
