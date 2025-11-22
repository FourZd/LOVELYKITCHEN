from typing import Annotated
from dishka import Provider, Scope, provide, FromComponent

from analytics.usecases import GetDealsSummaryUseCase, GetDealsFunnelUseCase
from deals.repositories import DealRepository
from core.database.unit_of_work import UnitOfWork


class AnalyticsProvider(Provider):
    scope = Scope.REQUEST
    component = "analytics"

    @provide
    def get_deals_summary_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> GetDealsSummaryUseCase:
        return GetDealsSummaryUseCase(uow, deal_repository)

    @provide
    def get_deals_funnel_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> GetDealsFunnelUseCase:
        return GetDealsFunnelUseCase(uow, deal_repository)

