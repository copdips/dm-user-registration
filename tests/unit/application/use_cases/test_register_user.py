"""Unit tests for RegisterUserUseCase."""

import pytest

from app.application.dto.user_dto import RegisterUserRequest
from app.application.exceptions import UserAlreadyExistsError
from app.application.use_cases.register_user import RegisterUserUseCase
from app.domain import Email, Password, User, UserRegistered, VerificationCode
from tests.unit.fakes.fake_code_store import FakeCodeStore
from tests.unit.fakes.fake_event_publisher import FakeEventPublisher
from tests.unit.fakes.fake_user_repository import FakeUserRepository


class TestRegisterUserUseCase:
    """Tests for RegisterUserUseCase."""

    @pytest.fixture
    def use_case(
        self,
        user_repository: FakeUserRepository,
        code_store: FakeCodeStore,
        event_publisher: FakeEventPublisher,
    ) -> RegisterUserUseCase:
        return RegisterUserUseCase(
            user_repository=user_repository,
            code_store=code_store,
            event_publisher=event_publisher,
        )

    async def test_register_user_success(
        self,
        use_case: RegisterUserUseCase,
        register_request: RegisterUserRequest,
        email: Email,
    ) -> None:
        response = await use_case.execute(register_request)

        assert response.email == email
        assert response.user_id is not None
        assert "verification code" in response.message.lower()

    async def test_register_user_saves_to_repository(
        self,
        use_case: RegisterUserUseCase,
        user_repository: FakeUserRepository,
        register_request: RegisterUserRequest,
        email: Email,
    ) -> None:
        response = await use_case.execute(register_request)

        user = await user_repository.get_by_email(email)
        assert user is not None
        assert user.id == response.user_id

    async def test_register_user_stores_verification_code(
        self,
        use_case: RegisterUserUseCase,
        code_store: FakeCodeStore,
        register_request: RegisterUserRequest,
        email: Email,
    ) -> None:
        await use_case.execute(register_request)

        code = await code_store.get(email)
        assert isinstance(code, VerificationCode)

    async def test_register_user_publishes_event(
        self,
        use_case: RegisterUserUseCase,
        event_publisher: FakeEventPublisher,
        register_request: RegisterUserRequest,
    ) -> None:
        await use_case.execute(register_request)

        assert len(event_publisher.published_events) == 1
        event = event_publisher.published_events[0]
        assert isinstance(event, UserRegistered)
        assert event.email.value == "user@example.com"

    async def test_register_user_already_exists_raises_error(
        self,
        use_case: RegisterUserUseCase,
        user_repository: FakeUserRepository,
        email: Email,
        password: Password,
        register_request: RegisterUserRequest,
    ) -> None:
        duplicate_user = User.create(
            email=email,
            password=password,
        )
        await user_repository.save(duplicate_user)

        with pytest.raises(UserAlreadyExistsError):
            await use_case.execute(register_request)

    async def test_register_user_hashes_password(
        self,
        use_case: RegisterUserUseCase,
        user_repository: FakeUserRepository,
        register_request: RegisterUserRequest,
        email: Email,
    ) -> None:
        await use_case.execute(register_request)

        user = await user_repository.get_by_email(email)
        assert user is not None
        assert user.password.hashed_value != "securepassword123"
        assert user.verify_password("securepassword123") is True
