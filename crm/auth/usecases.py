from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt

from core.database.unit_of_work import UnitOfWork
from core.environment.config import Settings
from users.repositories import UserRepository
from organizations.repositories import OrganizationRepository
from users.enums import UserRole
from auth.entities import TokenPair
from auth.exceptions import InvalidCredentialsError
from users.exceptions import UserAlreadyExistsError
from organizations.exceptions import OrganizationAccessDeniedError


class RegisterUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        user_repository: UserRepository,
        organization_repository: OrganizationRepository,
        settings: Settings,
    ):
        self._uow = uow
        self._user_repository = user_repository
        self._organization_repository = organization_repository
        self._settings = settings

    async def __call__(
        self, email: str, password: str, name: str, organization_name: str
    ) -> TokenPair:
        async with self._uow:
            existing_user = await self._user_repository.get_user_by_email(email)
            if existing_user:
                raise UserAlreadyExistsError()

            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            user_id = uuid4()
            user_data = {
                "id": user_id,
                "email": email,
                "hashed_password": hashed_password,
                "name": name,
                "created_at": datetime.now(timezone.utc),
            }

            user = await self._user_repository.create_user(user_data)

            org_id = uuid4()
            org_data = {
                "id": org_id,
                "name": organization_name,
                "created_at": datetime.now(timezone.utc),
            }
            await self._organization_repository.create(org_data)
            await self._organization_repository.add_member(
                org_id, user_id, UserRole.OWNER
            )

            access_expiration = datetime.now(timezone.utc) + timedelta(
                minutes=self._settings.access_token_lifetime
            )
            refresh_expiration = datetime.now(timezone.utc) + timedelta(
                minutes=self._settings.refresh_token_lifetime
            )

            access_payload = {
                "exp": access_expiration,
                "id": str(user.id),
                "email": user.email,
                "organization_id": str(org_id),
                "role": UserRole.OWNER.value,
            }

            refresh_payload = {
                "exp": refresh_expiration,
                "id": str(user.id),
            }

            access_token = jwt.encode(
                access_payload, self._settings.secret_key, algorithm=self._settings.jwt_algorithm
            )
            refresh_token = jwt.encode(
                refresh_payload, self._settings.secret_key, algorithm=self._settings.jwt_algorithm
            )

            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                access_expiration=int(access_expiration.timestamp()),
                refresh_expiration=int(refresh_expiration.timestamp()),
                organization_id=str(org_id),
            )


class LoginUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        user_repository: UserRepository,
        settings: Settings,
    ):
        self._uow = uow
        self._user_repository = user_repository
        self._settings = settings

    async def __call__(self, email: str, password: str, organization_id: str) -> TokenPair:
        async with self._uow:
            user = await self._user_repository.get_user_by_email(email, include_password=True)
            if not user:
                raise InvalidCredentialsError()

            if not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
                raise InvalidCredentialsError()

            membership = await self._user_repository.get_user_membership(
                user.id, UUID(organization_id)
            )
            if not membership:
                raise OrganizationAccessDeniedError()

            access_expiration = datetime.now(timezone.utc) + timedelta(
                minutes=self._settings.access_token_lifetime
            )
            refresh_expiration = datetime.now(timezone.utc) + timedelta(
                minutes=self._settings.refresh_token_lifetime
            )

            access_payload = {
                "exp": access_expiration,
                "id": str(user.id),
                "email": user.email,
                "organization_id": organization_id,
                "role": membership.role,
            }

            refresh_payload = {
                "exp": refresh_expiration,
                "id": str(user.id),
            }

            access_token = jwt.encode(
                access_payload, self._settings.secret_key, algorithm=self._settings.jwt_algorithm
            )
            refresh_token = jwt.encode(
                refresh_payload, self._settings.secret_key, algorithm=self._settings.jwt_algorithm
            )

            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                access_expiration=int(access_expiration.timestamp()),
                refresh_expiration=int(refresh_expiration.timestamp()),
                organization_id=organization_id,
            )

