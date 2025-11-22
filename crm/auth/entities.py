from pydantic import BaseModel, ConfigDict
from uuid import UUID

from users.enums import UserRole


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    access_expiration: int
    refresh_expiration: int
    organization_id: str


class AuthenticatedUser(BaseModel):
    id: UUID
    email: str
    organization_id: UUID
    role: UserRole

    model_config = ConfigDict(use_enum_values=True)

