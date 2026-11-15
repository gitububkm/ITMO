import structlog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.cache import link_cache_key
from app.services.click_tasks import deactivate_expired_links_sync, record_click_sync
from app.worker.celery_app import celery_app

logger = structlog.get_logger()

sync_engine = create_engine(settings.SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task(name="app.worker.tasks.record_click")
def record_click(
    link_id: str,
    referer: str | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> dict:
    with SyncSession() as session:
        record_click_sync(
            session,
            link_id=link_id,
            referer=referer,
            user_agent=user_agent,
            ip_address=ip_address,
        )
    logger.info("click_recorded", link_id=link_id)
    return {"status": "ok", "link_id": link_id}


@celery_app.task(name="app.worker.tasks.deactivate_expired_links")
def deactivate_expired_links() -> dict:
    with SyncSession() as session:
        count = deactivate_expired_links_sync(session)
    logger.info("expired_links_deactivated", count=count)
    return {"deactivated": count, "cache_hint": link_cache_key("*")}
