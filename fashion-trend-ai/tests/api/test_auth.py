import pytest
from httpx import AsyncClient
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "newuser@test.com",
        "password": "securepass123",
        "role": "boutique_owner",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert "password_hash" not in data
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, basic_user):
    response = await client.post("/api/v1/auth/register", json={
        "name": "Duplicate",
        "email": "basic@test.com",
        "password": "securepass123",
        "role": "boutique_owner",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_role(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "name": "Bad Role",
        "email": "badrole@test.com",
        "password": "securepass123",
        "role": "hacker",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "name": "Weak",
        "email": "weak@test.com",
        "password": "123",
        "role": "boutique_owner",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, basic_user):
    response = await client.post("/api/v1/auth/login", json={
        "email": "basic@test.com",
        "password": "password123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, basic_user):
    response = await client.post("/api/v1/auth/login", json={
        "email": "basic@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "nobody@test.com",
        "password": "password123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, basic_user, basic_token):
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers(basic_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "basic@test.com"
    assert data["name"] == "Basic User"


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, basic_user):
    # Login first
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "basic@test.com",
        "password": "password123",
    })
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client: AsyncClient, basic_token):
    """Access tokens should not work as refresh tokens."""
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": basic_token,
    })
    assert response.status_code == 401
