import pytest
from httpx import AsyncClient
import jwt
from core.environment.config import Settings


async def create_test_user_and_org(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"contact_test_{id(client)}@example.com",
            "password": "TestPassword123",
            "name": "Contact Test User",
            "organization_name": "Contact Test Org",
        },
    )
    
    data = response.json()
    access_token = data["data"]["access_token"]
    
    settings = Settings()
    decoded = jwt.decode(access_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    
    return access_token, decoded["organization_id"]


@pytest.mark.asyncio
async def test_create_contact(client: AsyncClient):
    access_token, org_id = await create_test_user_and_org(client)
    
    response = await client.post(
        "/api/v1/contacts",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+123456789",
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "John Doe"
    assert data["data"]["email"] == "john@example.com"


@pytest.mark.asyncio
async def test_list_contacts(client: AsyncClient):
    access_token, org_id = await create_test_user_and_org(client)
    
    await client.post(
        "/api/v1/contacts",
        json={"name": "Contact 1", "email": "c1@example.com"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    await client.post(
        "/api/v1/contacts",
        json={"name": "Contact 2", "email": "c2@example.com"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    response = await client.get(
        "/api/v1/contacts",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 2
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_cannot_delete_contact_with_deals(client: AsyncClient):
    access_token, org_id = await create_test_user_and_org(client)
    
    contact_response = await client.post(
        "/api/v1/contacts",
        json={"name": "Contact with Deal", "email": "contact@example.com"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    contact_id = contact_response.json()["data"]["id"]
    
    await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Test Deal",
            "amount": 1000,
            "currency": "USD",
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    delete_response = await client.delete(
        f"/api/v1/contacts/{contact_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert delete_response.status_code == 409

