import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from main import app
from core.database.database import BaseModel
from core.environment.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    settings = Settings()
    database_url = (
        f"{settings.database_dialect}+asyncpg://{settings.postgres_user}:"
        f"{settings.postgres_password}@{settings.postgres_hostname}:"
        f"{settings.postgres_port}/{settings.postgres_db}_test"
    )
    
    engine = create_async_engine(database_url, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

