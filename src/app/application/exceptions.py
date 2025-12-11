"""Application layer exceptions."""


class ApplicationError(Exception):
    """Base class for application exceptions."""


class UserAlreadyExistsError(ApplicationError):
    """Raised when user with email already exists."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User already exists with email: {email}")


class UserNotFoundError(ApplicationError):
    """Raised when user is not found"""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User not found: {email}")


class InvalidCredentialsError(ApplicationError):
    """Raised when credentials are invalid"""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Invalid credentials for user: {email}")


class VerificationCodeInvalidError(ApplicationError):
    """Raised when verification code is invalid"""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Verification code is invalid for user: {email}")


class VerificationCodeExpiredError(ApplicationError):
    """Raised when verification code has expired"""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Verification code has expired for user: {email}")
