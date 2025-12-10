"""Unit tests for UserId value object."""

from uuid import UUID

import pytest

from app.domain.exceptions import InvalidUserIdError
from app.domain.value_objects.user_id import UserId


class TestUserIdGenerate:
    """Tests for UserId.generate()."""

    def test_generate_creates_valid_uuid(self) -> None:
        user_id = UserId.generate()
        assert isinstance(user_id.value, UUID)

    def test_generate_creates_unique_ids(self) -> None:
        count = 1000
        ids = [UserId.generate() for _ in range(count)]
        unique_values = {uid.value for uid in ids}
        assert len(unique_values) == count


class TestUserIdFromString:
    """Tests for UserId.from_string()."""

    @pytest.mark.parametrize(
        "uuid_string",
        [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "00000000-0000-0000-0000-000000000000",
        ],
    )
    def test_from_string_valid(self, uuid_string: str) -> None:
        user_id = UserId.from_string(uuid_string)
        assert str(user_id.value) == uuid_string

    @pytest.mark.parametrize(
        "invalid_string",
        [
            "",
            "not-a-uuid",
            "550e8400-e29b-41d4-a716",  # Incomplete
        ],
    )
    def test_from_string_invalid(self, invalid_string: str) -> None:
        with pytest.raises(InvalidUserIdError):
            UserId.from_string(invalid_string)


class TestUserIdBehavior:
    """Tests for UserId value object behavior."""

    def test_immutable(self) -> None:
        user_id = UserId.generate()
        with pytest.raises(AttributeError):
            user_id.value = UUID("550e8400-e29b-41d4-a716-446655440000")  # ty: ignore[invalid-assignment]

    def test_equality(self) -> None:
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        id1 = UserId.from_string(uuid_str)
        id2 = UserId.from_string(uuid_str)
        assert id1 == id2

    def test_hashable(self) -> None:
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        id1 = UserId.from_string(uuid_str)
        id2 = UserId.from_string(uuid_str)
        assert hash(id1) == hash(id2)
        assert len({id1, id2}) == 1
