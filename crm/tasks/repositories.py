from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from uuid import UUID
from typing import Optional
from datetime import date

from tasks.models import Task
from tasks.entities import TaskEntity


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, task_id: UUID) -> Optional[TaskEntity]:
        query = select(Task).where(Task.id == task_id)
        result = await self._session.execute(query)
        task = result.scalar_one_or_none()
        if task:
            return TaskEntity.model_validate(task)
        return None

    async def create(self, task_data: dict) -> TaskEntity:
        task = Task(**task_data)
        self._session.add(task)
        await self._session.flush()
        return TaskEntity.model_validate(task)

    async def update(self, task_id: UUID, task_data: dict):
        stmt = update(Task).where(Task.id == task_id).values(**task_data)
        await self._session.execute(stmt)

    async def delete(self, task_id: UUID) -> bool:
        stmt = delete(Task).where(Task.id == task_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def list_by_deal(self, deal_id: UUID) -> list[TaskEntity]:
        query = select(Task).where(Task.deal_id == deal_id)
        result = await self._session.execute(query)
        tasks = result.scalars().all()
        return [TaskEntity.model_validate(t) for t in tasks]

    async def list_with_filters(
        self,
        deal_id: Optional[UUID] = None,
        only_open: bool = False,
        due_before: Optional[date] = None,
        due_after: Optional[date] = None
    ) -> list[TaskEntity]:
        query = select(Task)
        
        if deal_id:
            query = query.where(Task.deal_id == deal_id)
        
        if only_open:
            query = query.where(Task.is_done == False)
        
        if due_before:
            query = query.where(Task.due_date <= due_before)
        
        if due_after:
            query = query.where(Task.due_date >= due_after)
        
        result = await self._session.execute(query)
        tasks = result.scalars().all()
        return [TaskEntity.model_validate(t) for t in tasks]

