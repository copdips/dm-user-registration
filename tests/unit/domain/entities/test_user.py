"""Unit tests for User entity."""

import pytest

from app.domain import Email, Password, User, UserActivated, UserId, UserRegistered
from app.domain.exceptions import UserAlreadyActiveError


class TestUserCreate:
    """Tests for User.create()."""

    def test_create_user(self) -> None:
        email = Email("user@example.com")
        password = Password.create("securepassword123")

        user = User.create(email=email, password=password)

        assert user.email == email
        assert user.password == password
        assert user.is_active is False
        assert isinstance(user.id, UserId)
        assert user.created_at is not None

    def test_create_emits_user_registered_event(self, make_user) -> None:
        user = make_user()
        events = user.collect_events()

        assert len(events) == 1
        assert isinstance(events[0], UserRegistered)
        assert events[0].user_id == user.id
        assert events[0].email == user.email


class TestUserActivate:
    """Tests for User.activate()."""

    def test_activate_user(self, make_user) -> None:
        user = make_user()
        user.collect_events()  # Clear creation event

        user.activate()

        assert user.is_active is True

    def test_activate_emits_user_activated_event(self, make_user) -> None:
        user = make_user()
        user.collect_events()  # Clear creation event

        user.activate()
        events = user.collect_events()

        assert len(events) == 1
        assert isinstance(events[0], UserActivated)
        assert events[0].user_id == user.id

    def test_activate_already_active_raises_error(self, make_user) -> None:
        user = make_user()
        user.activate()

        with pytest.raises(UserAlreadyActiveError, match="already active"):
            user.activate()


class TestUserVerifyPassword:
    """Tests for User.verify_password()."""

    @pytest.mark.parametrize(
        ("password", "verify_with", "expected"),
        [
            ("securepassword123", "securepassword123", True),
            ("securepassword123", "wrongpassword", False),
            ("securepassword123", "", False),
        ],
    )
    def test_verify_password(
        self, make_user, password: str, verify_with: str, *, expected: bool
    ) -> None:
        user = make_user(password_value=password)

        assert user.verify_password(verify_with) is expected


class TestUserEvents:
    """Tests for User event handling."""

    def test_collect_events_clears_events(self, make_user) -> None:
        user = make_user()

        events1 = user.collect_events()
        events2 = user.collect_events()

        assert len(events1) == 1
        assert len(events2) == 0

    def test_multiple_events_collected_in_order(self, make_user) -> None:
        user = make_user()
        user.activate()

        events = user.collect_events()

        assert isinstance(events[0], UserRegistered)
        assert isinstance(events[1], UserActivated)
