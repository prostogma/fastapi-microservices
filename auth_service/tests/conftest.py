from httpx import AsyncClient, ASGITransport
import pytest
import redis.asyncio as redis
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import TestSettings
from app.db.base import Base
from app.db.session import create_async_session
from app.main import app


test_settings = TestSettings()  # type: ignore


@pytest.fixture(scope="session")
async def test_engine():
    assert "test" in test_settings.DATABASE_URL
    engine = create_async_engine(test_settings.DATABASE_URL, poolclass=NullPool)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture(scope="session")
async def async_session_maker(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False)

@pytest.fixture
async def db_session(async_session_maker):
    async with async_session_maker() as session:
        trans = await session.begin()
        try:
            yield session
        finally:
            await trans.rollback()


@pytest.fixture
async def async_client(db_session):
    async def override_get_session():
        yield db_session
    
    app.dependency_overrides[create_async_session] = override_get_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def redis_client():
    client = redis.from_url("redis://localhost:6380/0", decode_responses=True)
    yield client
    await client.aclose()

@pytest.fixture(autouse=True)
async def ovveride_redis(redis_client):
    app.state.redis = redis_client
    yield
    del app.state.redis

@pytest.fixture
async def clean_redis(redis_client):
    await redis_client.flushdb()


class MockUsersClient:
    async def verified_user_by_id(self, user_id: str):
        class MockResponse:
            id = user_id

        return MockResponse()


@pytest.fixture
async def ovveride_users_client():
    app.state.users_client = MockUsersClient()
    yield
    del app.state.users_client
