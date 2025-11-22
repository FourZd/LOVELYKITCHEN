from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

from core.database.unit_of_work import UnitOfWork
from contacts.repositories import ContactRepository
from contacts.entities import ContactEntity
from contacts.exceptions import ContactNotFoundError, ContactAccessDeniedError, ContactHasActiveDealsError
from users.enums import UserRole
from auth.entities import AuthenticatedUser


class CreateContactUseCase:
    def __init__(self, uow: UnitOfWork, contact_repository: ContactRepository):
        self._uow = uow
        self._contact_repository = contact_repository

    async def __call__(
        self, user: AuthenticatedUser, name: str, email: Optional[str], phone: Optional[str]
    ) -> ContactEntity:
        async with self._uow:
            contact_data = {
                "id": uuid4(),
                "organization_id": user.organization_id,
                "owner_id": user.id,
                "name": name,
                "email": email,
                "phone": phone,
                "created_at": datetime.now(timezone.utc),
            }
            return await self._contact_repository.create(contact_data)


class GetContactUseCase:
    def __init__(self, uow: UnitOfWork, contact_repository: ContactRepository):
        self._uow = uow
        self._contact_repository = contact_repository

    async def __call__(self, user: AuthenticatedUser, contact_id: UUID) -> ContactEntity:
        async with self._uow:
            contact = await self._contact_repository.get_by_id(contact_id)
            if not contact:
                raise ContactNotFoundError()
            
            if contact.organization_id != user.organization_id:
                raise ContactAccessDeniedError()
            
            return contact


class UpdateContactUseCase:
    def __init__(self, uow: UnitOfWork, contact_repository: ContactRepository):
        self._uow = uow
        self._contact_repository = contact_repository

    async def __call__(
        self, user: AuthenticatedUser, contact_id: UUID, update_data: dict
    ) -> ContactEntity:
        async with self._uow:
            contact = await self._contact_repository.get_by_id(contact_id)
            if not contact:
                raise ContactNotFoundError()
            
            if contact.organization_id != user.organization_id:
                raise ContactAccessDeniedError()
            
            if user.role == UserRole.MEMBER.value and contact.owner_id != user.id:
                raise ContactAccessDeniedError()
            
            await self._contact_repository.update(contact_id, update_data)
            
            updated_contact = contact.model_copy(update=update_data)
            return updated_contact


class DeleteContactUseCase:
    def __init__(self, uow: UnitOfWork, contact_repository: ContactRepository):
        self._uow = uow
        self._contact_repository = contact_repository

    async def __call__(self, user: AuthenticatedUser, contact_id: UUID):
        async with self._uow:
            contact = await self._contact_repository.get_by_id(contact_id)
            if not contact:
                raise ContactNotFoundError()
            
            if contact.organization_id != user.organization_id:
                raise ContactAccessDeniedError()
            
            if user.role == UserRole.MEMBER.value and contact.owner_id != user.id:
                raise ContactAccessDeniedError()
            
            has_deals = await self._contact_repository.has_active_deals(contact_id)
            if has_deals:
                raise ContactHasActiveDealsError()
            
            await self._contact_repository.delete(contact_id)


class ListContactsUseCase:
    def __init__(self, uow: UnitOfWork, contact_repository: ContactRepository):
        self._uow = uow
        self._contact_repository = contact_repository

    async def __call__(
        self,
        user: AuthenticatedUser,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> tuple[list[ContactEntity], int]:
        async with self._uow:
            if user.role == UserRole.MEMBER.value:
                owner_id = user.id
            
            return await self._contact_repository.list_by_organization(
                user.organization_id, page, page_size, search, owner_id
            )

