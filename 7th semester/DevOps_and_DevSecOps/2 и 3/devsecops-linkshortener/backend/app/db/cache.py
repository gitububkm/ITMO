from typing import Any

import redis.asyncio as redis
import structlog
from app.core.config import settings

logger = structlog.get_logger()

_redis_pool: redis.Redis | None = None


async def init_redis_pool() -> None:
    global _redis_pool  # noqa: PLW0603
    _redis_pool = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )
    await _redis_pool.ping()
    logger.info("redis_connected", host=settings.REDIS_HOST, port=settings.REDIS_PORT)


async def close_redis_pool() -> None:
    global _redis_pool  # noqa: PLW0603
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None


def get_redis_client() -> redis.Redis:
    if _redis_pool is None:
        msg = "Redis pool is not initialized"
        raise RuntimeError(msg)
    return _redis_pool


async def cache_get(key: str) -> str | None:
    return await get_redis_client().get(key)


async def cache_set(key: str, value: str, ttl: int | None = None) -> None:
    client = get_redis_client()
    if ttl is None:
        ttl = settings.LINK_CACHE_TTL_SECONDS
    await client.set(key, value, ex=ttl)


async def cache_delete(key: str) -> None:
    await get_redis_client().delete(key)


async def store_refresh_token(user_id: str, token: str, ttl_seconds: int) -> None:
    await get_redis_client().set(f"refresh:{token}", user_id, ex=ttl_seconds)


async def get_refresh_token_user(token: str) -> str | None:
    return await get_redis_client().get(f"refresh:{token}")


async def revoke_refresh_token(token: str) -> None:
    await get_redis_client().delete(f"refresh:{token}")


def link_cache_key(short_code: str) -> str:
    return f"link:{short_code}"


# Used by tests to inject FakeRedis
def set_redis_client_for_tests(client: Any) -> None:
    global _redis_pool  # noqa: PLW0603
    _redis_pool = client
