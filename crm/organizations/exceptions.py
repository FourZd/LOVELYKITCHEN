from core.exceptions import NotFoundException, ForbiddenException, ConflictException, BadRequestException


class OrganizationNotFoundError(NotFoundException):
    def __init__(self, message: str = "error.organization.not_found"):
        super().__init__(message)


class OrganizationAccessDeniedError(ForbiddenException):
    def __init__(self, message: str = "error.organization.access_denied"):
        super().__init__(message)


class MemberNotFoundError(NotFoundException):
    def __init__(self, message: str = "error.organization.member_not_found"):
        super().__init__(message)


class MemberAlreadyExistsError(ConflictException):
    def __init__(self, message: str = "error.organization.member_already_exists"):
        super().__init__(message)


class CannotRemoveLastOwnerError(BadRequestException):
    def __init__(self, message: str = "error.organization.cannot_remove_last_owner"):
        super().__init__(message)


class InsufficientPermissionsError(ForbiddenException):
    def __init__(self, message: str = "error.organization.insufficient_permissions"):
        super().__init__(message)

