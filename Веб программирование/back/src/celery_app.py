import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_shutdown


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379") + "/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379") + "/2")
CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "Europe/Moscow")


def _setup_logger() -> logging.Logger:
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("notifications")
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers if reloaded
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        handler = RotatingFileHandler(logs_dir / "notifications.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = _setup_logger()

celery_app = Celery(
    "news_notifications",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "src.tasks.notifications",
    ],
)

# General celery config
celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    timezone=CELERY_TIMEZONE,
    enable_utc=False,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

# Beat schedule: every Sunday at 09:00 send weekly digest
celery_app.conf.beat_schedule = {
    "weekly-digest": {
        "task": "src.tasks.notifications.send_weekly_digest",
        "schedule": crontab(hour=9, minute=0, day_of_week="sun"),
    }
}


@celery_app.on_after_finalize.connect
def _announce(sender, **kwargs):
    logger.info("Celery app finalized. Tasks: %s", list(sender.tasks.keys()))


@worker_shutdown.connect
def _graceful_shutdown(sig=None, how=None, exitcode=None, **kwargs):
    # Ensure log handlers are flushed on shutdown
    for h in list(logger.handlers):
        try:
            h.flush()
        except Exception:
            pass
        try:
            h.close()
        except Exception:
            pass


