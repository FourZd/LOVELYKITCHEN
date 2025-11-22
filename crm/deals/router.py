from typing import Annotated, Optional
from fastapi import APIRouter, Query
from uuid import UUID
from decimal import Decimal
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from deals.schemas import (
    CreateDealRequest,
    UpdateDealRequest,
    DealResponse,
    DealsListResponse,
)
from deals.usecases import (
    CreateDealUseCase,
    GetDealUseCase,
    UpdateDealUseCase,
    DeleteDealUseCase,
    ListDealsUseCase,
)
from auth.entities import AuthenticatedUser


router = APIRouter(
    prefix="/api/v1/deals",
    tags=["deals"],
)


@router.get("", response_model=DealsListResponse)
@inject
async def list_deals(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    list_usecase: Annotated[ListDealsUseCase, FromComponent("deals")],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[list[str]] = Query(None),
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    stage: Optional[str] = None,
    owner_id: Optional[UUID] = None,
    order_by: str = Query("created_at"),
    order: str = Query("desc"),
):
    deals, total = await list_usecase(
        user, page, page_size, status, min_amount, max_amount, stage, owner_id, order_by, order
    )
    return DealsListResponse(data=deals, total=total, page=page, page_size=page_size)


@router.post("", response_model=DealResponse)
@inject
async def create_deal(
    request: CreateDealRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    create_usecase: Annotated[CreateDealUseCase, FromComponent("deals")],
):
    deal = await create_usecase(
        user, request.contact_id, request.title, request.amount, request.currency
    )
    return DealResponse(data=deal)


@router.get("/{deal_id}", response_model=DealResponse)
@inject
async def get_deal(
    deal_id: UUID,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    get_usecase: Annotated[GetDealUseCase, FromComponent("deals")],
):
    deal = await get_usecase(user, deal_id)
    return DealResponse(data=deal)


@router.patch("/{deal_id}", response_model=DealResponse)
@inject
async def update_deal(
    deal_id: UUID,
    request: UpdateDealRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    update_usecase: Annotated[UpdateDealUseCase, FromComponent("deals")],
):
    update_data = request.model_dump(exclude_unset=True)
    deal = await update_usecase(user, deal_id, update_data)
    return DealResponse(data=deal)


@router.delete("/{deal_id}", status_code=204)
@inject
async def delete_deal(
    deal_id: UUID,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    delete_usecase: Annotated[DeleteDealUseCase, FromComponent("deals")],
):
    await delete_usecase(user, deal_id)

