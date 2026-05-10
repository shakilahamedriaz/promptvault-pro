import time
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request, status

from app.redis_client import get_redis


async def rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
    redis,
) -> None:
    if redis is None:
        return  # Redis unavailable — skip rate limiting

    now = time.time()
    window_start = now - window_seconds

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, "-inf", window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds + 1)
    results = await pipe.execute()

    current_count: int = results[2]
    if current_count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {limit} requests per {window_seconds}s.",
            headers={"Retry-After": str(window_seconds)},
        )


def make_rate_limit_dependency(limit: int, window_seconds: int) -> Callable:
    async def dependency(
        request: Request,
        redis: Optional[object] = Depends(get_redis),
    ) -> None:
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            bucket = f"rl:{limit}:{window_seconds}:user:{user_id}"
        else:
            client_ip = request.client.host if request.client else "unknown"
            bucket = f"rl:{limit}:{window_seconds}:ip:{client_ip}"

        await rate_limit(bucket, limit, window_seconds, redis)

    return dependency


api_rate_limit = make_rate_limit_dependency(limit=100, window_seconds=60)
ai_rate_limit = make_rate_limit_dependency(limit=20, window_seconds=60)
