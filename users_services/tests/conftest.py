import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import inspect
from alembic import command
from alembic.config import Config

from app.main import app
from app.core.config import Settings, BASE_DIR
from app.db.session import create_async_session
from app.crud.users import create_user
from app.schemas.user import UserCreateSchema
from app.db.base import Base


test_settings = Settings(_env_file=str(BASE_DIR / ".test.env"))

@pytest.fixture(scope="session")
async def test_engine():
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
async def test_users(db_session):
    users_data = [
        {"email": "alice@example.com", "is_verified": True},
        {"email": "bob@example.com"},
        {"email": "john@example.com", "is_verified": True},
        {"email": "ahmed@example.com", "is_active": False},
    ]

    users = []

    for udata in users_data:
        user = await create_user(
            user_data=UserCreateSchema(**udata), session=db_session
        )
        users.append(user)

    yield users
