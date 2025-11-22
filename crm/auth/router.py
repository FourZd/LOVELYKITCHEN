from typing import Annotated
from fastapi import APIRouter, Request
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from auth.schemas import RegisterRequest, LoginRequest, LoginResponse, TokenResponse
from auth.usecases import RegisterUseCase, LoginUseCase
from core.exceptions import AuthorizationException


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.post("/register", response_model=LoginResponse)
@inject
async def register(
    request: RegisterRequest,
    register_usecase: Annotated[RegisterUseCase, FromComponent("auth")],
):
    tokens = await register_usecase(
        request.email, request.password, request.name, request.organization_name
    )
    return LoginResponse(data=TokenResponse(**tokens.model_dump()))


@router.post("/login", response_model=LoginResponse)
@inject
async def login(
    request: Request,
    payload: LoginRequest,
    login_usecase: Annotated[LoginUseCase, FromComponent("auth")],
):
    x_organization_id = request.headers.get("X-Organization-Id")
    if not x_organization_id:
        raise AuthorizationException("error.auth.organization_id_not_provided")
    tokens = await login_usecase(payload.email, payload.password, x_organization_id)
    return LoginResponse(data=TokenResponse(**tokens.model_dump()))

