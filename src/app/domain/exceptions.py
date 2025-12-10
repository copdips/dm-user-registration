"""Domain layer exceptions."""


class DomainError(Exception):
    """Base class for all domain exceptions."""


class InvalidEmailError(DomainError):
    """Raised when email format is invalid."""


class InvalidPasswordError(DomainError):
    """Raised when password is invalid."""
