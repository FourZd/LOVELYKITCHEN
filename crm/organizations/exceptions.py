from core.exceptions import NotFoundException, ForbiddenException


class OrganizationNotFoundError(NotFoundException):
    def __init__(self, message: str = "error.organization.not_found"):
        super().__init__(message)


class OrganizationAccessDeniedError(ForbiddenException):
    def __init__(self, message: str = "error.organization.access_denied"):
        super().__init__(message)

