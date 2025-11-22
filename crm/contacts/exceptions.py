from core.exceptions import NotFoundException, ForbiddenException, ConflictException


class ContactNotFoundError(NotFoundException):
    def __init__(self, message: str = "error.contact.not_found"):
        super().__init__(message)


class ContactAccessDeniedError(ForbiddenException):
    def __init__(self, message: str = "error.contact.access_denied"):
        super().__init__(message)


class ContactHasActiveDealsError(ConflictException):
    def __init__(self, message: str = "error.contact.has_active_deals"):
        super().__init__(message)

