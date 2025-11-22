import pytest
from httpx import AsyncClient
import jwt
from decimal import Decimal
from core.environment.config import Settings


async def create_test_user_and_contact(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"deal_test_{id(client)}@example.com",
            "password": "TestPassword123",
            "name": "Deal Test User",
            "organization_name": "Deal Test Org",
        },
    )
    
    data = response.json()
    access_token = data["data"]["access_token"]
    
    settings = Settings()
    decoded = jwt.decode(access_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    org_id = decoded["organization_id"]
    
    contact_response = await client.post(
        "/api/v1/contacts",
        json={"name": "Test Contact", "email": "contact@example.com"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    contact_id = contact_response.json()["data"]["id"]
    
    return access_token, org_id, contact_id


@pytest.mark.asyncio
async def test_create_deal(client: AsyncClient):
    access_token, org_id, contact_id = await create_test_user_and_contact(client)
    
    response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Website Redesign",
            "amount": 10000.0,
            "currency": "USD",
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "Website Redesign"
    assert float(data["data"]["amount"]) == 10000.0
    assert data["data"]["status"] == "new"


@pytest.mark.asyncio
async def test_update_deal_status_to_won_with_zero_amount_fails(client: AsyncClient):
    access_token, org_id, contact_id = await create_test_user_and_contact(client)
    
    create_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Test Deal",
            "amount": 0,
            "currency": "USD",
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    deal_id = create_response.json()["data"]["id"]
    
    update_response = await client.patch(
        f"/api/v1/deals/{deal_id}",
        json={"status": "won"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert update_response.status_code == 400


@pytest.mark.asyncio
async def test_update_deal_creates_activity(client: AsyncClient):
    access_token, org_id, contact_id = await create_test_user_and_contact(client)
    
    create_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Test Deal",
            "amount": 5000,
            "currency": "USD",
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    deal_id = create_response.json()["data"]["id"]
    
    await client.patch(
        f"/api/v1/deals/{deal_id}",
        json={"status": "in_progress"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    activities_response = await client.get(
        f"/api/v1/deals/{deal_id}/activities",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert activities_response.status_code == 200
    activities = activities_response.json()["data"]
    assert len(activities) > 0
    assert any(a["type"] == "status_changed" for a in activities)

