"""
Celery configuration module.
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "app",
    backend=settings.CELERY_RESULT_BACKEND,
    broker=settings.CELERY_BROKER_URL,
    include=['app.services.infrastructure.async_tasks.celery.tasks'],
)

# Use default queue
celery_app.conf.task_default_queue = 'celery'

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
