import asyncio
import base64
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse
from uuid import UUID

from cryptography.fernet import Fernet
from pydantic import SecretStr

from app.core.config import Settings
from app.gmail.security import OAuthStateSigner, TokenCipher
from app.gmail.service import GMAIL_MODIFY_SCOPE, GmailService

USER_ID = UUID("90000000-0000-4000-8000-000000000001")
STATE_SECRET = "state-secret-that-is-long-enough-for-hmac-signing"
ENCRYPTION_KEY = Fernet.generate_key().decode("ascii")


class FakeGmailQueries:
    def __init__(self) -> None:
        self.record: dict[str, object] | None = None

    async def get_by_user_id(
        self,
        _: UUID,
        *,
        include_tokens: bool = False,
    ) -> dict[str, object] | None:
        return self.record

    async def upsert(self, values: dict[str, object]) -> dict[str, object]:
        self.record = values
        return values

    async def update(
        self,
        _: UUID,
        values: dict[str, object],
    ) -> dict[str, object]:
        self.record = {**(self.record or {}), **values}
        return self.record

    async def delete(self, _: UUID) -> bool:
        self.record = None
        return True


class FakeEmailLogs:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, object]] = {}

    async def get_incoming_by_gmail_message_id(
        self,
        message_id: str,
    ) -> dict[str, object] | None:
        return next(
            (
                record
                for record in self.records.values()
                if record.get("gmail_message_id") == message_id
            ),
            None,
        )

    async def create(self, values: dict[str, object]) -> dict[str, object]:
        record = {"id": "email-log-1", **values}
        self.records[str(record["id"])] = record
        return record

    async def update(
        self,
        email_log_id: str,
        values: dict[str, object],
    ) -> dict[str, object]:
        self.records[email_log_id].update(values)
        return self.records[email_log_id]

    async def delete(self, email_log_id: str) -> bool:
        return self.records.pop(email_log_id, None) is not None


class FakeEmailAttachments:
    def __init__(self) -> None:
        self.records: list[dict[str, object]] = []

    async def create(self, values: dict[str, object]) -> dict[str, object]:
        self.records.append(values)
        return values

    async def list_storage_paths(self, email_log_id: str) -> list[str]:
        return [
            str(record["storage_path"])
            for record in self.records
            if record["email_log_id"] == email_log_id
        ]


class FakeResumeStorage:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    async def upload(
        self,
        *,
        storage_path: str,
        content: bytes,
        mime_type: str,
    ) -> None:
        self.files[storage_path] = content

    async def remove(self, storage_path: str) -> None:
        self.files.pop(storage_path, None)


def make_settings() -> Settings:
    return Settings(
        google_client_id="client-id.apps.googleusercontent.com",
        google_client_secret=SecretStr("client-secret"),
        google_redirect_uri="http://localhost:8000/api/v1/gmail/oauth/callback",
        google_oauth_state_secret=SecretStr(STATE_SECRET),
        google_token_encryption_key=SecretStr(ENCRYPTION_KEY),
    )


def test_create_authorization_uses_secure_offline_flow() -> None:
    service = GmailService(FakeGmailQueries(), make_settings())

    result = service.create_authorization(USER_ID)
    params = parse_qs(urlparse(str(result.authorization_url)).query)

    assert params["scope"] == [GMAIL_MODIFY_SCOPE]
    assert params["access_type"] == ["offline"]
    assert params["prompt"] == ["consent"]
    assert params["redirect_uri"] == [
        "http://localhost:8000/api/v1/gmail/oauth/callback"
    ]
    state = OAuthStateSigner(STATE_SECRET).verify(params["state"][0])
    assert state.user_id == USER_ID


def test_complete_oauth_encrypts_tokens_before_storage(
    monkeypatch,
) -> None:
    queries = FakeGmailQueries()
    service = GmailService(queries, make_settings())
    state = OAuthStateSigner(STATE_SECRET).create(USER_ID)

    async def fake_exchange(_: str) -> dict[str, object]:
        return {
            "access_token": "plain-access-token",
            "refresh_token": "plain-refresh-token",
            "expires_in": 3600,
            "scope": GMAIL_MODIFY_SCOPE,
        }

    async def fake_profile(_: str) -> dict[str, object]:
        return {"emailAddress": "recruitment@example.com"}

    monkeypatch.setattr(service, "_exchange_code", fake_exchange)
    monkeypatch.setattr(service, "_get_profile", fake_profile)

    result = asyncio.run(service.complete_oauth("authorization-code", state))

    assert result == USER_ID
    assert queries.record is not None
    assert queries.record["encrypted_access_token"] != "plain-access-token"
    assert queries.record["encrypted_refresh_token"] != "plain-refresh-token"
    cipher = TokenCipher(ENCRYPTION_KEY)
    assert cipher.decrypt(str(queries.record["encrypted_access_token"])) == (
        "plain-access-token"
    )
    assert cipher.decrypt(str(queries.record["encrypted_refresh_token"])) == (
        "plain-refresh-token"
    )
    assert queries.record["status"] == "connected"
    assert datetime.fromisoformat(str(queries.record["token_expires_at"])) > datetime.now(
        UTC
    )


