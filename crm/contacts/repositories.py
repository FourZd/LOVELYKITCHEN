from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, exists, update, delete
from uuid import UUID
from typing import Optional

from contacts.models import Contact
from contacts.entities import ContactEntity
from deals.models import Deal


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, contact_id: UUID) -> Optional[ContactEntity]:
        query = select(Contact).where(Contact.id == contact_id)
        result = await self._session.execute(query)
        contact = result.scalar_one_or_none()
        if contact:
            return ContactEntity.model_validate(contact)
        return None

    async def create(self, contact_data: dict) -> ContactEntity:
        contact = Contact(**contact_data)
        self._session.add(contact)
        await self._session.flush()
        return ContactEntity.model_validate(contact)

    async def update(self, contact_id: UUID, contact_data: dict):
        stmt = update(Contact).where(Contact.id == contact_id).values(**contact_data)
        await self._session.execute(stmt)

    async def delete(self, contact_id: UUID) -> bool:
        stmt = delete(Contact).where(Contact.id == contact_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def list_by_organization(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        owner_id: Optional[UUID] = None
    ) -> tuple[list[ContactEntity], int]:
        query = select(Contact).where(Contact.organization_id == organization_id)
        
        if search:
            query = query.where(
                (Contact.name.ilike(f"%{search}%")) | 
                (Contact.email.ilike(f"%{search}%"))
            )
        
        if owner_id:
            query = query.where(Contact.owner_id == owner_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = await self._session.scalar(count_query)
        
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(query)
        contacts = result.scalars().all()
        
        return [ContactEntity.model_validate(c) for c in contacts], total or 0

    async def has_active_deals(self, contact_id: UUID) -> bool:
        query = select(exists().where(Deal.contact_id == contact_id))
        result = await self._session.execute(query)
        return result.scalar()

