"""API dependencies"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.activate_user import ActivateUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.resend_code import ResendCodeUseCase
from app.container import container


async def register_user_use_case(
    uow: UnitOfWork = Depends(container.uow),
) -> AsyncGenerator[RegisterUserUseCase]:
    yield RegisterUserUseCase(
        uow=uow,
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )


async def activate_user_use_case(
    uow: UnitOfWork = Depends(container.uow),
) -> AsyncGenerator[ActivateUserUseCase]:
    yield ActivateUserUseCase(
        uow=uow,
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )


async def resend_code_use_case(
    uow: UnitOfWork = Depends(container.uow),
) -> AsyncGenerator[ResendCodeUseCase]:
    yield ResendCodeUseCase(
        uow=uow,
        code_store=container.code_store,
        event_publisher=container.event_publisher,
    )


RegisterUserUseCaseDep = Annotated[RegisterUserUseCase, Depends(register_user_use_case)]
ActivateUserUseCaseDep = Annotated[ActivateUserUseCase, Depends(activate_user_use_case)]
ResendCodeUseCaseDep = Annotated[ResendCodeUseCase, Depends(resend_code_use_case)]
