from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "shortener_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "deactivate-expired-links-hourly": {
            "task": "app.worker.tasks.deactivate_expired_links",
            "schedule": 3600.0,
        },
    },
)
