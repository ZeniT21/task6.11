from redis.asyncio import Redis
from app.config import settings


class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            encoding="utf-8",
            decode_responses=True
        )
        await self.redis.ping()

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    def get_client(self) -> Redis:
        if not self.redis:
            raise RuntimeError("Redis client is not connected")
        return self.redis


redis_client = RedisClient()
