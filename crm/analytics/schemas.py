from pydantic import BaseModel
from typing import Dict
from decimal import Decimal


class DealsSummaryResponse(BaseModel):
    count_by_status: Dict[str, int]
    amount_by_status: Dict[str, Decimal]
    average_won_amount: Decimal
    new_deals_last_n_days: int


class FunnelStageData(BaseModel):
    stage: str
    count_by_status: Dict[str, int]
    conversion_rate: float


class DealsFunnelResponse(BaseModel):
    data: list[FunnelStageData]

