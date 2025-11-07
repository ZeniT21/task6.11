import json

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.config import settings
from app.core.dependencies import get_redis
from app.schemas import FlightSchema
from app.services.connector.flight import Flight


router = APIRouter()


@router.post("", response_model=FlightSchema, summary="Получить данные о рейсе")
async def get_flights(
        use_cache: bool = True,
        redis_client: Redis = Depends(get_redis),
        flight_data: Flight = Depends()
):

    if use_cache:
        cached = await redis_client.get("get_flights")
        if cached:
            return FlightSchema(**json.loads(cached))

    raw_data = flight_data.get_flight()
    data = flight_data.transform_flight(raw_data)

    await redis_client.set("get_flights", data.json(), settings.cache_timeout)

    return data
