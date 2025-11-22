from pydantic import BaseModel
from users.entities import UserEntity


class UserResponse(BaseModel):
    data: UserEntity

