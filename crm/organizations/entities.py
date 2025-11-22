from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from users.enums import UserRole


class OrganizationEntity(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationWithRoleEntity(BaseModel):
    """Организация с ролью текущего пользователя"""
    id: UUID
    name: str
    created_at: datetime
    role: UserRole

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class OrganizationMemberEntity(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    user_email: str
    user_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

