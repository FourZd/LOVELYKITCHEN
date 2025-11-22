from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import date

from tasks.entities import TaskEntity


class CreateTaskRequest(BaseModel):
    deal_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[date] = None


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[date] = None
    is_done: Optional[bool] = None


class TaskResponse(BaseModel):
    data: TaskEntity


class TasksListResponse(BaseModel):
    data: list[TaskEntity]

