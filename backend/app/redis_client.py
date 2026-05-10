from typing import Optional

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

_redis_client: Optional[aioredis.Redis] = None


def get_redis_client() -> Optional[aioredis.Redis]:
    global _redis_client
    if not settings.REDIS_URL:
        return None
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def get_redis() -> Optional[aioredis.Redis]:
    return get_redis_client()


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
