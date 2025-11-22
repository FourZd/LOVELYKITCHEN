from uuid import UUID

from core.database.unit_of_work import UnitOfWork
from organizations.repositories import OrganizationRepository
from users.repositories import UserRepository
from organizations.entities import OrganizationEntity, OrganizationWithRoleEntity, OrganizationMemberEntity
from organizations.exceptions import (
    OrganizationNotFoundError,
    MemberNotFoundError,
    MemberAlreadyExistsError,
    CannotRemoveLastOwnerError,
    InsufficientPermissionsError,
)
from users.exceptions import UserNotFoundError
from users.enums import UserRole
from auth.entities import AuthenticatedUser


class GetUserOrganizationsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        organization_repository: OrganizationRepository,
    ):
        self._uow = uow
        self._organization_repository = organization_repository

    async def __call__(self, user_id: UUID) -> list[OrganizationWithRoleEntity]:
        async with self._uow:
            return await self._organization_repository.get_user_organizations(user_id)


class GetOrganizationMembersUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        organization_repository: OrganizationRepository,
    ):
        self._uow = uow
        self._organization_repository = organization_repository

    async def __call__(self, user: AuthenticatedUser) -> list[OrganizationMemberEntity]:
        async with self._uow:
            org = await self._organization_repository.get_by_id(user.organization_id)
            if not org:
                raise OrganizationNotFoundError()
            
            return await self._organization_repository.get_members(user.organization_id)


class AddOrganizationMemberUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
    ):
        self._uow = uow
        self._organization_repository = organization_repository
        self._user_repository = user_repository

    async def __call__(
        self, 
        current_user: AuthenticatedUser, 
        email: str, 
        role: UserRole
    ) -> OrganizationMemberEntity:
        # Проверка прав: только owner и admin могут добавлять участников
        if current_user.role not in [UserRole.OWNER.value, UserRole.ADMIN.value]:
            raise InsufficientPermissionsError()

        async with self._uow:
            # Проверяем существование организации
            org = await self._organization_repository.get_by_id(current_user.organization_id)
            if not org:
                raise OrganizationNotFoundError()

            # Ищем пользователя по email
            user = await self._user_repository.get_user_by_email(email)
            if not user:
                raise UserNotFoundError()

            # Проверяем, не состоит ли уже в организации
            existing_member = await self._organization_repository.get_member(
                current_user.organization_id, user.id
            )
            if existing_member:
                raise MemberAlreadyExistsError()

            # Добавляем участника
            await self._organization_repository.add_member(
                current_user.organization_id, user.id, role
            )

            # Возвращаем информацию о добавленном участнике
            members = await self._organization_repository.get_members(current_user.organization_id)
            added_member = next((m for m in members if m.user_id == user.id), None)
            if not added_member:
                raise MemberNotFoundError()
            
            return added_member


class UpdateMemberRoleUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        organization_repository: OrganizationRepository,
    ):
        self._uow = uow
        self._organization_repository = organization_repository

    async def __call__(
        self,
        current_user: AuthenticatedUser,
        member_user_id: UUID,
        new_role: UserRole,
    ) -> OrganizationMemberEntity:
        # Проверка прав: только owner и admin могут менять роли
        if current_user.role not in [UserRole.OWNER.value, UserRole.ADMIN.value]:
            raise InsufficientPermissionsError()

        async with self._uow:
            # Проверяем существование участника
            member = await self._organization_repository.get_member(
                current_user.organization_id, member_user_id
            )
            if not member:
                raise MemberNotFoundError()

            # Нельзя изменить роль последнего owner
            if member.role == UserRole.OWNER and new_role != UserRole.OWNER:
                members = await self._organization_repository.get_members(current_user.organization_id)
                owner_count = sum(1 for m in members if m.role == UserRole.OWNER.value)
                if owner_count <= 1:
                    raise CannotRemoveLastOwnerError()

            # Обновляем роль
            await self._organization_repository.update_member_role(
                current_user.organization_id, member_user_id, new_role
            )

            # Возвращаем обновленную информацию
            members = await self._organization_repository.get_members(current_user.organization_id)
            updated_member = next((m for m in members if m.user_id == member_user_id), None)
            if not updated_member:
                raise MemberNotFoundError()
            
            return updated_member


class RemoveOrganizationMemberUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        organization_repository: OrganizationRepository,
    ):
        self._uow = uow
        self._organization_repository = organization_repository

    async def __call__(
        self,
        current_user: AuthenticatedUser,
        member_user_id: UUID,
    ):
        # Проверка прав: только owner и admin могут удалять участников
        if current_user.role not in [UserRole.OWNER.value, UserRole.ADMIN.value]:
            raise InsufficientPermissionsError()

        async with self._uow:
            # Проверяем существование участника
            member = await self._organization_repository.get_member(
                current_user.organization_id, member_user_id
            )
            if not member:
                raise MemberNotFoundError()

            # Нельзя удалить последнего owner
            if member.role == UserRole.OWNER:
                members = await self._organization_repository.get_members(current_user.organization_id)
                owner_count = sum(1 for m in members if m.role == UserRole.OWNER.value)
                if owner_count <= 1:
                    raise CannotRemoveLastOwnerError()

            # Удаляем участника
            await self._organization_repository.remove_member(
                current_user.organization_id, member_user_id
            )

