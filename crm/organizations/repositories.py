from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
from typing import Optional

from organizations.models import Organization
from organizations.entities import OrganizationEntity, OrganizationWithRoleEntity, OrganizationMemberEntity
from users.models import OrganizationMember, User
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

    async def get_user_organizations(self, user_id: UUID) -> list[OrganizationWithRoleEntity]:
        """Получить список организаций пользователя с его ролями"""
        query = (
            select(
                Organization.id,
                Organization.name,
                Organization.created_at,
                OrganizationMember.role
            )
            .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
            .where(OrganizationMember.user_id == user_id)
        )
        result = await self._session.execute(query)
        rows = result.all()
        return [
            OrganizationWithRoleEntity(
                id=row.id,
                name=row.name,
                created_at=row.created_at,
                role=row.role
            )
            for row in rows
        ]

    async def get_members(self, organization_id: UUID) -> list[OrganizationMemberEntity]:
        query = (
            select(
                OrganizationMember.id,
                OrganizationMember.organization_id,
                OrganizationMember.user_id,
                User.email.label("user_email"),
                User.name.label("user_name"),
                OrganizationMember.role
            )
            .join(User, OrganizationMember.user_id == User.id)
            .where(OrganizationMember.organization_id == organization_id)
        )
        result = await self._session.execute(query)
        rows = result.all()
        return [
            OrganizationMemberEntity(
                id=row.id,
                organization_id=row.organization_id,
                user_id=row.user_id,
                user_email=row.user_email,
                user_name=row.user_name,
                role=row.role
            )
            for row in rows
        ]

    async def get_member(self, organization_id: UUID, user_id: UUID) -> Optional[OrganizationMember]:
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def update_member_role(self, organization_id: UUID, user_id: UUID, role: UserRole):
        member = await self.get_member(organization_id, user_id)
        if member:
            member.role = role
            await self._session.flush()

    async def remove_member(self, organization_id: UUID, user_id: UUID):
        query = delete(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id
        )
        await self._session.execute(query)

