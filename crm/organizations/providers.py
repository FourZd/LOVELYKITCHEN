from typing import Annotated
from dishka import Provider, Scope, provide, FromComponent

from organizations.repositories import OrganizationRepository
from organizations.usecases import GetUserOrganizationsUseCase
from core.database.unit_of_work import UnitOfWork


class OrganizationProvider(Provider):
    scope = Scope.REQUEST
    component = "organizations"

    @provide
    def get_organization_repository(
        self, uow: Annotated[UnitOfWork, FromComponent("database")]
    ) -> OrganizationRepository:
        return OrganizationRepository(uow.session)

    @provide
    def get_user_organizations_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        organization_repository: Annotated[OrganizationRepository, FromComponent("organizations")],
    ) -> GetUserOrganizationsUseCase:
        return GetUserOrganizationsUseCase(uow, organization_repository)

