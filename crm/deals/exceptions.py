from core.exceptions import NotFoundException, ForbiddenException, BadRequestException


class DealNotFoundError(NotFoundException):
    def __init__(self, message: str = "error.deal.not_found"):
        super().__init__(message)


class DealAccessDeniedError(ForbiddenException):
    def __init__(self, message: str = "error.deal.access_denied"):
        super().__init__(message)


class InvalidDealStatusError(BadRequestException):
    def __init__(self, message: str = "error.deal.invalid_status"):
        super().__init__(message)


class InvalidDealAmountError(BadRequestException):
    def __init__(self, message: str = "error.deal.invalid_amount"):
        super().__init__(message)


class InvalidStageTransitionError(BadRequestException):
    def __init__(self, message: str = "error.deal.invalid_stage_transition"):
        super().__init__(message)

