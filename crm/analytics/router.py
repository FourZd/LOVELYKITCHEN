from typing import Annotated
from fastapi import APIRouter, Query
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from analytics.entities import DealsSummaryEntity, DealsFunnelEntity
from analytics.usecases import GetDealsSummaryUseCase, GetDealsFunnelUseCase
from auth.entities import AuthenticatedUser


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"],
)


@router.get("/deals/summary", response_model=DealsSummaryEntity)
@inject
async def get_deals_summary(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    summary_usecase: Annotated[GetDealsSummaryUseCase, FromComponent("analytics")],
    days: int = Query(30, ge=1, le=365),
):
    return await summary_usecase(user, days)


@router.get("/deals/funnel", response_model=DealsFunnelEntity)
@inject
async def get_deals_funnel(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    funnel_usecase: Annotated[GetDealsFunnelUseCase, FromComponent("analytics")],
):
    return await funnel_usecase(user)

