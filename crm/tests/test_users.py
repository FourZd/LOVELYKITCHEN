import pytest
from httpx import AsyncClient
import jwt
from core.environment.config import Settings


async def create_test_user(client: AsyncClient, email_suffix: str):
    """Вспомогательная функция для создания пользователя"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"user_test_{email_suffix}@example.com",
            "password": "TestPassword123",
            "name": f"Test User {email_suffix}",
            "organization_name": f"Test Org {email_suffix}",
        },
    )
    
    data = response.json()
    access_token = data["data"]["access_token"]
    
    settings = Settings()
    decoded = jwt.decode(access_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    
    return access_token, decoded["organization_id"], decoded["id"], decoded["email"]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Тест получения информации о текущем пользователе"""
    access_token, org_id, user_id, email = await create_test_user(client, "me")
    
    response = await client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == user_id
    assert data["data"]["email"] == email
    assert "name" in data["data"]
    assert "created_at" in data["data"]
    # Проверяем, что пароль не возвращается
    assert "password" not in data["data"]
    assert "hashed_password" not in data["data"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Тест: неавторизованный запрос должен вернуть 401"""
    response = await client.get("/api/v1/users/me")
    
    assert response.status_code == 401

