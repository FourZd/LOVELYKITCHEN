from typing import Annotated
from dishka import Provider, Scope, provide, FromComponent

from activities.repositories import ActivityRepository
from deals.repositories import DealRepository
from activities.usecases import CreateActivityUseCase, ListActivitiesUseCase
from core.database.unit_of_work import UnitOfWork


class ActivityProvider(Provider):
    scope = Scope.REQUEST
    component = "activities"

    @provide
    def get_activity_repository(
        self, uow: Annotated[UnitOfWork, FromComponent("database")]
    ) -> ActivityRepository:
        return ActivityRepository(uow.session)

    @provide
    def get_create_activity_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        activity_repository: Annotated[ActivityRepository, FromComponent("activities")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> CreateActivityUseCase:
        return CreateActivityUseCase(uow, activity_repository, deal_repository)

    @provide
    def get_list_activities_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        activity_repository: Annotated[ActivityRepository, FromComponent("activities")],
        deal_repository: Annotated[DealRepository, FromComponent("deals")],
    ) -> ListActivitiesUseCase:
        return ListActivitiesUseCase(uow, activity_repository, deal_repository)

