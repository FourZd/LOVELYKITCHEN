from typing import Annotated
from fastapi import APIRouter, Header
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from auth.schemas import RegisterRequest, LoginRequest, LoginResponse, TokenResponse
from auth.usecases import RegisterUseCase, LoginUseCase


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
    request: LoginRequest,
    x_organization_id: Annotated[str, Header(alias="X-Organization-Id")],
    login_usecase: Annotated[LoginUseCase, FromComponent("auth")],
):
    tokens = await login_usecase(request.email, request.password, x_organization_id)
    return LoginResponse(data=TokenResponse(**tokens.model_dump()))

