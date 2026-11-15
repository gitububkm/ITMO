from http import HTTPStatus

import jwt
import pytest
from app.models import User
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_me(client: AsyncClient) -> None:
    register = await client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )
    assert register.status_code == HTTPStatus.CREATED
    assert register.json()["email"] == "alice@example.com"

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "alice@example.com", "password": "secret123"},
    )
    assert login.status_code == HTTPStatus.OK
    token = login.json()["access_token"]

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == HTTPStatus.OK
    assert me.json()["name"] == "Alice"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {"name": "Bob", "email": "bob@example.com", "password": "secret123"}
    first = await client.post("/api/v1/auth/register", json=payload)
    second = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == HTTPStatus.CREATED
    assert second.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Carol", "email": "carol@example.com", "password": "secret123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "carol@example.com", "password": "bad"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("key", "algorithm"),
    [("attacker-controlled-secret-key-32b!", "HS256"), (None, "none")],
    ids=["wrong-signature", "unsigned"],
)
async def test_forged_token_is_rejected(
    client: AsyncClient,
    registered_user: User,
    key: str | None,
    algorithm: str,
) -> None:
    forged = jwt.encode({"sub": str(registered_user.id)}, key, algorithm=algorithm)
    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
