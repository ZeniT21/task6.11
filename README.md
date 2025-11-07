.env
PROJECT_NAME=Тестовая задача
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PWD=
CACHE_TIMEOUT=100

Запуск проекта:
docker-compose down && docker-compose build --no-cache && docker-compose up