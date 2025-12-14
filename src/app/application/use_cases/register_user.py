"""Register user use case."""

from app.application.dto.user_dto import RegisterUserRequest, RegisterUserResponse
from app.application.exceptions import UserAlreadyExistsError
from app.application.ports.code_store import CodeStore
from app.application.ports.event_publisher import EventPublisher
from app.application.ports.unit_of_work import UnitOfWork
from app.domain import User, VerificationCode


class RegisterUserUseCase:
    """
    Use Case: Register a new user.

    - Creates user with email and password
    - Generates verification code
    - Stores code with TTL
    - Publishes UserRegistered event
    """

    def __init__(
        self,
        uow: UnitOfWork,
        code_store: CodeStore,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow: UnitOfWork = uow
        self._code_store: CodeStore = code_store
        self._event_publisher: EventPublisher = event_publisher

    async def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        email = request.email
        password = request.password

        async with self._uow:
            if await self._uow.user_repository.get_by_email(email):
                raise UserAlreadyExistsError(email.value)

            user = User.create(email=email, password=password)
            await self._uow.user_repository.save(user)
            code = VerificationCode.generate()
            await self._code_store.save(email, code)

            await self._event_publisher.publish_all(user.collect_events())

        return RegisterUserResponse(
            user_id=user.id,
            email=email,
            message="User registered. "
            "Please check your email for verification code to activate your account.",
        )
