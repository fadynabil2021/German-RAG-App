from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from core.container import container

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware.
    Shared across workers and scalable.
    """
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute

    async def dispatch(self, request: Request, call_next):
        # We try to get the redis client from our container
        redis_client = container.redis_client
        
        if redis_client:
            try:
                # Basic connectivity check
                await redis_client.ping()
            except Exception:
                logger.error("Redis is down - bypassing rate limit")
                redis_client = None

        if not redis_client:
            # Fallback for local dev or if redis is down
            return await call_next(request)

        client_ip = request.client.host
        # Use a sliding window with Redis or a simple counter per minute
        key = f"rate_limit:{client_ip}:{int(time.time() / 60)}"
        
        try:
            current_usage = await redis_client.get(key)
            if current_usage and int(current_usage) >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later."
                )
            
            # Increment and set expiry
            pipeline = redis_client.pipeline()
            pipeline.incr(key)
            pipeline.expire(key, 60)
            await pipeline.execute()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis Rate Limit error: {e}")
            # Fail open in case of Redis failure to not block API
            return await call_next(request)
            
        response = await call_next(request)
        return response

import time # For the key generation
