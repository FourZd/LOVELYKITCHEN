from pydantic import BaseModel
from organizations.entities import OrganizationEntity


class OrganizationsListResponse(BaseModel):
    data: list[OrganizationEntity]

