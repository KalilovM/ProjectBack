import os


env = os.environ

REAL_DATABASE_URL = env.get(
    "REAL_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres"
)

TEST_DATABASE_URL = env.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres_test:postgres_test@0.0.0.0:5433/postgres_test",
)
