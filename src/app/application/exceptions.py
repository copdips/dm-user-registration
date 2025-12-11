"""Application layer exceptions."""


class ApplicationError(Exception):
    """Base class for application exceptions."""


class UserAlreadyExistsError(ApplicationError):
    """Raised when user with email already exists."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User already exists with email: {email}")
