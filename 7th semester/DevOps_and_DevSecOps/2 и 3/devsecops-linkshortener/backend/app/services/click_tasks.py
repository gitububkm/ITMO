import hashlib
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Click, Link


def record_click_sync(
    session: Session,
    *,
    link_id: str,
    referer: str | None,
    user_agent: str | None,
    ip_address: str | None,
) -> None:
    link = session.get(Link, uuid.UUID(link_id))
    if link is None or not link.is_active:
        return

    ip_hash = None
    if ip_address:
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()

    click = Click(
        link_id=link.id,
        clicked_at=datetime.now(UTC),
        referer=(referer or "")[:512] or None,
        user_agent=(user_agent or "")[:512] or None,
        ip_hash=ip_hash,
    )
    link.click_count += 1
    session.add(click)
    session.commit()


def deactivate_expired_links_sync(session: Session) -> int:
    now = datetime.now(UTC)
    links = session.scalars(
        select(Link).where(Link.is_active.is_(True), Link.expires_at.is_not(None), Link.expires_at <= now),
    ).all()
    count = 0
    for link in links:
        link.is_active = False
        count += 1
    session.commit()
    return count
