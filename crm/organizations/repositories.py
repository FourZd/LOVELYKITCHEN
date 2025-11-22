from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from organizations.models import Organization
from organizations.entities import OrganizationEntity
from users.models import OrganizationMember
from users.enums import UserRole


class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, organization_id: UUID) -> Optional[OrganizationEntity]:
        query = select(Organization).where(Organization.id == organization_id)
        result = await self._session.execute(query)
        org = result.scalar_one_or_none()
        if org:
            return OrganizationEntity.model_validate(org)
        return None

    async def create(self, org_data: dict) -> OrganizationEntity:
        org = Organization(**org_data)
        self._session.add(org)
        await self._session.flush()
        return OrganizationEntity.model_validate(org)

    async def add_member(self, organization_id: UUID, user_id: UUID, role: UserRole):
        member = OrganizationMember(
            organization_id=organization_id,
            user_id=user_id,
            role=role
        )
        self._session.add(member)
        await self._session.flush()

    async def get_user_organizations(self, user_id: UUID) -> list[OrganizationEntity]:
        query = (
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
        )
        result = await self._session.execute(query)
        orgs = result.scalars().all()
        return [OrganizationEntity.model_validate(org) for org in orgs]

