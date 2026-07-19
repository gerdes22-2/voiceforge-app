import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.core.config import settings

async def create_tables():
    engine = create_async_engine(settings.async_database_url)
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
