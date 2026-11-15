from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_list_and_stats(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/links",
        headers=auth_headers,
        json={"original_url": "https://example.com/docs", "title": "Docs", "custom_code": "docs01"},
    )
    assert create.status_code == HTTPStatus.CREATED
    body = create.json()
    assert body["short_code"] == "docs01"
    link_id = body["id"]

    listing = await client.get("/api/v1/links", headers=auth_headers)
    assert listing.status_code == HTTPStatus.OK
    assert len(listing.json()) == 1

    stats = await client.get(f"/api/v1/links/{link_id}/stats", headers=auth_headers)
    assert stats.status_code == HTTPStatus.OK
    assert stats.json()["click_count"] == 0


@pytest.mark.asyncio
async def test_redirect_enqueues_click(
    client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create = await client.post(
        "/api/v1/links",
        headers=auth_headers,
        json={"original_url": "https://example.com/path", "custom_code": "go1234"},
    )
    assert create.status_code == HTTPStatus.CREATED

    mock_delay = MagicMock()
    monkeypatch.setattr("app.api.v1.links.record_click.delay", mock_delay)

    response = await client.get("/r/go1234", follow_redirects=False)
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["location"] == "https://example.com/path"
    mock_delay.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_link(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/links",
        headers=auth_headers,
        json={"original_url": "https://example.com/x", "custom_code": "dead01"},
    )
    link_id = create.json()["id"]

    deleted = await client.delete(f"/api/v1/links/{link_id}", headers=auth_headers)
    assert deleted.status_code == HTTPStatus.OK
    assert deleted.json()["is_active"] is False

    response = await client.get("/r/dead01", follow_redirects=False)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "ok"
