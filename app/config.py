import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    project_name: str = os.getenv("PROJECT_NAME")

    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: str = os.getenv("REDIS_PORT")
    redis_db: str = os.getenv("REDIS_DB")
    redis_password: str = os.getenv("REDIS_PWD")
    cache_timeout: int = os.getenv("CACHE_TIMEOUT")
    flight_cache_key: str = os.getenv("FLIGHT_CACHE_KEY")


settings = Settings()
