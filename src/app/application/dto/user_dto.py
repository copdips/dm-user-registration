"""User DTOs for application layer."""

from dataclasses import dataclass

from app.domain import Email, Password, UserId, VerificationCode


@dataclass(frozen=True, slots=True)
class RegisterUserRequest:
    """Request DTO for user registration."""

    email: Email
    password: Password


@dataclass(frozen=True, slots=True)
class RegisterUserResponse:
    """Response DTO for user registration."""

    user_id: UserId
    email: Email
    message: str


@dataclass(frozen=True, slots=True)
class ActivateUserRequest:
    """Request DTO for user activation"""

    email: Email
    password: str
    code: VerificationCode


@dataclass(frozen=True, slots=True)
class ActivateUserResponse:
    """Response DTO for user activation"""

    user_id: UserId
    email: Email
    is_active: bool


@dataclass(frozen=True, slots=True)
class ResendCodeRequest:
    """Request DTO for resending verification code"""

    email: Email
    password: str


@dataclass(frozen=True, slots=True)
class ResendCodeResponse:
    """Response DTO for resending verification code"""

    email: Email
    message: str
