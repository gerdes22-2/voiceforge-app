from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://") \
    if settings.DATABASE_URL.startswith("postgresql://") and not settings.DATABASE_URL.startswith("postgresql+asyncpg://") \
    else settings.DATABASE_URL

logger.info(f"Final DATABASE_URL: {db_url}")

engine = create_async_engine(
    db_url,
    pool_pre_ping=True,
    echo=False,
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session_maker() as session:
        yield session
