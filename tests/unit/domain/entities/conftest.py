"""Shared fixtures for user entity tests."""

from collections.abc import Callable

import pytest

from app.domain import Email, Password, User


@pytest.fixture
def make_user() -> Callable[..., User]:
    """
    Factory fixture to create users with optional overrides.

    Allows tests to inject existing value objects or override defaults
    without repeating setup code.
    """

    def _make_user(
        *,
        email: Email | None = None,
        password: Password | None = None,
        email_value: str = "user@example.com",
        password_value: str = "securepassword123",  # noqa: S107 hardcoded-password-default
    ) -> User:
        email_obj = email or Email(email_value)
        password_obj = password or Password.create(password_value)
        return User.create(email=email_obj, password=password_obj)

    return _make_user
