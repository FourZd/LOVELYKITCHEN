from typing import Annotated
from fastapi import APIRouter, Query
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from analytics.schemas import DealsSummaryResponse, DealsFunnelResponse
from analytics.usecases import GetDealsSummaryUseCase, GetDealsFunnelUseCase
from auth.entities import AuthenticatedUser


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"],
)


@router.get("/deals/summary", response_model=DealsSummaryResponse)
@inject
async def get_deals_summary(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    summary_usecase: Annotated[GetDealsSummaryUseCase, FromComponent("analytics")],
    days: int = Query(30, ge=1, le=365),
):
    summary = await summary_usecase(user, days)
    return DealsSummaryResponse(
        count_by_status=summary.count_by_status,
        amount_by_status=summary.amount_by_status,
        average_won_amount=summary.average_won_amount,
        new_deals_last_n_days=summary.new_deals_last_n_days,
    )


@router.get("/deals/funnel", response_model=DealsFunnelResponse)
@inject
async def get_deals_funnel(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    funnel_usecase: Annotated[GetDealsFunnelUseCase, FromComponent("analytics")],
):
    funnel = await funnel_usecase(user)
    return DealsFunnelResponse(data=funnel.stages)

