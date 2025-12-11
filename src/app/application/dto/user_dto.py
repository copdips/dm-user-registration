"""User DTOs for application layer."""

from dataclasses import dataclass

from app.domain import Email, Password, UserId


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
