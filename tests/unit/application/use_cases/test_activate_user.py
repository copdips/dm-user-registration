"""Unit tests for ActivateUserUseCase"""

import pytest

from app.application.dto.user_dto import ActivateUserRequest
from app.application.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    VerificationCodeExpiredError,
    VerificationCodeInvalidError,
)
from app.application.use_cases.activate_user import ActivateUserUseCase
from app.domain import Email, Password, User, UserActivated, VerificationCode
from tests.fakes.fake_code_store import FakeCodeStore
from tests.fakes.fake_event_publisher import FakeEventPublisher
from tests.fakes.fake_user_repository import FakeUserRepository


class TestActivateUserUseCase:
    """Tests for ActivateUserUseCase"""

    @pytest.fixture
    def use_case(
        self,
        user_repository: FakeUserRepository,
        code_store: FakeCodeStore,
        event_publisher: FakeEventPublisher,
    ) -> ActivateUserUseCase:
        return ActivateUserUseCase(
            user_repository=user_repository,
            code_store=code_store,
            event_publisher=event_publisher,
        )

    @pytest.fixture
    async def registered_user(
        self,
        user_repository: FakeUserRepository,
        code_store: FakeCodeStore,
        code: VerificationCode,
    ) -> User:
        """Create a registered but not activated user"""
        user = User.create(
            email=Email("user@example.com"),
            password=Password.create("securepassword123"),
        )
        await code_store.save(user.email, code)
        user.collect_events()  # Clear creation event
        await user_repository.save(user)
        return user

    async def test_activate_user_success(
        self,
        use_case: ActivateUserUseCase,
        activate_request: ActivateUserRequest,
        registered_user: User,
    ) -> None:
        response = await use_case.execute(activate_request)

        assert response.email == activate_request.email
        assert response.is_active is True
        assert response.user_id == registered_user.id

    async def test_activate_user_updates_user_state(
        self,
        use_case: ActivateUserUseCase,
        activate_request: ActivateUserRequest,
        user_repository: FakeUserRepository,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        await use_case.execute(activate_request)
        user = await user_repository.get_by_email(activate_request.email)
        assert user is not None
        assert user.is_active is True

    async def test_activate_user_deletes_code(
        self,
        use_case: ActivateUserUseCase,
        activate_request: ActivateUserRequest,
        code_store: FakeCodeStore,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        await use_case.execute(activate_request)

        code = await code_store.get(activate_request.email)
        assert code is None

    async def test_activate_user_publishes_event(
        self,
        use_case: ActivateUserUseCase,
        activate_request: ActivateUserRequest,
        event_publisher: FakeEventPublisher,
        registered_user: User,
    ) -> None:
        await use_case.execute(activate_request)

        assert len(event_publisher.published_events) == 1
        event = event_publisher.published_events[0]
        assert isinstance(event, UserActivated)
        assert event.user_id == registered_user.id

    async def test_user_not_found_raises_error(
        self,
        use_case: ActivateUserUseCase,
        activate_request: ActivateUserRequest,
    ) -> None:
        request = ActivateUserRequest(
            email=Email("nonexistent@example.com"),
            password=activate_request.password,
            code=activate_request.code,
        )

        with pytest.raises(UserNotFoundError):
            await use_case.execute(request)

    async def test_invalid_password_raises_error(
        self,
        use_case: ActivateUserUseCase,
        activate_request: ActivateUserRequest,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        request = ActivateUserRequest(
            email=activate_request.email,
            password="wrongpassword",  # noqa: S106 Possible hardcoded password
            code=activate_request.code,
        )

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(request)

    async def test_expired_code_raises_error(
        self,
        use_case: ActivateUserUseCase,
        activate_request: ActivateUserRequest,
        code_store: FakeCodeStore,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        code_store.clear()

        with pytest.raises(VerificationCodeExpiredError):
            await use_case.execute(activate_request)

    async def test_invalid_code_raises_error(
        self,
        use_case: ActivateUserUseCase,
        activate_request: ActivateUserRequest,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        request = ActivateUserRequest(
            email=activate_request.email,
            password=activate_request.password,
            code=VerificationCode.generate(),
        )

        with pytest.raises(VerificationCodeInvalidError):
            await use_case.execute(request)
