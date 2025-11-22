from typing import Annotated
from dishka import Provider, Scope, provide, FromComponent

from users.repositories import UserRepository
from core.database.unit_of_work import UnitOfWork


class UserProvider(Provider):
    scope = Scope.REQUEST
    component = "users"

    @provide
    def get_user_repository(
        self, uow: Annotated[UnitOfWork, FromComponent("database")]
    ) -> UserRepository:
        return UserRepository(uow.session)

