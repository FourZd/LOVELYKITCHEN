from abc import ABC


class BaseCustomException(Exception, ABC):
    def __init__(self, message: str | None = None):
        self.message = message or self.get_default_message()
        super().__init__(self.message)
    
    def get_default_message(self) -> str:
        return "error.unknown"
    
    def get_status_code(self) -> int:
        return 500


class BadRequestException(BaseCustomException):
    def get_status_code(self) -> int:
        return 400


class AuthorizationException(BaseCustomException):
    def get_status_code(self) -> int:
        return 401


class ForbiddenException(BaseCustomException):
    def get_status_code(self) -> int:
        return 403


class NotFoundException(BaseCustomException):
    def get_status_code(self) -> int:
        return 404


class ConflictException(BaseCustomException):
    def get_status_code(self) -> int:
        return 409


class ValidationException(BaseCustomException):
    def get_status_code(self) -> int:
        return 422

