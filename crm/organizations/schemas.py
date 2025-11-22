from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from organizations.entities import OrganizationWithRoleEntity, OrganizationMemberEntity
from users.enums import UserRole


class OrganizationsListResponse(BaseModel):
    data: list[OrganizationWithRoleEntity]


class AddMemberRequest(BaseModel):
    email: EmailStr
    role: UserRole = Field(default=UserRole.MEMBER)


class UpdateMemberRoleRequest(BaseModel):
    role: UserRole


class MemberResponse(BaseModel):
    data: OrganizationMemberEntity


class MembersListResponse(BaseModel):
    data: list[OrganizationMemberEntity]

