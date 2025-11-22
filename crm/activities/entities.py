from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

from activities.enums import ActivityType


class ActivityEntity(BaseModel):
    id: UUID
    deal_id: UUID
    author_id: Optional[UUID] = None
    type: ActivityType
    payload: Optional[dict] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True, use_enum_values=True
    )

