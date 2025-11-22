from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional

from users.models import User, OrganizationMember
from users.entities import UserEntity, UserEntityWithPassword, OrganizationMemberEntity


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_by_id(
        self,
        user_id: UUID,
        include_password: bool = False,
    ) -> UserEntity | UserEntityWithPassword | None:
        query = select(User).where(User.id == user_id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            if include_password:
                return UserEntityWithPassword.model_validate(user)
            return UserEntity.model_validate(user)
        return None

    async def get_user_by_email(
        self,
        email: str,
        include_password: bool = False,
    ) -> UserEntity | UserEntityWithPassword | None:
        query = select(User).where(User.email == email)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            if include_password:
                return UserEntityWithPassword.model_validate(user)
            return UserEntity.model_validate(user)
        return None

    async def create_user(self, user_data: dict) -> UserEntity:
        user = User(**user_data)
        self._session.add(user)
        await self._session.flush()
        return UserEntity.model_validate(user)

    async def user_exists(self, email: str) -> bool:
        query = select(exists().where(User.email == email))
        result = await self._session.execute(query)
        return result.scalar()

    async def get_user_membership(
        self, user_id: UUID, organization_id: UUID
    ) -> Optional[OrganizationMemberEntity]:
        query = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id
        )
        result = await self._session.execute(query)
        member = result.scalar_one_or_none()
        if member:
            return OrganizationMemberEntity.model_validate(member)
        return None

    async def get_user_memberships(self, user_id: UUID) -> list[OrganizationMemberEntity]:
        query = select(OrganizationMember).where(OrganizationMember.user_id == user_id)
        result = await self._session.execute(query)
        members = result.scalars().all()
        return [OrganizationMemberEntity.model_validate(m) for m in members]

