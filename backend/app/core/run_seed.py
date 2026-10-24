import asyncio
from app.core.database import init_engine, get_session
from app.core.seed import seed_database

async def main():
    init_engine()
    async for session in get_session():
        await seed_database(session)

if __name__ == "__main__":
    asyncio.run(main())
