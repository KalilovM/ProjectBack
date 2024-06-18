from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import settings

from typing import Generator


engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