def test_parse_message_finds_supported_nested_resume_attachment() -> None:
    metadata = GmailService._parse_message(
        {
            "id": "message-1",
            "threadId": "thread-1",
            "internalDate": "1780886400000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Candidate <candidate@example.com>"},
                    {"name": "To", "value": "recruitment@example.com"},
                    {"name": "Subject", "value": "Frontend application"},
                ],
                "parts": [
                    {
                        "filename": "Francis Resume.pdf",
                        "mimeType": "application/pdf",
                        "body": {
                            "attachmentId": "attachment-1",
                            "size": 128,
                        },
                    },
                    {
                        "filename": "photo.png",
                        "mimeType": "image/png",
                        "body": {
                            "attachmentId": "attachment-2",
                            "size": 128,
                        },
                    },
                ],
            },
        },
        fallback_recipient="fallback@example.com",
    )

    assert metadata.sender_email == "candidate@example.com"
    assert metadata.subject == "Frontend application"
    assert len(metadata.attachments) == 1
    assert metadata.attachments[0].attachment_id == "attachment-1"


def test_process_inbox_stores_resume_and_marks_message_processed(
    monkeypatch,
) -> None:
    queries = FakeGmailQueries()
    cipher = TokenCipher(ENCRYPTION_KEY)
    queries.record = {
        "user_id": str(USER_ID),
        "gmail_address": "recruitment@example.com",
        "status": "connected",
        "encrypted_access_token": cipher.encrypt("access-token"),
        "encrypted_refresh_token": cipher.encrypt("refresh-token"),
        "token_expires_at": "2099-01-01T00:00:00+00:00",
    }
    email_logs = FakeEmailLogs()
    email_attachments = FakeEmailAttachments()
    storage = FakeResumeStorage()
    service = GmailService(
        queries,
        make_settings(),
        email_logs=email_logs,
        email_attachments=email_attachments,
        resume_storage=storage,
    )
    marked_read: list[str] = []

    async def fake_list(_: str, *, max_messages: int) -> list[str]:
        assert max_messages == 25
        return ["message-1"]

    async def fake_message(_: str, __: str) -> dict[str, object]:
        return {
            "id": "message-1",
            "threadId": "thread-1",
            "internalDate": "1780886400000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "candidate@example.com"},
                    {"name": "To", "value": "recruitment@example.com"},
                    {"name": "Subject", "value": "Application"},
                ],
                "parts": [
                    {
                        "filename": "resume.pdf",
                        "mimeType": "application/pdf",
                        "body": {"attachmentId": "attachment-1", "size": 7},
                    }
                ],
            },
        }

    async def fake_download(_: str, __: str, ___: str) -> bytes:
        return base64.b64decode(base64.b64encode(b"resume"))

    async def fake_mark(_: str, message_id: str) -> None:
        marked_read.append(message_id)

    monkeypatch.setattr(service, "_list_resume_message_ids", fake_list)
    monkeypatch.setattr(service, "_get_message", fake_message)
    monkeypatch.setattr(service, "_download_attachment", fake_download)
    monkeypatch.setattr(service, "_mark_as_read", fake_mark)

    result = asyncio.run(service.process_inbox(USER_ID))

    assert result.messages_scanned == 1
    assert result.messages_processed == 1
    assert result.attachments_stored == 1
    assert result.errors == 0
    assert marked_read == ["message-1"]
    assert email_logs.records["email-log-1"]["status"] == "processed"
    assert email_attachments.records[0]["mime_type"] == "application/pdf"
    assert next(iter(storage.files.values())) == b"resume"
    assert queries.record["last_synced_at"] is not None


def test_expired_access_token_is_refreshed_and_saved(monkeypatch) -> None:
    queries = FakeGmailQueries()
    cipher = TokenCipher(ENCRYPTION_KEY)
    queries.record = {
        "encrypted_access_token": cipher.encrypt("expired-token"),
        "encrypted_refresh_token": cipher.encrypt("refresh-token"),
        "token_expires_at": "2020-01-01T00:00:00+00:00",
    }
    service = GmailService(queries, make_settings())

    async def fake_refresh(refresh_token: str) -> dict[str, object]:
        assert refresh_token == "refresh-token"
        return {"access_token": "new-access-token", "expires_in": 3600}

    monkeypatch.setattr(service, "_refresh_access_token", fake_refresh)

    access_token = asyncio.run(
        service._get_valid_access_token(USER_ID, queries.record)
    )

    assert access_token == "new-access-token"
    assert cipher.decrypt(str(queries.record["encrypted_access_token"])) == (
        "new-access-token"
    )
