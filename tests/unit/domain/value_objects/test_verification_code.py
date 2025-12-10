"""Unit tests for VerificationCode value object."""

import pytest

from app.domain.exceptions import InvalidVerificationCodeError
from app.domain.value_objects.verification_code import _CODE_LENGTH, VerificationCode


class TestVerificationCodeValid:
    """Tests for valid verification code creation."""

    @pytest.mark.parametrize(
        "code",
        [
            "0000",
            "1234",
            "9999",
            "0001",
        ],
    )
    def test_valid_code(self, code: str) -> None:
        vc = VerificationCode(code)
        assert vc.value == code


class TestVerificationCodeInvalid:
    """Tests for invalid verification code rejection."""

    @pytest.mark.parametrize(
        ("code", "error_match"),
        [
            ("", "cannot be empty"),
            ("abc4", "must be numeric"),
            ("12.4", "must be numeric"),
            ("123", "must be 4 digits"),
            ("12345", "must be 4 digits"),
            ("12", "must be 4 digits"),
        ],
    )
    def test_invalid_code(self, code: str, error_match: str) -> None:
        with pytest.raises(InvalidVerificationCodeError, match=error_match):
            VerificationCode(code)


class TestVerificationCodeGenerate:
    """Tests for VerificationCode.generate()."""

    def test_generate_creates_4_digit_code(self) -> None:
        vc = VerificationCode.generate()
        assert len(vc.value) == _CODE_LENGTH
        assert vc.value.isdigit()

    def test_generate_creates_varied_codes(self) -> None:
        """Generate should produce different codes (not always 0000)."""
        codes = {VerificationCode.generate().value for _ in range(100)}
        assert len(codes) > 1  # At least some variation


class TestVerificationCodeMatches:
    """Tests for VerificationCode.matches()."""

    @pytest.mark.parametrize(
        ("code", "check", "expected"),
        [
            ("1234", "1234", True),
            ("1234", "4321", False),
            ("1234", "123", False),
            ("1234", "12345", False),
            ("1234", "", False),
            ("0000", "0000", True),
        ],
    )
    def test_matches(self, code: str, check: str, *, expected: bool) -> None:
        vc = VerificationCode(code)
        assert vc.matches(check) is expected


class TestVerificationCodeBehavior:
    """Tests for VerificationCode value object behavior."""

    def test_immutable(self) -> None:
        vc = VerificationCode("1234")
        with pytest.raises(AttributeError):
            vc.value = "5678"  # type: ignore[misc]

    def test_equality(self) -> None:
        vc1 = VerificationCode("1234")
        vc2 = VerificationCode("1234")
        assert vc1 == vc2

    def test_hashable(self) -> None:
        vc1 = VerificationCode("1234")
        vc2 = VerificationCode("1234")
        assert hash(vc1) == hash(vc2)
        assert len({vc1, vc2}) == 1
