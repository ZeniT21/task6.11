from redis.asyncio import Redis
from app.core.redis import redis_client


async def get_redis() -> Redis:
    if not redis_client.redis:
        await redis_client.connect()
    return redis_client.get_client()
