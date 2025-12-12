import pytest

from app.application.dto.user_dto import (
    ActivateUserRequest,
    RegisterUserRequest,
    ResendCodeRequest,
)
from app.domain import Email, Password, VerificationCode
from tests.unit.fakes.fake_code_store import FakeCodeStore
from tests.unit.fakes.fake_event_publisher import FakeEventPublisher
from tests.unit.fakes.fake_user_repository import FakeUserRepository


@pytest.fixture
def code_store() -> FakeCodeStore:
    return FakeCodeStore()


@pytest.fixture
def event_publisher() -> FakeEventPublisher:
    return FakeEventPublisher()


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture(scope="module")
def email() -> Email:
    return Email("user@example.com")


@pytest.fixture(scope="module")
def password() -> str:
    return "securepassword123"


@pytest.fixture(scope="module")
def code() -> VerificationCode:
    return VerificationCode.generate()


@pytest.fixture(scope="module")
def register_request(email: Email, password: str) -> RegisterUserRequest:
    return RegisterUserRequest(email, Password.create(password))


@pytest.fixture(scope="module")
def activate_request(
    email: Email, password: str, code: VerificationCode
) -> ActivateUserRequest:
    return ActivateUserRequest(email, password, code)


@pytest.fixture(scope="module")
def resend_code_request(email: Email, password: str) -> ResendCodeRequest:
    return ResendCodeRequest(email, password)
