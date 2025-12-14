"""API dependencies"""

from app.application.use_cases.activate_user import ActivateUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.resend_code import ResendCodeUseCase
from app.container import container


def register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        uow=container.uow(),
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )


def activate_user_use_case() -> ActivateUserUseCase:
    return ActivateUserUseCase(
        uow=container.uow(),
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )


def resend_code_use_case() -> ResendCodeUseCase:
    return ResendCodeUseCase(
        uow=container.uow(),
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )
