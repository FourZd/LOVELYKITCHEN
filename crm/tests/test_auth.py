import pytest
from httpx import AsyncClient
import jwt
from core.environment.config import Settings


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
            "name": "Test User",
            "organization_name": "Test Org",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    user_data = {
        "email": "duplicate@example.com",
        "password": "TestPassword123",
        "name": "Test User",
        "organization_name": "Test Org",
    }
    
    response1 = await client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 200
    
    response2 = await client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "TestPassword123",
            "name": "Login User",
            "organization_name": "Login Org",
        },
    )
    
    register_data = register_response.json()
    org_id = register_data["data"]["access_token"]
    
    settings = Settings()
    decoded = jwt.decode(org_id, settings.secret_key, algorithms=[settings.jwt_algorithm])
    organization_id = decoded["organization_id"]
    
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "TestPassword123"},
        headers={"X-Organization-Id": organization_id},
    )
    
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "data" in login_data
    assert "access_token" in login_data["data"]

