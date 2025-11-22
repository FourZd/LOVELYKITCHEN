from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from deals.enums import DealStatus, DealStage


class DealEntity(BaseModel):
    id: UUID
    organization_id: UUID
    contact_id: UUID
    owner_id: UUID
    title: str
    amount: Decimal
    currency: str
    status: DealStatus
    stage: DealStage
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

