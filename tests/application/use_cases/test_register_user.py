"""Unit tests for RegisterUserUseCase."""

import pytest

from app.application.dto.user_dto import RegisterUserRequest
from app.application.exceptions import UserAlreadyExistsError
from app.application.use_cases.register_user import RegisterUserUseCase
from app.domain import Email, Password, User, UserRegistered, VerificationCode
from tests.fakes.fake_code_store import FakeCodeStore
from tests.fakes.fake_event_publisher import FakeEventPublisher
from tests.fakes.fake_user_repository import FakeUserRepository


class TestRegisterUserUseCase:
    """Tests for RegisterUserUseCase."""

    @pytest.fixture
    def code_store(self) -> FakeCodeStore:
        return FakeCodeStore()

    @pytest.fixture
    def event_publisher(self) -> FakeEventPublisher:
        return FakeEventPublisher()

    @pytest.fixture
    def user_repository(self) -> FakeUserRepository:
        return FakeUserRepository()

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
    ) -> None:
        request = RegisterUserRequest(
            Email("user@example.com"),
            Password.create("securepassword123"),
        )

        response = await use_case.execute(request)

        assert response.email == Email("user@example.com")
        assert response.user_id is not None
        assert "verification code" in response.message.lower()

    async def test_register_user_saves_to_repository(
        self,
        use_case: RegisterUserUseCase,
        user_repository: FakeUserRepository,
    ) -> None:
        request = RegisterUserRequest(
            Email("user@example.com"),
            Password.create("securepassword123"),
        )

        response = await use_case.execute(request)

        user = await user_repository.get_by_email(Email("user@example.com"))
        assert user is not None
        assert user.id == response.user_id

    async def test_register_user_stores_verification_code(
        self,
        use_case: RegisterUserUseCase,
        code_store: FakeCodeStore,
    ) -> None:
        request = RegisterUserRequest(
            Email("user@example.com"),
            Password.create("securepassword123"),
        )

        await use_case.execute(request)

        code = await code_store.get(Email("user@example.com"))
        assert isinstance(code, VerificationCode)

    async def test_register_user_publishes_event(
        self,
        use_case: RegisterUserUseCase,
        event_publisher: FakeEventPublisher,
    ) -> None:
        request = RegisterUserRequest(
            Email("user@example.com"),
            Password.create("securepassword123"),
        )

        await use_case.execute(request)

        assert len(event_publisher.published_events) == 1
        event = event_publisher.published_events[0]
        assert isinstance(event, UserRegistered)
        assert event.email.value == "user@example.com"

    async def test_register_user_already_exists_raises_error(
        self,
        use_case: RegisterUserUseCase,
        user_repository: FakeUserRepository,
    ) -> None:
        duplicate_user = User.create(
            email=Email("user@example.com"),
            password=Password.create("securepassword123"),
        )
        await user_repository.save(duplicate_user)

        request = RegisterUserRequest(
            Email("user@example.com"),
            Password.create("securepassword123"),
        )

        with pytest.raises(UserAlreadyExistsError):
            await use_case.execute(request)

    async def test_register_user_hashes_password(
        self,
        use_case: RegisterUserUseCase,
        user_repository: FakeUserRepository,
    ) -> None:
        request = RegisterUserRequest(
            Email("user@example.com"),
            Password.create("securepassword123"),
        )

        await use_case.execute(request)

        user = await user_repository.get_by_email(Email("user@example.com"))
        assert user is not None
        assert user.password.hashed_value != "securepassword123"
        assert user.verify_password("securepassword123") is True
