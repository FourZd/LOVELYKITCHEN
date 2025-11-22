from core.exceptions import ConflictException, NotFoundException, ForbiddenException


class UserAlreadyExistsError(ConflictException):
    def __init__(self, message: str = "error.user.already_exists"):
        super().__init__(message)


class UserNotFoundError(NotFoundException):
    def __init__(self, message: str = "error.user.not_found"):
        super().__init__(message)


class InsufficientPermissionsError(ForbiddenException):
    def __init__(self, message: str = "error.user.insufficient_permissions"):
        super().__init__(message)

