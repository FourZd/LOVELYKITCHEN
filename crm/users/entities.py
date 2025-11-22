from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

from users.enums import UserRole


class UserEntity(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserEntityWithPassword(UserEntity):
    hashed_password: str


class OrganizationMemberEntity(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: UserRole

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

