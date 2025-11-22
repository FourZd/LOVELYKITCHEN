from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from decimal import Decimal

from deals.entities import DealEntity
from deals.enums import DealStatus, DealStage


class CreateDealRequest(BaseModel):
    contact_id: UUID
    title: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(ge=0)
    currency: str = Field(default="USD", max_length=10)


class UpdateDealRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    status: Optional[DealStatus] = None
    stage: Optional[DealStage] = None


class DealResponse(BaseModel):
    data: DealEntity


class DealsListResponse(BaseModel):
    data: list[DealEntity]
    total: int
    page: int
    page_size: int

