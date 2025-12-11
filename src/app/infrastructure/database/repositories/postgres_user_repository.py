"""postgres user repository implementation"""

import asyncpg

from app.domain import Email, User, UserId
from app.infrastructure.database.mappers.user_mapper import UserMapper
from app.infrastructure.database.models.user_model import UserModel


class PostgresUserRepository:
    """postgres user repository implementation"""

    def __init__(self, connection: asyncpg.Connection) -> None:
        self._conn: asyncpg.Connection = connection

    async def get_by_id(self, user_id: UserId) -> User | None:
        if row := await self._conn.fetchrow(
            """
            SELECT * FROM users WHERE id = $1
            """,
            user_id.value,
        ):
            return self._row_to_entity(row)
        return None

    async def get_by_email(self, email: Email) -> User | None:
        if row := await self._conn.fetchrow(
            """
            SELECT * FROM users WHERE email = $1
            """,
            email.value,
        ):
            return self._row_to_entity(row)
        return None

    async def save(self, user: User) -> None:
        model = UserMapper.to_model(user)
        await self._conn.execute(
            """
            INSERT INTO users (id, email, hashed_password, is_active, created_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                hashed_password = EXCLUDED.hashed_password,
                is_active = EXCLUDED.is_active
            """,
            model.id,
            model.email,
            model.hashed_password,
            model.is_active,
            model.created_at,
        )

    def _row_to_entity(self, row: asyncpg.Record) -> User:
        model = UserModel(
            id=row["id"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            is_active=row["is_active"],
            created_at=row["created_at"],
        )
        return UserMapper.to_entity(model)
