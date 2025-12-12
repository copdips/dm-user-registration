from unittest.mock import Mock

from fastapi import status
from httpx import AsyncClient

from app.domain import VerificationCode

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "toto1234"  # noqa: S105 Possible hardcoded password
TEST_VERIFICATION_CODE = "1234"


async def test_register_user_success(
    async_client: AsyncClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.domain.VerificationCode.generate",
        Mock(return_value=VerificationCode(TEST_VERIFICATION_CODE)),
    )
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    }
    response = await async_client.post("/v1/users/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == TEST_EMAIL
