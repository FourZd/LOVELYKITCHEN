from core.exceptions import NotFoundException, ForbiddenException


class ActivityNotFoundError(NotFoundException):
    def __init__(self, message: str = "error.activity.not_found"):
        super().__init__(message)


class ActivityAccessDeniedError(ForbiddenException):
    def __init__(self, message: str = "error.activity.access_denied"):
        super().__init__(message)

