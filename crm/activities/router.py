from typing import Annotated
from fastapi import APIRouter
from uuid import UUID
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from activities.schemas import CreateActivityRequest, ActivityResponse, ActivitiesListResponse
from activities.usecases import CreateActivityUseCase, ListActivitiesUseCase
from auth.entities import AuthenticatedUser


router = APIRouter(
    prefix="/api/v1/deals/{deal_id}/activities",
    tags=["activities"],
)


@router.get("", response_model=ActivitiesListResponse)
@inject
async def list_activities(
    deal_id: UUID,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    list_usecase: Annotated[ListActivitiesUseCase, FromComponent("activities")],
):
    activities = await list_usecase(user, deal_id)
    return ActivitiesListResponse(data=activities)


@router.post("", response_model=ActivityResponse)
@inject
async def create_activity(
    deal_id: UUID,
    request: CreateActivityRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    create_usecase: Annotated[CreateActivityUseCase, FromComponent("activities")],
):
    activity = await create_usecase(user, deal_id, request.type, request.payload)
    return ActivityResponse(data=activity)

