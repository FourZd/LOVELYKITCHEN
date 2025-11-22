from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from activities.models import Activity
from activities.entities import ActivityEntity


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, activity_id: UUID) -> Optional[ActivityEntity]:
        query = select(Activity).where(Activity.id == activity_id)
        result = await self._session.execute(query)
        activity = result.scalar_one_or_none()
        if activity:
            return ActivityEntity.model_validate(activity)
        return None

    async def create(self, activity_data: dict) -> ActivityEntity:
        activity = Activity(**activity_data)
        self._session.add(activity)
        await self._session.flush()
        return ActivityEntity.model_validate(activity)

    async def list_by_deal(self, deal_id: UUID) -> list[ActivityEntity]:
        query = (
            select(Activity)
            .where(Activity.deal_id == deal_id)
            .order_by(Activity.created_at.desc())
        )
        result = await self._session.execute(query)
        activities = result.scalars().all()
        return [ActivityEntity.model_validate(a) for a in activities]

