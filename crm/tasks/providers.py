from typing import Annotated
from dishka import Provider, Scope, provide, FromComponent

from tasks.repositories import TaskRepository
from deals.repositories import DealRepository
from activities.repositories import ActivityRepository
from tasks.usecases import (
    CreateTaskUseCase,
    GetTaskUseCase,
    UpdateTaskUseCase,
    DeleteTaskUseCase,
    ListTasksUseCase,
)
from core.database.unit_of_work import UnitOfWork


class TaskProvider(Provider):
    scope = Scope.REQUEST
    component = "tasks"

    @provide
    def get_task_repository(
        self, uow: Annotated[UnitOfWork, FromComponent("database")]
    ) -> TaskRepository:
        return TaskRepository(uow.session)

    @provide
    def get_create_task_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        task_repository: Annotated[TaskRepository, FromComponent("tasks")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
        activity_repository: Annotated[ActivityRepository, FromComponent("activities")],
    ) -> CreateTaskUseCase:
        return CreateTaskUseCase(uow, task_repository, deal_repository, activity_repository)

    @provide
    def get_get_task_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        task_repository: Annotated[TaskRepository, FromComponent("tasks")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> GetTaskUseCase:
        return GetTaskUseCase(uow, task_repository, deal_repository)

    @provide
    def get_update_task_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        task_repository: Annotated[TaskRepository, FromComponent("tasks")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> UpdateTaskUseCase:
        return UpdateTaskUseCase(uow, task_repository, deal_repository)

    @provide
    def get_delete_task_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        task_repository: Annotated[TaskRepository, FromComponent("tasks")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> DeleteTaskUseCase:
        return DeleteTaskUseCase(uow, task_repository, deal_repository)

    @provide
    def get_list_tasks_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        task_repository: Annotated[TaskRepository, FromComponent("tasks")],
    ) -> ListTasksUseCase:
        return ListTasksUseCase(uow, task_repository)

