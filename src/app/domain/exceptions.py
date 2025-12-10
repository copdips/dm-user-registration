"""Domain layer exceptions."""


class DomainError(Exception):
    """Base class for all domain exceptions."""


class InvalidEmailError(DomainError):
    """Raised when email format is invalid."""


class InvalidPasswordError(DomainError):
    """Raised when password is invalid."""


class InvalidUserIdError(DomainError):
    """Raised when user ID is invalid."""


class InvalidVerificationCodeError(DomainError):
    """Raised when verification code is invalid."""
