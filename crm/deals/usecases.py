from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal

from core.database.unit_of_work import UnitOfWork
from deals.repositories import DealRepository
from contacts.repositories import ContactRepository
from activities.repositories import ActivityRepository
from deals.entities import DealEntity
from deals.enums import DealStatus, DealStage
from deals.exceptions import (
    DealNotFoundError,
    DealAccessDeniedError,
    InvalidDealAmountError,
    InvalidStageTransitionError,
)
from contacts.exceptions import ContactNotFoundError
from users.enums import UserRole
from auth.entities import AuthenticatedUser


STAGE_ORDER = {
    DealStage.QUALIFICATION: 0,
    DealStage.PROPOSAL: 1,
    DealStage.NEGOTIATION: 2,
    DealStage.CLOSED: 3,
}


class CreateDealUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        deal_repository: DealRepository,
        contact_repository: ContactRepository,
    ):
        self._uow = uow
        self._deal_repository = deal_repository
        self._contact_repository = contact_repository

    async def __call__(
        self,
        user: AuthenticatedUser,
        contact_id: UUID,
        title: str,
        amount: Decimal,
        currency: str,
    ) -> DealEntity:
        async with self._uow:
            contact = await self._contact_repository.get_by_id(contact_id)
            if not contact:
                raise ContactNotFoundError()
            
            if contact.organization_id != user.organization_id:
                raise DealAccessDeniedError()

            deal_data = {
                "id": uuid4(),
                "organization_id": user.organization_id,
                "contact_id": contact_id,
                "owner_id": user.id,
                "title": title,
                "amount": amount,
                "currency": currency,
                "status": DealStatus.NEW,
                "stage": DealStage.QUALIFICATION,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            return await self._deal_repository.create(deal_data)


class GetDealUseCase:
    def __init__(self, uow: UnitOfWork, deal_repository: DealRepository):
        self._uow = uow
        self._deal_repository = deal_repository

    async def __call__(self, user: AuthenticatedUser, deal_id: UUID) -> DealEntity:
        async with self._uow:
            deal = await self._deal_repository.get_by_id(deal_id)
            if not deal:
                raise DealNotFoundError()
            
            if deal.organization_id != user.organization_id:
                raise DealAccessDeniedError()
            
            return deal


class UpdateDealUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        deal_repository: DealRepository,
        activity_repository: ActivityRepository,
    ):
        self._uow = uow
        self._deal_repository = deal_repository
        self._activity_repository = activity_repository

    async def __call__(
        self, user: AuthenticatedUser, deal_id: UUID, update_data: dict
    ) -> DealEntity:
        async with self._uow:
            deal = await self._deal_repository.get_by_id(deal_id)
            if not deal:
                raise DealNotFoundError()
            
            if deal.organization_id != user.organization_id:
                raise DealAccessDeniedError()
            
            if user.role == UserRole.MEMBER.value and deal.owner_id != user.id:
                raise DealAccessDeniedError()

            if "status" in update_data:
                new_status = update_data["status"]
                if new_status == DealStatus.WON.value:
                    current_amount = update_data.get("amount", deal.amount)
                    if current_amount <= 0:
                        raise InvalidDealAmountError("error.deal.amount_must_be_positive_for_won")

                if new_status != deal.status:
                    activity_data = {
                        "id": uuid4(),
                        "deal_id": deal_id,
                        "author_id": user.id,
                        "type": "status_changed",
                        "payload": {
                            "old_status": deal.status,
                            "new_status": new_status,
                        },
                        "created_at": datetime.now(timezone.utc),
                    }
                    await self._activity_repository.create(activity_data)

            if "stage" in update_data:
                new_stage = DealStage(update_data["stage"])
                old_stage = DealStage(deal.stage)
                
                if STAGE_ORDER[new_stage] < STAGE_ORDER[old_stage]:
                    if user.role not in [UserRole.ADMIN.value, UserRole.OWNER.value]:
                        raise InvalidStageTransitionError("error.deal.stage_rollback_not_allowed")

                if new_stage != old_stage:
                    activity_data = {
                        "id": uuid4(),
                        "deal_id": deal_id,
                        "author_id": user.id,
                        "type": "stage_changed",
                        "payload": {
                            "old_stage": deal.stage,
                            "new_stage": new_stage.value,
                        },
                        "created_at": datetime.now(timezone.utc),
                    }
                    await self._activity_repository.create(activity_data)

            await self._deal_repository.update(deal_id, update_data)
            
            update_data["updated_at"] = datetime.now(timezone.utc)
            updated_deal = deal.model_copy(update=update_data)
            return updated_deal


class DeleteDealUseCase:
    def __init__(self, uow: UnitOfWork, deal_repository: DealRepository):
        self._uow = uow
        self._deal_repository = deal_repository

    async def __call__(self, user: AuthenticatedUser, deal_id: UUID):
        async with self._uow:
            deal = await self._deal_repository.get_by_id(deal_id)
            if not deal:
                raise DealNotFoundError()
            
            if deal.organization_id != user.organization_id:
                raise DealAccessDeniedError()
            
            if user.role == UserRole.MEMBER.value and deal.owner_id != user.id:
                raise DealAccessDeniedError()
            
            await self._deal_repository.delete(deal_id)


class ListDealsUseCase:
    def __init__(self, uow: UnitOfWork, deal_repository: DealRepository):
        self._uow = uow
        self._deal_repository = deal_repository

    async def __call__(
        self,
        user: AuthenticatedUser,
        page: int = 1,
        page_size: int = 50,
        statuses: Optional[list[str]] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        stage: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[DealEntity], int]:
        async with self._uow:
            if user.role == UserRole.MEMBER.value:
                owner_id = user.id
            
            status_enums = [DealStatus(s) for s in statuses] if statuses else None
            stage_enum = DealStage(stage) if stage else None
            
            return await self._deal_repository.list_by_organization(
                user.organization_id,
                page,
                page_size,
                status_enums,
                min_amount,
                max_amount,
                stage_enum,
                owner_id,
                order_by,
                order,
            )

