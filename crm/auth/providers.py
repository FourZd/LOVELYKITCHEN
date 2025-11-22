from typing import Annotated
from fastapi import Request
from dishka import Provider, Scope, provide, FromComponent

from auth.usecases import RegisterUseCase, LoginUseCase
from auth.services import JWTBearer
from auth.entities import AuthenticatedUser
from users.repositories import UserRepository
from organizations.repositories import OrganizationRepository
from core.database.unit_of_work import UnitOfWork
from core.environment.config import Settings
from core.exceptions import AuthorizationException
from organizations.exceptions import OrganizationAccessDeniedError


class AuthProvider(Provider):
    scope = Scope.REQUEST
    component = "auth"

    @provide
    def get_jwt_bearer(self) -> JWTBearer:
        return JWTBearer()

    @provide
    def get_register_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        user_repository: Annotated[UserRepository, FromComponent("users")],
        organization_repository: Annotated[OrganizationRepository, FromComponent("organizations")],
        settings: Annotated[Settings, FromComponent("environment")],
    ) -> RegisterUseCase:
        return RegisterUseCase(uow, user_repository, organization_repository, settings)

    @provide
    def get_login_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        user_repository: Annotated[UserRepository, FromComponent("users")],
        settings: Annotated[Settings, FromComponent("environment")],
    ) -> LoginUseCase:
        return LoginUseCase(uow, user_repository, settings)

    @provide
    async def get_authenticated_user(
        self,
        request: Annotated[Request, FromComponent("")],
        user_repository: Annotated[UserRepository, FromComponent("users")],
        jwt_bearer: Annotated[JWTBearer, FromComponent("auth")],
        settings: Annotated[Settings, FromComponent("environment")],
    ) -> AuthenticatedUser:
        token = await jwt_bearer(request, settings)
        if not token:
            raise AuthorizationException("error.auth.token_not_provided")
        
        payload = jwt_bearer.decode_jwt(token, settings)
        if not payload:
            raise AuthorizationException("error.auth.token.invalid")
        
        org_id_header = request.headers.get("X-Organization-Id")
        if not org_id_header:
            raise AuthorizationException("error.auth.organization_id_not_provided")
        
        if payload.get("organization_id") != org_id_header:
            raise OrganizationAccessDeniedError()
        
        from uuid import UUID
        user = await user_repository.get_user_by_id(UUID(payload["id"]))
        if not user:
            raise AuthorizationException("error.auth.user.not_found")
        
        membership = await user_repository.get_user_membership(
            UUID(payload["id"]), UUID(org_id_header)
        )
        if not membership:
            raise OrganizationAccessDeniedError()
        
        return AuthenticatedUser(
            id=UUID(payload["id"]),
            email=payload["email"],
            organization_id=UUID(payload["organization_id"]),
            role=membership.role,
        )

