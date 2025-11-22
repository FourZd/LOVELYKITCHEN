from typing import Annotated
from dishka import Provider, Scope, provide, FromComponent

from organizations.repositories import OrganizationRepository
from users.repositories import UserRepository
from organizations.usecases import (
    GetUserOrganizationsUseCase,
    GetOrganizationMembersUseCase,
    AddOrganizationMemberUseCase,
    UpdateMemberRoleUseCase,
    RemoveOrganizationMemberUseCase,
)
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

    @provide
    def get_organization_members_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        organization_repository: Annotated[OrganizationRepository, FromComponent("organizations")],
    ) -> GetOrganizationMembersUseCase:
        return GetOrganizationMembersUseCase(uow, organization_repository)

    @provide
    def add_organization_member_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        organization_repository: Annotated[OrganizationRepository, FromComponent("organizations")],
        user_repository: Annotated[UserRepository, FromComponent("users")],
    ) -> AddOrganizationMemberUseCase:
        return AddOrganizationMemberUseCase(uow, organization_repository, user_repository)

    @provide
    def update_member_role_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        organization_repository: Annotated[OrganizationRepository, FromComponent("organizations")],
    ) -> UpdateMemberRoleUseCase:
        return UpdateMemberRoleUseCase(uow, organization_repository)

    @provide
    def remove_organization_member_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        organization_repository: Annotated[OrganizationRepository, FromComponent("organizations")],
    ) -> RemoveOrganizationMemberUseCase:
        return RemoveOrganizationMemberUseCase(uow, organization_repository)

