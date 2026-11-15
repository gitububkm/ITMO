import pytest
from app.core.config import settings
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_allows_configured_origin(client: AsyncClient) -> None:
    origin = settings.CORS_ORIGINS[0]
    response = await client.get("/health", headers={"Origin": origin})
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_rejects_unknown_origin(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers
