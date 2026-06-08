from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import get_current_user

pytestmark = pytest.mark.anyio

USER_ID = UUID("90000000-0000-4000-8000-000000000001")


class FakeAuthApi:
    def __init__(self) -> None:
        self.token: str | None = None

    async def get_user(self, token: str) -> SimpleNamespace:
        self.token = token
        return SimpleNamespace(
            user=SimpleNamespace(
                id=USER_ID,
                email="recruiter@example.com",
            )
        )


class FakeAuthClient:
    def __init__(self) -> None:
        self.auth = FakeAuthApi()


async def test_current_user_uses_isolated_auth_client() -> None:
    auth_client = FakeAuthClient()
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="recruiter-token",
    )

    user = await get_current_user(credentials, auth_client)

    assert auth_client.auth.token == "recruiter-token"
    assert user.id == USER_ID
    assert user.email == "recruiter@example.com"
