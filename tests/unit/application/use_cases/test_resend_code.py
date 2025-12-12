"""Unit tests for ResendCodeUseCase"""

import pytest

from app.application.dto.user_dto import ResendCodeRequest
from app.application.exceptions import InvalidCredentialsError, UserNotFoundError
from app.application.use_cases.resend_code import ResendCodeUseCase
from app.domain import (
    Email,
    Password,
    User,
    UserNewVerificationCodeCreated,
    VerificationCode,
)
from tests.fakes.fake_code_store import FakeCodeStore
from tests.fakes.fake_event_publisher import FakeEventPublisher
from tests.fakes.fake_user_repository import FakeUserRepository


class TestResendCodeUseCase:
    """Tests for ResendCodeUseCase"""

    @pytest.fixture
    def use_case(
        self,
        user_repository: FakeUserRepository,
        code_store: FakeCodeStore,
        event_publisher: FakeEventPublisher,
    ) -> ResendCodeUseCase:
        return ResendCodeUseCase(
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

    async def test_resend_code_success(
        self,
        use_case: ResendCodeUseCase,
        resend_code_request: ResendCodeRequest,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        response = await use_case.execute(resend_code_request)

        assert response.email == resend_code_request.email
        assert "new verification code has been sent" in response.message.lower()

    async def test_resend_code_stores_new_code(
        self,
        use_case: ResendCodeUseCase,
        resend_code_request: ResendCodeRequest,
        code_store: FakeCodeStore,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        old_code = VerificationCode("0000")
        await code_store.save(resend_code_request.email, old_code)
        await use_case.execute(resend_code_request)
        code = await code_store.get(resend_code_request.email)

        assert isinstance(code, VerificationCode)
        assert old_code != code

    async def test_resend_code_publishes_event(
        self,
        use_case: ResendCodeUseCase,
        resend_code_request: ResendCodeRequest,
        event_publisher: FakeEventPublisher,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        await use_case.execute(resend_code_request)

        assert len(event_publisher.published_events) == 1
        event = event_publisher.published_events[0]
        assert isinstance(event, UserNewVerificationCodeCreated)
        assert event.email.value == "user@example.com"

    async def test_user_not_found_raises_error(
        self,
        use_case: ResendCodeUseCase,
        resend_code_request: ResendCodeRequest,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        request = ResendCodeRequest(
            email=Email("nonexistent@example.com"),
            password=resend_code_request.password,
        )

        with pytest.raises(UserNotFoundError):
            await use_case.execute(request)

    async def test_invalid_password_raises_error(
        self,
        use_case: ResendCodeUseCase,
        resend_code_request: ResendCodeRequest,
        registered_user: User,  # noqa: ARG002 Unused method argument
    ) -> None:
        request = ResendCodeRequest(
            email=resend_code_request.email,
            password="wrongpassword",  # noqa: S106 Possible hardcoded password
        )

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(request)
