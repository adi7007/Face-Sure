"""Legacy seed hook with no automatic demo data."""

from sqlalchemy.ext.asyncio import AsyncSession


async def seed_database(db: AsyncSession) -> None:
    """Retained for old scripts; deliberately writes no demo data."""
    del db
