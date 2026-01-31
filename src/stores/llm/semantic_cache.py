import json
import hashlib
from typing import Optional, Any
import redis
import logging

logger = logging.getLogger(__name__)

class SemanticCache:
    """
    Redis-based cache for LLM responses.
    Initial implementation uses exact prompt matching (hashing).
    Can be expanded to use vector similarity search (RedisVL).
    """
    def __init__(self, redis_url: str, ttl: int = 3600):
        self.redis_client = redis.from_url(redis_url)
        self.ttl = ttl

    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Create a unique key for the prompt and model."""
        content = f"{model}:{prompt}".encode('utf-8')
        return f"llm_cache:{hashlib.sha256(content).hexdigest()}"

    def get_cached_response(self, prompt: str, model: str) -> Optional[str]:
        """Retrieve cached response if it exists."""
        try:
            key = self._get_cache_key(prompt, model)
            cached_data = self.redis_client.get(key)
            if cached_data:
                logger.info("Cache hit for LLM query")
                return cached_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error accessing LLM cache: {e}")
        return None

    def set_cached_response(self, prompt: str, model: str, response: str):
        """Store response in cache with TTL."""
        try:
            key = self._get_cache_key(prompt, model)
            self.redis_client.setex(key, self.ttl, response)
        except Exception as e:
            logger.error(f"Error setting LLM cache: {e}")
