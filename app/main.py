from fastapi import FastAPI, Request

from app.api.v1 import flights
from app.config import Settings
from app.logging_config import logger
from app.core.redis import redis_client


settings = Settings()

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json"
)


@app.on_event("startup")
async def startup_event():
    await redis_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.disconnect()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error handling request {request.method} {request.url}: {e}", exc_info=True)
        raise
    logger.info(f"Completed request: {request.method} {request.url} "
                f"Status code: {response.status_code}")
    return response


app.include_router(flights.router, prefix="/api/v1/flights", tags=["flights"])
