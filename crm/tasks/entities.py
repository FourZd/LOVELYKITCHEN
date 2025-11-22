from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Optional


class TaskEntity(BaseModel):
    id: UUID
    deal_id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    is_done: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

