"""
Async database engine and session management.

Uses SQLAlchemy 2.0 async engine with asyncpg driver for PostgreSQL.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# Engine and session factory will be initialized at startup
_engine = None
_async_session_factory = None


def init_engine() -> None:
    """
    Initialize the async database engine and session factory.

    Should be called once during application startup.
    """
    global _engine, _async_session_factory

    settings = get_settings()

    _engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )

    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncSession:
    """
    FastAPI dependency that provides an async database session.

    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...

    Yields:
        AsyncSession: An async SQLAlchemy session that auto-commits on success
        and auto-rolls-back on exception.
    """
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_engine() first.")

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_engine() -> None:
    """
    Close the database engine and release all connections.

    Should be called during application shutdown.
    """
    global _engine, _async_session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
