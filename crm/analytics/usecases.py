from core.database.unit_of_work import UnitOfWork
from deals.repositories import DealRepository
from analytics.entities import DealsSummaryEntity, DealsFunnelEntity, FunnelStageEntity
from auth.entities import AuthenticatedUser


class GetDealsSummaryUseCase:
    def __init__(self, uow: UnitOfWork, deal_repository: DealRepository):
        self._uow = uow
        self._deal_repository = deal_repository

    async def __call__(self, user: AuthenticatedUser, days: int = 30) -> DealsSummaryEntity:
        async with self._uow:
            count_by_status = await self._deal_repository.get_deals_count_by_status(
                user.organization_id
            )
            amount_by_status = await self._deal_repository.get_deals_amount_by_status(
                user.organization_id
            )
            new_deals_count = await self._deal_repository.get_new_deals_count(
                user.organization_id, days
            )
            won_average = await self._deal_repository.get_won_deals_average(
                user.organization_id
            )
            
            return DealsSummaryEntity(
                count_by_status=count_by_status,
                amount_by_status=amount_by_status,
                average_won_amount=won_average,
                new_deals_last_n_days=new_deals_count,
            )


class GetDealsFunnelUseCase:
    def __init__(self, uow: UnitOfWork, deal_repository: DealRepository):
        self._uow = uow
        self._deal_repository = deal_repository

    async def __call__(self, user: AuthenticatedUser) -> DealsFunnelEntity:
        async with self._uow:
            funnel_data = await self._deal_repository.get_deals_funnel_data(
                user.organization_id
            )
            
            stages_dict: dict[str, dict[str, int]] = {}
            stage_totals: dict[str, int] = {}
            
            for stage, status, count in funnel_data:
                if stage not in stages_dict:
                    stages_dict[stage] = {}
                    stage_totals[stage] = 0
                
                stages_dict[stage][status] = count
                stage_totals[stage] += count
            
            stages = []
            stage_order = ["qualification", "proposal", "negotiation", "closed"]
            prev_total = None
            
            for stage in stage_order:
                if stage in stages_dict:
                    conversion_rate = 0.0
                    if prev_total and prev_total > 0:
                        conversion_rate = (stage_totals[stage] / prev_total) * 100
                    
                    stages.append(
                        FunnelStageEntity(
                            stage=stage,
                            count_by_status=stages_dict[stage],
                            conversion_rate=round(conversion_rate, 2),
                        )
                    )
                    prev_total = stage_totals[stage]
            
            return DealsFunnelEntity(stages=stages)

