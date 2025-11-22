from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from deals.models import Deal, DealStatus, DealStage
from deals.entities import DealEntity


class DealRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, deal_id: UUID) -> Optional[DealEntity]:
        query = select(Deal).where(Deal.id == deal_id)
        result = await self._session.execute(query)
        deal = result.scalar_one_or_none()
        if deal:
            return DealEntity.model_validate(deal)
        return None

    async def create(self, deal_data: dict) -> DealEntity:
        deal = Deal(**deal_data)
        self._session.add(deal)
        await self._session.flush()
        return DealEntity.model_validate(deal)

    async def update(self, deal_id: UUID, deal_data: dict):
        deal_data["updated_at"] = datetime.now(timezone.utc)
        stmt = update(Deal).where(Deal.id == deal_id).values(**deal_data)
        await self._session.execute(stmt)

    async def delete(self, deal_id: UUID) -> bool:
        stmt = delete(Deal).where(Deal.id == deal_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def list_by_organization(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 50,
        statuses: Optional[list[DealStatus]] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        stage: Optional[DealStage] = None,
        owner_id: Optional[UUID] = None,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> tuple[list[DealEntity], int]:
        query = select(Deal).where(Deal.organization_id == organization_id)
        
        if statuses:
            query = query.where(Deal.status.in_(statuses))
        
        if min_amount is not None:
            query = query.where(Deal.amount >= min_amount)
        
        if max_amount is not None:
            query = query.where(Deal.amount <= max_amount)
        
        if stage:
            query = query.where(Deal.stage == stage)
        
        if owner_id:
            query = query.where(Deal.owner_id == owner_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = await self._session.scalar(count_query)
        
        order_column = getattr(Deal, order_by, Deal.created_at)
        if order == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(query)
        deals = result.scalars().all()
        
        return [DealEntity.model_validate(d) for d in deals], total or 0

    async def get_deals_count_by_status(self, organization_id: UUID) -> dict[str, int]:
        query = select(
            Deal.status,
            func.count(Deal.id).label("count")
        ).where(
            Deal.organization_id == organization_id
        ).group_by(Deal.status)
        
        result = await self._session.execute(query)
        return {row.status: row.count for row in result.all()}

    async def get_deals_amount_by_status(self, organization_id: UUID) -> dict[str, Decimal]:
        query = select(
            Deal.status,
            func.sum(Deal.amount).label("total_amount")
        ).where(
            Deal.organization_id == organization_id
        ).group_by(Deal.status)
        
        result = await self._session.execute(query)
        return {row.status: row.total_amount or Decimal(0) for row in result.all()}

    async def get_new_deals_count(self, organization_id: UUID, days: int = 30) -> int:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = select(func.count(Deal.id)).where(
            Deal.organization_id == organization_id,
            Deal.created_at >= cutoff_date
        )
        result = await self._session.scalar(query)
        return result or 0

    async def get_won_deals_average(self, organization_id: UUID) -> Decimal:
        query = select(func.avg(Deal.amount)).where(
            Deal.organization_id == organization_id,
            Deal.status == DealStatus.WON
        )
        result = await self._session.scalar(query)
        return result or Decimal(0)

    async def get_deals_funnel_data(
        self, organization_id: UUID
    ) -> list[tuple[str, str, int]]:
        query = select(
            Deal.stage,
            Deal.status,
            func.count(Deal.id).label("count")
        ).where(
            Deal.organization_id == organization_id
        ).group_by(Deal.stage, Deal.status).order_by(Deal.stage)
        
        result = await self._session.execute(query)
        return [(row.stage, row.status, row.count) for row in result.all()]

