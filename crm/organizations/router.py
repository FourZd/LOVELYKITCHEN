from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, status
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from organizations.schemas import (
    OrganizationsListResponse,
    MembersListResponse,
    AddMemberRequest,
    UpdateMemberRoleRequest,
    MemberResponse,
)
from organizations.usecases import (
    GetUserOrganizationsUseCase,
    GetOrganizationMembersUseCase,
    AddOrganizationMemberUseCase,
    UpdateMemberRoleUseCase,
    RemoveOrganizationMemberUseCase,
)
from auth.entities import AuthenticatedUser


router = APIRouter(
    prefix="/api/v1/organizations",
    tags=["organizations"],
)


@router.get("/me", response_model=OrganizationsListResponse)
@inject
async def get_my_organizations(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    get_orgs_usecase: Annotated[GetUserOrganizationsUseCase, FromComponent("organizations")],
):
    """Получить список организаций, в которых состоит текущий пользователь"""
    orgs = await get_orgs_usecase(user.id)
    return OrganizationsListResponse(data=orgs)


@router.get("/members", response_model=MembersListResponse)
@inject
async def get_organization_members(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    get_members_usecase: Annotated[GetOrganizationMembersUseCase, FromComponent("organizations")],
):
    """Получить список участников текущей организации"""
    members = await get_members_usecase(user)
    return MembersListResponse(data=members)


@router.post("/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
@inject
async def add_organization_member(
    request: AddMemberRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    add_member_usecase: Annotated[AddOrganizationMemberUseCase, FromComponent("organizations")],
):
    """
    Добавить пользователя в организацию (только для owner/admin)
    
    Пользователь должен быть уже зарегистрирован в системе.
    """
    member = await add_member_usecase(user, request.email, request.role)
    return MemberResponse(data=member)


@router.patch("/members/{user_id}", response_model=MemberResponse)
@inject
async def update_member_role(
    user_id: UUID,
    request: UpdateMemberRoleRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    update_role_usecase: Annotated[UpdateMemberRoleUseCase, FromComponent("organizations")],
):
    """
    Изменить роль участника организации (только для owner/admin)
    
    Нельзя изменить роль последнего owner.
    """
    member = await update_role_usecase(user, user_id, request.role)
    return MemberResponse(data=member)


@router.delete("/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_organization_member(
    user_id: UUID,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    remove_member_usecase: Annotated[RemoveOrganizationMemberUseCase, FromComponent("organizations")],
):
    """
    Удалить участника из организации (только для owner/admin)
    
    Нельзя удалить последнего owner.
    """
    await remove_member_usecase(user, user_id)

