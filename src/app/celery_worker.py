from celery import Celery
from src.app.core.config import settings


celery_app = Celery(
    "barbershop_celery_app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.app.tasks"]
)

celery_app.conf.update(
    timezone="UTC"
)
