"""API dependencies"""

from app.application.use_cases.activate_user import ActivateUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.resend_code import ResendCodeUseCase
from app.container import container


def register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repository=container.user_repository(),
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )


def activate_user_use_case() -> ActivateUserUseCase:
    return ActivateUserUseCase(
        user_repository=container.user_repository(),
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )


def resend_code_use_case() -> ResendCodeUseCase:
    return ResendCodeUseCase(
        user_repository=container.user_repository(),
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )
