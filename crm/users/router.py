from typing import Annotated
from fastapi import APIRouter
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from users.schemas import UserResponse
from users.usecases import GetCurrentUserUseCase
from auth.entities import AuthenticatedUser


router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)


@router.get("/me", response_model=UserResponse)
@inject
async def get_current_user(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    get_user_usecase: Annotated[GetCurrentUserUseCase, FromComponent("users")],
):
    """Получить информацию о текущем пользователе"""
    user_info = await get_user_usecase(user.id)
    return UserResponse(data=user_info)

