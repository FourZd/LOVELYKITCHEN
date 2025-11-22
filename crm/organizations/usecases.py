from uuid import UUID

from core.database.unit_of_work import UnitOfWork
from organizations.repositories import OrganizationRepository
from organizations.entities import OrganizationEntity


class GetUserOrganizationsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        organization_repository: OrganizationRepository,
    ):
        self._uow = uow
        self._organization_repository = organization_repository

    async def __call__(self, user_id: UUID) -> list[OrganizationEntity]:
        async with self._uow:
            return await self._organization_repository.get_user_organizations(user_id)

