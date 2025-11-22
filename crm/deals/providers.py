from typing import Annotated
from dishka import Provider, Scope, provide, FromComponent

from deals.repositories import DealRepository
from contacts.repositories import ContactRepository
from activities.repositories import ActivityRepository
from deals.usecases import (
    CreateDealUseCase,
    GetDealUseCase,
    UpdateDealUseCase,
    DeleteDealUseCase,
    ListDealsUseCase,
)
from core.database.unit_of_work import UnitOfWork


class DealProvider(Provider):
    scope = Scope.REQUEST
    component = "deals"

    @provide
    def get_deal_repository(
        self, uow: Annotated[UnitOfWork, FromComponent("database")]
    ) -> DealRepository:
        return DealRepository(uow.session)

    @provide
    def get_create_deal_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
        contact_repository: Annotated[ContactRepository, FromComponent("contacts")],
    ) -> CreateDealUseCase:
        return CreateDealUseCase(uow, deal_repository, contact_repository)

    @provide
    def get_get_deal_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> GetDealUseCase:
        return GetDealUseCase(uow, deal_repository)

    @provide
    def get_update_deal_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
        activity_repository: Annotated[ActivityRepository, FromComponent("activities")],
    ) -> UpdateDealUseCase:
        return UpdateDealUseCase(uow, deal_repository, activity_repository)

    @provide
    def get_delete_deal_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> DeleteDealUseCase:
        return DeleteDealUseCase(uow, deal_repository)

    @provide
    def get_list_deals_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> ListDealsUseCase:
        return ListDealsUseCase(uow, deal_repository)

