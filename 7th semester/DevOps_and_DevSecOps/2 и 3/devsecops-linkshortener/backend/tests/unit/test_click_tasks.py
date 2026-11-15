from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

from app.services.click_tasks import deactivate_expired_links_sync, record_click_sync


def test_record_click_sync_increments_counter() -> None:
    link = MagicMock()
    link.id = uuid4()
    link.is_active = True
    link.click_count = 0

    session = MagicMock()
    session.get.return_value = link

    record_click_sync(
        session,
        link_id=str(link.id),
        referer="https://ref.example",
        user_agent="pytest",
        ip_address="127.0.0.1",
    )

    assert link.click_count == 1
    session.add.assert_called_once()
    session.commit.assert_called_once()


def test_deactivate_expired_links_sync() -> None:
    expired = MagicMock()
    expired.is_active = True
    expired.expires_at = datetime.now(UTC) - timedelta(hours=1)

    session = MagicMock()
    session.scalars.return_value.all.return_value = [expired]

    count = deactivate_expired_links_sync(session)
    assert count == 1
    assert expired.is_active is False
    session.commit.assert_called_once()
