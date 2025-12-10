"""Unit tests for Password value object."""

import pytest

from app.domain.exceptions import InvalidPasswordError
from app.domain.value_objects.password import Password


class TestPasswordCreate:
    """Tests for Password.create()."""

    @pytest.mark.parametrize(
        "plain_password",
        [
            "securepassword123",
            "12345678",  # Exactly min length
        ],
    )
    def test_valid_password(self, plain_password: str) -> None:
        password = Password.create(plain_password)
        assert password.hashed_value.startswith("$2b$")
        assert password.hashed_value != plain_password

    @pytest.mark.parametrize(
        ("plain_password", "error_match"),
        [
            ("", "cannot be empty"),
            ("short", "at least 8 characters"),
            ("1234567", "at least 8 characters"),  # 7 chars
        ],
    )
    def test_invalid_password(self, plain_password: str, error_match: str) -> None:
        with pytest.raises(InvalidPasswordError, match=error_match):
            Password.create(plain_password)


class TestPasswordVerify:
    """Tests for Password.verify()."""

    @pytest.mark.parametrize(
        ("plain_password", "verify_with", "expected"),
        [
            ("securepassword123", "securepassword123", True),
            ("securepassword123", "wrongpassword", False),
            ("securepassword123", "", False),
            ("securepassword123", "securepassword12", False),  # Off by one
        ],
    )
    def test_verify(
        self, plain_password: str, verify_with: str, *, expected: bool
    ) -> None:
        password = Password.create(plain_password)
        assert password.verify(verify_with) is expected


class TestPasswordFromHash:
    """Tests for Password.from_hash()."""

    def test_from_hash_valid(self) -> None:
        original = Password.create("securepassword123")
        restored = Password.from_hash(original.hashed_value)
        assert restored.verify("securepassword123") is True

    def test_from_hash_empty_raises_error(self) -> None:
        with pytest.raises(InvalidPasswordError, match="cannot be empty"):
            Password.from_hash("")


class TestPasswordBehavior:
    """Tests for Password value object behavior."""

    def test_same_password_different_hashes(self) -> None:
        """Each hash should be unique due to random salt."""
        password1 = Password.create("securepassword123")
        password2 = Password.create("securepassword123")
        assert password1.hashed_value != password2.hashed_value

    def test_immutable(self) -> None:
        password = Password.create("securepassword123")
        with pytest.raises(AttributeError):
            password.hashed_value = "toto"  # ty: ignore[invalid-assignment]
