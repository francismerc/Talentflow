from uuid import UUID

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user, get_gmail_service
from app.main import app
from app.schemas.auth import AuthenticatedUser
from app.schemas.gmail import (
    GmailAuthorization,
    GmailConnection,
    GmailProcessResult,
)

USER_ID = UUID("90000000-0000-4000-8000-000000000001")


class FakeGmailService:
    def __init__(self) -> None:
        self.disconnected_user_id: UUID | None = None

    async def get_connection(self, _: UUID) -> GmailConnection:
        return GmailConnection(
            oauth_configured=True,
            connected=True,
            gmail_address="recruitment@example.com",
            scopes=["https://www.googleapis.com/auth/gmail.modify"],
            status="connected",
        )

    def create_authorization(self, _: UUID) -> GmailAuthorization:
        return GmailAuthorization(
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth?state=signed"
        )

    async def complete_oauth(self, _: str, __: str) -> UUID:
        return USER_ID

    async def disconnect(self, user_id: UUID) -> None:
        self.disconnected_user_id = user_id

    async def process_inbox(
        self,
        _: UUID,
        *,
        max_messages: int,
    ) -> GmailProcessResult:
        return GmailProcessResult(
            messages_scanned=2,
            messages_processed=1,
            attachments_stored=1,
            duplicates_skipped=1,
        )

    async def update_settings(
        self,
        _: UUID,
        *,
        send_acknowledgment_emails: bool,
    ) -> GmailConnection:
        return GmailConnection(
            oauth_configured=True,
            connected=True,
            gmail_address="recruitment@example.com",
            scopes=["https://www.googleapis.com/auth/gmail.modify"],
            status="connected",
            send_acknowledgment_emails=send_acknowledgment_emails,
        )


fake_service = FakeGmailService()


def get_fake_gmail_service() -> FakeGmailService:
    return fake_service


def get_fake_current_user() -> AuthenticatedUser:
    return AuthenticatedUser(id=USER_ID, email="recruiter@example.com")


app.dependency_overrides[get_gmail_service] = get_fake_gmail_service
app.dependency_overrides[get_current_user] = get_fake_current_user
client = TestClient(app)


def test_get_gmail_status_returns_safe_connection_metadata() -> None:
    response = client.get("/api/v1/gmail/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["connected"] is True
    assert payload["data"]["gmail_address"] == "recruitment@example.com"
    assert "access_token" not in response.text
    assert "refresh_token" not in response.text


def test_create_gmail_authorization_url() -> None:
    response = client.get("/api/v1/gmail/oauth/authorize")

    assert response.status_code == 200
    assert response.json()["data"]["authorization_url"].startswith(
        "https://accounts.google.com/"
    )


def test_disconnect_gmail_connection() -> None:
    response = client.delete("/api/v1/gmail/connection")

    assert response.status_code == 200
    assert fake_service.disconnected_user_id == USER_ID


def test_gmail_status_requires_authentication() -> None:
    override = app.dependency_overrides.pop(get_current_user)
    try:
        response = client.get("/api/v1/gmail/status")
    finally:
        app.dependency_overrides[get_current_user] = override

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication is required."


def test_oauth_callback_redirects_to_settings() -> None:
    response = client.get(
        "/api/v1/gmail/oauth/callback?code=code&state=state",
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"] == "http://localhost:3000/settings?gmail=connected"


def test_process_gmail_inbox_returns_batch_summary() -> None:
    response = client.post("/api/v1/gmail/process", json={"max_messages": 25})

    assert response.status_code == 200
    assert response.json()["data"] == {
        "messages_scanned": 2,
        "messages_processed": 1,
        "attachments_stored": 1,
        "duplicates_skipped": 1,
        "unsupported_skipped": 0,
        "errors": 0,
    }


def test_update_gmail_settings_enables_acknowledgments() -> None:
    response = client.patch(
        "/api/v1/gmail/settings",
        json={"send_acknowledgment_emails": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["send_acknowledgment_emails"] is True
