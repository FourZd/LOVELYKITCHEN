from typing import Annotated, Optional
from fastapi import APIRouter
from uuid import UUID
from datetime import date
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from tasks.schemas import CreateTaskRequest, UpdateTaskRequest, TaskResponse, TasksListResponse
from tasks.usecases import (
    CreateTaskUseCase,
    GetTaskUseCase,
    UpdateTaskUseCase,
    DeleteTaskUseCase,
    ListTasksUseCase,
)
from auth.entities import AuthenticatedUser


router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["tasks"],
)


@router.get("", response_model=TasksListResponse)
@inject
async def list_tasks(
    list_usecase: Annotated[ListTasksUseCase, FromComponent("tasks")],
    deal_id: Optional[UUID] = None,
    only_open: bool = False,
    due_before: Optional[date] = None,
    due_after: Optional[date] = None,
):
    tasks = await list_usecase(deal_id, only_open, due_before, due_after)
    return TasksListResponse(data=tasks)


@router.post("", response_model=TaskResponse)
@inject
async def create_task(
    request: CreateTaskRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    create_usecase: Annotated[CreateTaskUseCase, FromComponent("tasks")],
):
    task = await create_usecase(
        user, request.deal_id, request.title, request.description, request.due_date
    )
    return TaskResponse(data=task)


@router.get("/{task_id}", response_model=TaskResponse)
@inject
async def get_task(
    task_id: UUID,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    get_usecase: Annotated[GetTaskUseCase, FromComponent("tasks")],
):
    task = await get_usecase(user, task_id)
    return TaskResponse(data=task)


@router.patch("/{task_id}", response_model=TaskResponse)
@inject
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    update_usecase: Annotated[UpdateTaskUseCase, FromComponent("tasks")],
):
    update_data = request.model_dump(exclude_unset=True)
    task = await update_usecase(user, task_id, update_data)
    return TaskResponse(data=task)


@router.delete("/{task_id}", status_code=204)
@inject
async def delete_task(
    task_id: UUID,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    delete_usecase: Annotated[DeleteTaskUseCase, FromComponent("tasks")],
):
    await delete_usecase(user, task_id)

