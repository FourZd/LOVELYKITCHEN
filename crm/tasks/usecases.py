from uuid import UUID, uuid4
from datetime import datetime, timezone, date
from typing import Optional

from core.database.unit_of_work import UnitOfWork
from tasks.repositories import TaskRepository
from deals.repositories import DealRepository
from activities.repositories import ActivityRepository
from tasks.entities import TaskEntity
from tasks.exceptions import TaskNotFoundError, TaskAccessDeniedError, InvalidDueDateError
from deals.exceptions import DealNotFoundError, DealAccessDeniedError
from users.enums import UserRole
from auth.entities import AuthenticatedUser


class CreateTaskUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        task_repository: TaskRepository,
        deal_repository: DealRepository,
        activity_repository: ActivityRepository,
    ):
        self._uow = uow
        self._task_repository = task_repository
        self._deal_repository = deal_repository
        self._activity_repository = activity_repository

    async def __call__(
        self,
        user: AuthenticatedUser,
        deal_id: UUID,
        title: str,
        description: Optional[str],
        due_date: Optional[date],
    ) -> TaskEntity:
        async with self._uow:
            deal = await self._deal_repository.get_by_id(deal_id)
            if not deal:
                raise DealNotFoundError()
            
            if deal.organization_id != user.organization_id:
                raise DealAccessDeniedError()
            
            if user.role == UserRole.MEMBER.value and deal.owner_id != user.id:
                raise TaskAccessDeniedError()

            if due_date and due_date < date.today():
                raise InvalidDueDateError()

            task_data = {
                "id": uuid4(),
                "deal_id": deal_id,
                "title": title,
                "description": description,
                "due_date": due_date,
                "is_done": False,
                "created_at": datetime.now(timezone.utc),
            }
            task = await self._task_repository.create(task_data)

            activity_data = {
                "id": uuid4(),
                "deal_id": deal_id,
                "author_id": user.id,
                "type": "task_created",
                "payload": {"task_id": str(task.id), "task_title": title},
                "created_at": datetime.now(timezone.utc),
            }
            await self._activity_repository.create(activity_data)

            return task


class GetTaskUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        task_repository: TaskRepository,
        deal_repository: DealRepository,
    ):
        self._uow = uow
        self._task_repository = task_repository
        self._deal_repository = deal_repository

    async def __call__(self, user: AuthenticatedUser, task_id: UUID) -> TaskEntity:
        async with self._uow:
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                raise TaskNotFoundError()
            
            deal = await self._deal_repository.get_by_id(task.deal_id)
            if not deal or deal.organization_id != user.organization_id:
                raise TaskAccessDeniedError()
            
            return task


class UpdateTaskUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        task_repository: TaskRepository,
        deal_repository: DealRepository,
    ):
        self._uow = uow
        self._task_repository = task_repository
        self._deal_repository = deal_repository

    async def __call__(
        self, user: AuthenticatedUser, task_id: UUID, update_data: dict
    ) -> TaskEntity:
        async with self._uow:
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                raise TaskNotFoundError()
            
            deal = await self._deal_repository.get_by_id(task.deal_id)
            if not deal or deal.organization_id != user.organization_id:
                raise TaskAccessDeniedError()
            
            if user.role == UserRole.MEMBER.value and deal.owner_id != user.id:
                raise TaskAccessDeniedError()

            if "due_date" in update_data and update_data["due_date"]:
                if update_data["due_date"] < date.today():
                    raise InvalidDueDateError()

            await self._task_repository.update(task_id, update_data)
            
            updated_task = task.model_copy(update=update_data)
            return updated_task


class DeleteTaskUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        task_repository: TaskRepository,
        deal_repository: DealRepository,
    ):
        self._uow = uow
        self._task_repository = task_repository
        self._deal_repository = deal_repository

    async def __call__(self, user: AuthenticatedUser, task_id: UUID):
        async with self._uow:
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                raise TaskNotFoundError()
            
            deal = await self._deal_repository.get_by_id(task.deal_id)
            if not deal or deal.organization_id != user.organization_id:
                raise TaskAccessDeniedError()
            
            if user.role == UserRole.MEMBER.value and deal.owner_id != user.id:
                raise TaskAccessDeniedError()
            
            await self._task_repository.delete(task_id)


class ListTasksUseCase:
    def __init__(self, uow: UnitOfWork, task_repository: TaskRepository):
        self._uow = uow
        self._task_repository = task_repository

    async def __call__(
        self,
        deal_id: Optional[UUID] = None,
        only_open: bool = False,
        due_before: Optional[date] = None,
        due_after: Optional[date] = None,
    ) -> list[TaskEntity]:
        async with self._uow:
            return await self._task_repository.list_with_filters(
                deal_id, only_open, due_before, due_after
            )

