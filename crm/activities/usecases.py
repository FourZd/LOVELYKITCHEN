from uuid import UUID, uuid4
from datetime import datetime, timezone

from core.database.unit_of_work import UnitOfWork
from activities.repositories import ActivityRepository
from deals.repositories import DealRepository
from activities.entities import ActivityEntity
from activities.exceptions import ActivityAccessDeniedError
from deals.exceptions import DealNotFoundError
from auth.entities import AuthenticatedUser


class CreateActivityUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        activity_repository: ActivityRepository,
        deal_repository: DealRepository,
    ):
        self._uow = uow
        self._activity_repository = activity_repository
        self._deal_repository = deal_repository

    async def __call__(
        self, user: AuthenticatedUser, deal_id: UUID, activity_type: str, payload: dict
    ) -> ActivityEntity:
        async with self._uow:
            deal = await self._deal_repository.get_by_id(deal_id)
            if not deal:
                raise DealNotFoundError()
            
            if deal.organization_id != user.organization_id:
                raise ActivityAccessDeniedError()

            activity_data = {
                "id": uuid4(),
                "deal_id": deal_id,
                "author_id": user.id,
                "type": activity_type,
                "payload": payload,
                "created_at": datetime.now(timezone.utc),
            }
            return await self._activity_repository.create(activity_data)


class ListActivitiesUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        activity_repository: ActivityRepository,
        deal_repository: DealRepository,
    ):
        self._uow = uow
        self._activity_repository = activity_repository
        self._deal_repository = deal_repository

    async def __call__(self, user: AuthenticatedUser, deal_id: UUID) -> list[ActivityEntity]:
        async with self._uow:
            deal = await self._deal_repository.get_by_id(deal_id)
            if not deal:
                raise DealNotFoundError()
            
            if deal.organization_id != user.organization_id:
                raise ActivityAccessDeniedError()
            
            return await self._activity_repository.list_by_deal(deal_id)

