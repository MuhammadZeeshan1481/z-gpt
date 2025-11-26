import logging
import secrets
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional, Tuple

from fastapi import Request
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

LOGGER = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit_per_minute: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limit_per_minute = limit_per_minute
        self.window_seconds = window_seconds
        self.hits: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        key = f"ip:{client_ip}"

        redis_client: Optional[Redis] = getattr(request.app.state, "redis_client", None)
        if redis_client:
            result = await self._check_redis(redis_client, key)
            if result is not None:
                allowed, retry_after = result
                if allowed:
                    return await call_next(request)
                return self._reject(request, retry_after)

        if not self._allow_in_memory(key):
            return self._reject(request, self.window_seconds)
        return await call_next(request)

    async def _check_redis(self, redis_client: Redis, key: str) -> Optional[Tuple[bool, int]]:
        now_ms = int(time.time() * 1000)
        window_ms = self.window_seconds * 1000
        redis_key = f"zgpt:rl:{key}"
        member = f"{now_ms}-{secrets.token_hex(2)}"
        try:
            pipeline = redis_client.pipeline()
            pipeline.zremrangebyscore(redis_key, 0, now_ms - window_ms)
            pipeline.zadd(redis_key, {member: now_ms})
            pipeline.zcard(redis_key)
            pipeline.expire(redis_key, self.window_seconds)
            _, _, count, _ = await pipeline.execute()
        except Exception as exc:  # pragma: no cover - fallback path
            LOGGER.warning("Redis rate limiter unavailable, falling back to memory: %s", exc)
            return None

        if count > self.limit_per_minute:
            retry_after = self.window_seconds
            try:
                oldest = await redis_client.zrange(redis_key, 0, 0, withscores=True)
            except Exception:
                oldest = []
            if oldest:
                retry_after = max(1, int((oldest[0][1] + window_ms - now_ms) / 1000))
            return False, retry_after
        return True, 0

    def _allow_in_memory(self, key: str) -> bool:
        now = time.time()
        window_start = now - float(self.window_seconds)
        dq = self.hits[key]
        while dq and dq[0] < window_start:
            dq.popleft()
        if len(dq) >= self.limit_per_minute:
            return False
        dq.append(now)
        return True

    def _reject(self, request: Request, retry_after: int) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "rate_limited",
                    "message": "Too many requests, please try again later.",
                },
                "request_id": getattr(request.state, "request_id", None),
            },
            headers={"Retry-After": str(max(retry_after, 1))},
        )
