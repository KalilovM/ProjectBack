import asyncio
import os

import asyncpg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import settings
from db.session import get_db

test_engine = create_async_engine(
    settings.TEST_DATABASE_URL, future=True, echo=True, poolclass=NullPool
)
test_async_session = async_sessionmaker(
    bind=test_engine, expire_on_commit=False, class_=AsyncSession
)


CLEAN_TABLES = [
    "users",
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def run_migrations():
    os.system("alembic init migrations")
    os.system("alembic revision --autogenerate -m 'running test migrations'")
    os.system("alembic upgrade heads")


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(
        settings.TEST_DATABASE_URL, future=True, echo=True, poolclass=NullPool
    )
    session = async_sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    yield session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    async with async_session_test() as session:
        async with session.begin():
            for table in CLEAN_TABLES:
                await session.execute(text(f"TRUNCATE TABLE {table};"))
            await session.commit()


async def _get_test_db():
    try:
        engine = create_async_engine(
            settings.TEST_DATABASE_URL, future=True, echo=True, poolclass=NullPool
        )
        async_session = async_sessionmaker(
            bind=engine, expire_on_commit=False, class_=AsyncSession
        )
        yield async_session()
    finally:
        pass


@pytest.fixture
async def client():
    from main import app

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app=app) as client:
        yield client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join(settings.TEST_DATABASE_URL.split("+asyncpg"))
    )
    yield pool


@pytest.fixture
async def get_user_from_database(asyncpg_pool):
    async def get_user_from_db_by_uuid(user_id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch(
                "SELECT * FROM users WHERE user_id = $1", user_id
            )

    return get_user_from_db_by_uuid


@pytest.fixture
async def create_user_in_db(asyncpg_pool):
    async def create_user_in_db(
        user_id: str, username: str, email: str, password: str, is_active: bool
    ):
        async with asyncpg_pool.acquire() as connection:
            return await connection.execute(
                """INSERT INTO users VALUES ($1, $2, $3, $4, $5)""",
                user_id,
                username,
                email,
                password,
                is_active,
            )

    return create_user_in_db
