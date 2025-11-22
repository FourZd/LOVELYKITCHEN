from typing import Optional
from fastapi import Request
import jwt

from core.environment.config import Settings
from auth.exceptions import InvalidTokenError, TokenExpiredError


class JWTBearer:
    async def __call__(self, request: Request, settings: Settings) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        if not authorization.startswith("Bearer "):
            return None
        
        return authorization[7:]
    
    def decode_jwt(self, token: str, settings: Settings) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

