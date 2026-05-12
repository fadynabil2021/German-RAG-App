import time
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import structlog
from core.container import container
from redis.asyncio import Redis

logger = structlog.get_logger(__name__)

LIMITS = {
    "free": int(container.settings.RATE_LIMIT_PER_MINUTE_FREE),
    "pro": int(container.settings.RATE_LIMIT_PER_MINUTE_PRO)
}

async def check_rate(user_id: str, tier: str, redis_client: Redis):
    """
    Per-user rate limiting logic as per PRD 5.7.
    Called as a dependency or within specific routes.
    """
    key = f"rl:{user_id}:{int(time.time())//60}"
    try:
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 65)
        
        limit = LIMITS.get(tier, LIMITS["free"])
        if count > limit:
            logger.warning("Rate limit exceeded", user_id=user_id, tier=tier)
            return False
        return True
    except Exception as e:
        logger.error("Redis Rate Limit error", error=str(e))
        # Fail open
        return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Fallback IP-based rate limiting middleware for non-authenticated routes.
    """
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for static files or documentation if needed
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return await call_next(request)

        redis_client = container.redis_client
        client_ip = request.client.host
        key = f"rl:ip:{client_ip}:{int(time.time() / 60)}"
        
        try:
            count = await redis_client.incr(key)
            if count == 1:
                await redis_client.expire(key, 65)
            
            if count > self.requests_per_minute:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Too many requests. Please try again later."}
                )
        except Exception as e:
            logger.error("IP Rate Limit error", error=str(e))
            
        return await call_next(request)
