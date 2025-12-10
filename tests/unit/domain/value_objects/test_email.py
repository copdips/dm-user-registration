"""Unit tests for Email value object."""

import pytest

from app.domain.exceptions import InvalidEmailError
from app.domain.value_objects.email import Email


class TestEmail:
    """Tests for Email value object."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("user@example.com", "user@example.com"),
            ("User@EXAMPLE.COM", "user@example.com"),
            ("  user@example.com  ", "user@example.com"),
            ("simple@example.com", "simple@example.com"),
            ("very.common@example.com", "very.common@example.com"),
            (
                "disposable.style.email.with+symbol@example.com",
                "disposable.style.email.with+symbol@example.com",
            ),
            (
                "other.email-with-hyphen@example.com",
                "other.email-with-hyphen@example.com",
            ),
            (
                "fully-qualified-domain@example.com",
                "fully-qualified-domain@example.com",
            ),
            ("user.name+tag+sorting@example.com", "user.name+tag+sorting@example.com"),
            ("x@example.com", "x@example.com"),
            ("user@subdomain.example.com", "user@subdomain.example.com"),
            ("user@sub.domain.example.com", "user@sub.domain.example.com"),
        ],
    )
    def test_valid_emails_normalize_lower(self, raw: str, expected: str) -> None:
        email = Email(raw)
        assert email.value == expected

    @pytest.mark.parametrize(
        ("raw", "message"),
        [
            ("", "cannot be empty"),
            ("   ", "cannot be empty"),
            ("toto.com", "Invalid email format"),
            ("user@", "Invalid email format"),
            ("@example.com", "Invalid email format"),
            ("user@example", "Invalid email format"),
            ("user@example.c", "Invalid email format"),
        ],
    )
    def test_invalid_emails_raise(self, raw: str, message: str) -> None:
        with pytest.raises(InvalidEmailError, match=message):
            Email(raw)

    def test_email_is_immutable(self) -> None:
        email = Email("user@example.com")
        with pytest.raises(AttributeError):
            email.value = "other@example.com"  # type: ignore[misc]

    def test_email_equality(self) -> None:
        email1 = Email("user@example.com")
        email2 = Email("USER@example.com")  # Different case
        assert email1 == email2  # Should be equal after normalization

    def test_email_hash(self) -> None:
        email1 = Email("user@example.com")
        email2 = Email("USER@example.com")
        # Same hash for equal emails
        assert hash(email1) == hash(email2)
        # Can be used in sets
        email_set = {email1, email2}
        assert len(email_set) == 1
