import pytest
from httpx import AsyncClient
import jwt
from core.environment.config import Settings


async def create_test_user_and_org(client: AsyncClient, email_suffix: str):
    """Вспомогательная функция для создания пользователя и организации"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"org_test_{email_suffix}@example.com",
            "password": "TestPassword123",
            "name": f"Test User {email_suffix}",
            "organization_name": f"Test Org {email_suffix}",
        },
    )
    
    data = response.json()
    access_token = data["data"]["access_token"]
    
    settings = Settings()
    decoded = jwt.decode(access_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    
    return access_token, decoded["organization_id"], decoded["id"]


@pytest.mark.asyncio
async def test_get_my_organizations(client: AsyncClient):
    """Тест получения списка организаций пользователя с ролями"""
    access_token, org_id, user_id = await create_test_user_and_org(client, "list")
    
    response = await client.get(
        "/api/v1/organizations/me",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1
    
    # Проверяем, что организация есть в списке
    user_org = next((org for org in data["data"] if org["id"] == org_id), None)
    assert user_org is not None
    
    # Проверяем, что роль возвращается
    assert "role" in user_org
    assert user_org["role"] == "owner"  # Создатель организации — owner


@pytest.mark.asyncio
async def test_get_organization_members(client: AsyncClient):
    """Тест получения списка участников организации"""
    access_token, org_id, user_id = await create_test_user_and_org(client, "members")
    
    response = await client.get(
        "/api/v1/organizations/members",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1  # Только создатель
    assert data["data"][0]["role"] == "owner"


@pytest.mark.asyncio
async def test_add_member_to_organization(client: AsyncClient):
    """Тест добавления участника в организацию"""
    # Создаем owner
    owner_token, org_id, owner_id = await create_test_user_and_org(client, "owner_add")
    
    # Создаем второго пользователя
    new_user_token, new_org_id, new_user_id = await create_test_user_and_org(client, "member_add")
    
    # Извлекаем email нового пользователя
    new_user_email = f"org_test_member_add@example.com"
    
    # Owner добавляет нового пользователя в свою организацию
    response = await client.post(
        "/api/v1/organizations/members",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": org_id,
        },
        json={
            "email": new_user_email,
            "role": "member",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["role"] == "member"
    assert data["data"]["user_email"] == new_user_email


@pytest.mark.asyncio
async def test_update_member_role(client: AsyncClient):
    """Тест изменения роли участника"""
    # Создаем owner
    owner_token, org_id, owner_id = await create_test_user_and_org(client, "owner_update")
    
    # Создаем второго пользователя и добавляем его
    new_user_token, new_org_id, new_user_id = await create_test_user_and_org(client, "member_update")
    new_user_email = f"org_test_member_update@example.com"
    
    add_response = await client.post(
        "/api/v1/organizations/members",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": org_id,
        },
        json={
            "email": new_user_email,
            "role": "member",
        },
    )
    
    added_member = add_response.json()["data"]
    member_user_id = added_member["user_id"]
    
    # Повышаем роль до manager
    update_response = await client.patch(
        f"/api/v1/organizations/members/{member_user_id}",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": org_id,
        },
        json={
            "role": "manager",
        },
    )
    
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["data"]["role"] == "manager"


@pytest.mark.asyncio
async def test_remove_member_from_organization(client: AsyncClient):
    """Тест удаления участника из организации"""
    # Создаем owner
    owner_token, org_id, owner_id = await create_test_user_and_org(client, "owner_remove")
    
    # Создаем второго пользователя и добавляем его
    new_user_token, new_org_id, new_user_id = await create_test_user_and_org(client, "member_remove")
    new_user_email = f"org_test_member_remove@example.com"
    
    add_response = await client.post(
        "/api/v1/organizations/members",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": org_id,
        },
        json={
            "email": new_user_email,
            "role": "member",
        },
    )
    
    added_member = add_response.json()["data"]
    member_user_id = added_member["user_id"]
    
    # Удаляем участника
    delete_response = await client.delete(
        f"/api/v1/organizations/members/{member_user_id}",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert delete_response.status_code == 204
    
    # Проверяем, что участник удален
    members_response = await client.get(
        "/api/v1/organizations/members",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    members = members_response.json()["data"]
    assert not any(m["user_id"] == member_user_id for m in members)


@pytest.mark.asyncio
async def test_member_cannot_add_users(client: AsyncClient):
    """Тест: member не может добавлять пользователей"""
    # Создаем owner
    owner_token, org_id, owner_id = await create_test_user_and_org(client, "owner_perm")
    
    # Создаем member
    member_token, member_org_id, member_id = await create_test_user_and_org(client, "member_perm")
    member_email = f"org_test_member_perm@example.com"
    
    # Owner добавляет member
    await client.post(
        "/api/v1/organizations/members",
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": org_id,
        },
        json={
            "email": member_email,
            "role": "member",
        },
    )
    
    # Member пытается войти в организацию owner
    settings = Settings()
    decoded = jwt.decode(member_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    
    # Member пытается добавить кого-то (должно вернуть 403)
    third_user_token, _, _ = await create_test_user_and_org(client, "third_perm")
    third_email = f"org_test_third_perm@example.com"
    
    # Получаем токен member для организации owner
    login_response = await client.post(
        "/api/v1/auth/login",
        headers={"X-Organization-Id": org_id},
        json={
            "email": member_email,
            "password": "TestPassword123",
        },
    )
    
    member_token_in_org = login_response.json()["data"]["access_token"]
    
    add_response = await client.post(
        "/api/v1/organizations/members",
        headers={
            "Authorization": f"Bearer {member_token_in_org}",
            "X-Organization-Id": org_id,
        },
        json={
            "email": third_email,
            "role": "member",
        },
    )
    
    assert add_response.status_code == 403


@pytest.mark.asyncio
async def test_cannot_remove_last_owner(client: AsyncClient):
    """Тест: нельзя удалить последнего owner"""
    access_token, org_id, user_id = await create_test_user_and_org(client, "last_owner")
    
    # Пытаемся удалить единственного owner (самого себя)
    response = await client.delete(
        f"/api/v1/organizations/members/{user_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Organization-Id": org_id,
        },
    )
    
    assert response.status_code == 400

