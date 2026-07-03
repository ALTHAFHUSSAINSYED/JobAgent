import json
import logging
from typing import Any, Dict
import redis.asyncio as aioredis
from app.domain.interfaces import IEventBus
from app.core.config import settings

logger = logging.getLogger("app.infrastructure.redis.event_bus")

class RedisEventBus(IEventBus):
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self._redis = None

    async def get_redis(self) -> aioredis.Redis:
        if not self._redis:
            self._redis = aioredis.from_url(self.redis_url)
        return self._redis

    async def publish(self, event_name: str, payload: Dict[str, Any]) -> None:
        try:
            r = await self.get_redis()
            serialized = json.dumps(payload)
            await r.publish(event_name, serialized)
            logger.info(f"Published event '{event_name}' to Redis channel.")
        except Exception as e:
            logger.error(f"Failed to publish event '{event_name}': {e}")

    async def subscribe(self, event_name: str, handler: Any) -> None:
        try:
            r = await self.get_redis()
            pubsub = r.pubsub()
            await pubsub.subscribe(event_name)
            logger.info(f"Subscribed to Redis event '{event_name}'.")
        except Exception as e:
            logger.error(f"Failed to subscribe to event '{event_name}': {e}")
            
    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None
