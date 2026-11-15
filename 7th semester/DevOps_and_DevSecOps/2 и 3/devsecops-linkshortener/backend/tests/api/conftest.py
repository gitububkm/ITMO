# ruff: noqa: E402
import asyncio
import sys
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import nest_asyncio
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

nest_asyncio.apply()

from app.core.config import settings
from app.core.security import hash_password
from app.db import cache as cache_module
from app.db.session import get_db_session
from app.main import app
from app.models import User
from app.schemas.role import UserRole

engine_test = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
def event_loop() -> Generator[AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    command.upgrade(config, "head")

    sync_engine = create_sync_engine(settings.SYNC_DATABASE_URL)
    with sync_engine.connect() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(text("TRUNCATE TABLE clicks, links, users RESTART IDENTITY CASCADE;"))
        conn.commit()
    sync_engine.dispose()


@pytest_asyncio.fixture
async def test_redis() -> AsyncGenerator[FakeRedis]:
    client = FakeRedis(decode_responses=True)
    cache_module.set_redis_client_for_tests(client)
    yield client
    await client.flushall()
    await client.aclose()


@pytest_asyncio.fixture
async def db_session(test_redis: FakeRedis) -> AsyncGenerator[AsyncSession]:
    _ = test_redis
    async with async_session_maker() as session:
        await session.execute(text("TRUNCATE TABLE clicks, links, users RESTART IDENTITY CASCADE;"))
        await session.commit()
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, test_redis: FakeRedis) -> AsyncGenerator[AsyncClient]:
    _ = test_redis

    async def override_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(db_session: AsyncSession) -> User:
    user = User(
        name="Test User",
        email="user@example.com",
        hashed_password=hash_password("secret123"),
        role=UserRole.USER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, registered_user: User) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": registered_user.email, "password": "secret123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
