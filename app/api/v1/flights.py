from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis

from app.config import settings
from app.core.dependencies import get_redis
from app.schemas import FlightSchema
from app.services.connector.flight import GetFlightData, AviaConverter


router = APIRouter()


@router.post("", response_model=FlightSchema, summary="Получить данные о рейсе")
async def get_flights(
    use_cache: bool = True,
    cache: Redis = Depends(get_redis),
    flight_data: GetFlightData = Depends(),
    converter: AviaConverter = Depends(),
):

    if use_cache:
        cached_data = await cache.get(settings.flight_cache_key)
        if cached_data:
            return FlightSchema.model_validate_json(cached_data)

    raw_data = flight_data.get_flight_data()
    if not raw_data:
        raise HTTPException(status_code=404, detail="Данные о рейсе не найдены")

    data = converter.transform_flight(raw_data)

    await cache.set(settings.flight_cache_key, data.model_dump_json(), settings.cache_timeout)

    return data
