from fastapi import status
from httpx import AsyncClient

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "toto1234"  # noqa: S105 Possible hardcoded password


async def test_register_user_success(
    async_client: AsyncClient,
) -> None:
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    }
    response = await async_client.post("/v1/users/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == TEST_EMAIL
