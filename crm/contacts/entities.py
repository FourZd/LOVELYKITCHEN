from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class ContactEntity(BaseModel):
    id: UUID
    organization_id: UUID
    owner_id: UUID
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

