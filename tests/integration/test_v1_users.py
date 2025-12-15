from unittest.mock import Mock

from fastapi import status
from httpx import AsyncClient, BasicAuth

from app.domain import VerificationCode

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "toto1234"  # noqa: S105 Possible hardcoded password
TEST_VERIFICATION_CODE_OLD = "1234"
TEST_VERIFICATION_CODE_NEW = "5678"

basic_auth = BasicAuth(TEST_EMAIL, TEST_PASSWORD)


async def test_register_user_success(
    async_client: AsyncClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.domain.VerificationCode.generate",
        Mock(return_value=VerificationCode(TEST_VERIFICATION_CODE_OLD)),
    )
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    }
    response = await async_client.post("/v1/users/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == TEST_EMAIL


async def test_resend_verification_code_success(
    async_client: AsyncClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.domain.VerificationCode.generate",
        Mock(return_value=VerificationCode(TEST_VERIFICATION_CODE_NEW)),
    )
    response = await async_client.post("/v1/users/resend-code", auth=basic_auth)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "New verification code has been sent" in data["message"]


async def test_activate_user_failed_with_old_code(
    async_client: AsyncClient,
) -> None:
    payload = {
        "code": TEST_VERIFICATION_CODE_OLD,
    }
    response = await async_client.post(
        "/v1/users/activate", json=payload, auth=basic_auth
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert f"Verification code is invalid for user: {TEST_EMAIL}" in data["message"]


async def test_activate_user_success_with_new_code(
    async_client: AsyncClient,
) -> None:
    payload = {
        "code": TEST_VERIFICATION_CODE_NEW,
    }
    response = await async_client.post(
        "/v1/users/activate", json=payload, auth=basic_auth
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Account activated successfully" in data["message"]
