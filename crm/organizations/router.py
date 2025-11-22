from typing import Annotated
from fastapi import APIRouter
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from organizations.schemas import OrganizationsListResponse
from organizations.usecases import GetUserOrganizationsUseCase
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
    orgs = await get_orgs_usecase(user.id)
    return OrganizationsListResponse(data=orgs)

