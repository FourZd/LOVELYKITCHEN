from core.exceptions import AuthorizationException


class InvalidCredentialsError(AuthorizationException):
    def __init__(self, message: str = "error.auth.invalid_credentials"):
        super().__init__(message)


class InvalidTokenError(AuthorizationException):
    def __init__(self, message: str = "error.auth.invalid_token"):
        super().__init__(message)


class TokenExpiredError(AuthorizationException):
    def __init__(self, message: str = "error.auth.token_expired"):
        super().__init__(message)

