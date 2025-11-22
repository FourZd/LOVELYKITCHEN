from uuid import UUID

from core.database.unit_of_work import UnitOfWork
from users.repositories import UserRepository
from users.entities import UserEntity
from users.exceptions import UserNotFoundError


class GetCurrentUserUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        user_repository: UserRepository,
    ):
        self._uow = uow
        self._user_repository = user_repository

    async def __call__(self, user_id: UUID) -> UserEntity:
        async with self._uow:
            user = await self._user_repository.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError()
            return user

