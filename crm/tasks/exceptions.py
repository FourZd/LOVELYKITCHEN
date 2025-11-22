from core.exceptions import NotFoundException, ForbiddenException, BadRequestException


class TaskNotFoundError(NotFoundException):
    def __init__(self, message: str = "error.task.not_found"):
        super().__init__(message)


class TaskAccessDeniedError(ForbiddenException):
    def __init__(self, message: str = "error.task.access_denied"):
        super().__init__(message)


class InvalidDueDateError(BadRequestException):
    def __init__(self, message: str = "error.task.invalid_due_date"):
        super().__init__(message)

