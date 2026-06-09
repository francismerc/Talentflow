import base64
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx

from app.core.config import Settings
from app.core.errors import ConfigurationError, ConflictError, IntegrationError
from app.database.queries.email_attachments import EmailAttachmentQueries
from app.database.queries.email_logs import EmailLogQueries
from app.database.queries.gmail_integrations import GmailIntegrationQueries
from app.gmail.security import OAuthStateError, OAuthStateSigner, TokenCipher
from app.schemas.gmail import (
    GmailAuthorization,
    GmailConnection,
    GmailProcessResult,
)
from app.services.resume_storage import RESUME_BUCKET, ResumeStorageService

GMAIL_MODIFY_SCOPE = "https://www.googleapis.com/auth/gmail.modify"
GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_API_URL = "https://gmail.googleapis.com/gmail/v1/users/me"
GMAIL_PROFILE_URL = f"{GMAIL_API_URL}/profile"
GMAIL_RESUME_QUERY = (
    "in:inbox is:unread has:attachment "
    "{filename:pdf filename:doc filename:docx}"
)

MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024
MAX_ATTACHMENTS_PER_MESSAGE = 5
TOKEN_EXPIRY_BUFFER_SECONDS = 60

SUPPORTED_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ),
}
_UNSAFE_FILE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True, slots=True)
class GmailAttachment:
    attachment_id: str
    file_name: str
    mime_type: str
    declared_size: int


@dataclass(frozen=True, slots=True)
class GmailMessageMetadata:
    message_id: str
    thread_id: str | None
    sender_email: str
    recipient_email: str
    subject: str
    received_at: datetime
    attachments: list[GmailAttachment]


@dataclass(frozen=True, slots=True)
class GmailSendResult:
    message_id: str
    thread_id: str | None


class GmailService:
    def __init__(
        self,
        queries: GmailIntegrationQueries,
        settings: Settings,
        *,
        email_logs: EmailLogQueries | None = None,
        email_attachments: EmailAttachmentQueries | None = None,
        resume_storage: ResumeStorageService | None = None,
    ) -> None:
        self._queries = queries
        self._settings = settings
        self._email_logs = email_logs
        self._email_attachments = email_attachments
        self._resume_storage = resume_storage

    async def get_connection(self, user_id: UUID) -> GmailConnection:
        record = await self._queries.get_by_user_id(user_id)
        if record is None:
            return GmailConnection(
                oauth_configured=self._is_configured(),
                connected=False,
            )
        return GmailConnection.model_validate(
            {
                **record,
                "oauth_configured": self._is_configured(),
                "connected": record["status"] == "connected",
            }
        )

    def create_authorization(self, user_id: UUID) -> GmailAuthorization:
        signer, _ = self._security_components()
        params = {
            "access_type": "offline",
            "client_id": self._settings.google_client_id,
            "include_granted_scopes": "true",
            "prompt": "consent",
            "redirect_uri": self._settings.google_redirect_uri,
            "response_type": "code",
            "scope": GMAIL_MODIFY_SCOPE,
            "state": signer.create(user_id),
        }
        return GmailAuthorization(
            authorization_url=f"{GOOGLE_AUTHORIZATION_URL}?{urlencode(params)}"
        )

    async def complete_oauth(self, code: str, state: str) -> UUID:
        signer, cipher = self._security_components()
        try:
            oauth_state = signer.verify(state)
        except OAuthStateError as exception:
            raise IntegrationError(str(exception)) from exception

        existing = await self._queries.get_by_user_id(
            oauth_state.user_id,
            include_tokens=True,
        )
        token_data = await self._exchange_code(code)
        access_token = self._required_string(token_data, "access_token")
        refresh_token = token_data.get("refresh_token")
        if not refresh_token and existing:
            encrypted_refresh_token = existing.get("encrypted_refresh_token")
        elif refresh_token:
            encrypted_refresh_token = cipher.encrypt(str(refresh_token))
        else:
            encrypted_refresh_token = None
        if not encrypted_refresh_token:
            raise IntegrationError(
                "Google did not return a refresh token. Reconnect Gmail and grant access."
            )

        profile = await self._get_profile(access_token)
        gmail_address = self._required_string(profile, "emailAddress")
        scopes = str(token_data.get("scope") or GMAIL_MODIFY_SCOPE).split()
        expires_in = int(token_data.get("expires_in", 3600))
        await self._queries.upsert(
            {
                "user_id": str(oauth_state.user_id),
                "gmail_address": gmail_address,
                "encrypted_access_token": cipher.encrypt(access_token),
                "encrypted_refresh_token": encrypted_refresh_token,
                "token_expires_at": (
                    datetime.now(UTC) + timedelta(seconds=expires_in)
                ).isoformat(),
                "scopes": scopes,
                "status": "connected",
                "last_error": None,
            }
        )
        return oauth_state.user_id

    async def disconnect(self, user_id: UUID) -> None:
        await self._queries.delete(user_id)

    async def update_settings(
        self,
        user_id: UUID,
        *,
        send_acknowledgment_emails: bool,
    ) -> GmailConnection:
        record = await self._queries.get_by_user_id(user_id)
        if record is None:
            raise ConflictError("Connect Gmail before updating email settings.")
        updated = await self._queries.update(
            user_id,
            {"send_acknowledgment_emails": send_acknowledgment_emails},
        )
        return GmailConnection.model_validate(
            {
                **updated,
                "oauth_configured": self._is_configured(),
                "connected": updated["status"] == "connected",
            }
        )

    async def send_message(
        self,
        user_id: UUID,
        *,
        recipient_email: str,
        subject: str,
        text_body: str,
        html_body: str,
        reply_to: str | None = None,
        thread_id: str | None = None,
    ) -> GmailSendResult:
        integration = await self._queries.get_by_user_id(
            user_id,
            include_tokens=True,
        )
        if integration is None or integration.get("status") != "connected":
            raise ConflictError("Connect Gmail before sending candidate emails.")

        sender_email = str(integration["gmail_address"])
        access_token = await self._get_valid_access_token(user_id, integration)
        message = EmailMessage()
        message["To"] = recipient_email
        message["From"] = sender_email
        message["Subject"] = subject
        if reply_to:
            message["Reply-To"] = reply_to
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")

        request_body: dict[str, str] = {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode("ascii").rstrip("=")
        }
        if thread_id:
            request_body["threadId"] = thread_id

        async with httpx.AsyncClient(timeout=20) as client:
            try:
                response = await client.post(
                    f"{GMAIL_API_URL}/messages/send",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=request_body,
                )
                response.raise_for_status()
            except httpx.HTTPError as exception:
                raise IntegrationError(
                    "Gmail could not send the candidate email."
                ) from exception
        payload = response.json()
        return GmailSendResult(
            message_id=self._required_string(payload, "id"),
            thread_id=str(payload["threadId"]) if payload.get("threadId") else None,
        )

    async def process_inbox(
        self,
        user_id: UUID,
        *,
        max_messages: int = 25,
    ) -> GmailProcessResult:
        self._require_processing_dependencies()
        integration = await self._queries.get_by_user_id(
            user_id,
            include_tokens=True,
        )
        if integration is None or integration.get("status") != "connected":
            raise ConflictError(
                "Connect a Gmail account before processing the inbox."
            )

        access_token = await self._get_valid_access_token(user_id, integration)
        message_ids = await self._list_resume_message_ids(
            access_token,
            max_messages=max_messages,
        )
        result = GmailProcessResult(messages_scanned=len(message_ids))

        for message_id in message_ids:
            existing_log = await self._email_logs.get_incoming_by_gmail_message_id(
                message_id
            )
            if existing_log is not None:
                if existing_log.get("status") == "failed":
                    await self._cleanup_failed_email_log(str(existing_log["id"]))
                else:
                    result.duplicates_skipped += 1
                    try:
                        await self._mark_as_read(access_token, message_id)
                    except IntegrationError:
                        result.errors += 1
                    continue

            email_log_id: str | None = None
            try:
                message = await self._get_message(access_token, message_id)
                metadata = self._parse_message(
                    message,
                    fallback_recipient=str(integration["gmail_address"]),
                )
                if not metadata.attachments:
                    result.unsupported_skipped += 1
                    continue

                email_log = await self._email_logs.create(
                    {
                        "gmail_message_id": metadata.message_id,
                        "gmail_thread_id": metadata.thread_id,
                        "idempotency_key": f"gmail:incoming:{metadata.message_id}",
                        "direction": "incoming",
                        "email_type": "application",
                        "sender_email": metadata.sender_email,
                        "recipient_email": metadata.recipient_email,
                        "subject": metadata.subject,
                        "status": "processing",
                        "received_at": metadata.received_at.isoformat(),
                    }
                )
                email_log_id = str(email_log["id"])

                stored_count = await self._store_attachments(
                    user_id=user_id,
                    access_token=access_token,
                    email_log_id=email_log_id,
                    metadata=metadata,
                )
                await self._email_logs.update(
                    email_log_id,
                    {
                        "status": "processed",
                        "processed_at": datetime.now(UTC).isoformat(),
                        "error_message": None,
                    },
                )
                result.messages_processed += 1
                result.attachments_stored += stored_count
                try:
                    await self._mark_as_read(access_token, message_id)
                except IntegrationError:
                    result.errors += 1
            except Exception as exception:
                result.errors += 1
                if email_log_id is not None:
                    await self._email_logs.update(
                        email_log_id,
                        {
                            "status": "failed",
                            "error_message": self._safe_error_message(exception),
                        },
                    )

        sync_values: dict[str, Any] = {
            "last_synced_at": datetime.now(UTC).isoformat(),
            "status": "connected",
            "last_error": None,
        }
        if result.errors:
            sync_values["last_error"] = (
                f"{result.errors} email(s) failed during the latest inbox run."
            )
        await self._queries.update(user_id, sync_values)
        return result

    async def _cleanup_failed_email_log(self, email_log_id: str) -> None:
        storage_paths = await self._email_attachments.list_storage_paths(email_log_id)
        for storage_path in storage_paths:
            try:
                await self._resume_storage.remove(storage_path)
            except Exception:
                continue
        await self._email_logs.delete(email_log_id)

    async def _store_attachments(
        self,
        *,
        user_id: UUID,
        access_token: str,
        email_log_id: str,
        metadata: GmailMessageMetadata,
    ) -> int:
        stored_count = 0
        for attachment in metadata.attachments[:MAX_ATTACHMENTS_PER_MESSAGE]:
            content = await self._download_attachment(
                access_token,
                metadata.message_id,
                attachment.attachment_id,
            )
            if not content or len(content) > MAX_ATTACHMENT_SIZE_BYTES:
                raise IntegrationError(
                    f"Attachment {attachment.file_name} exceeds the 10 MB limit."
                )

            safe_name = self._sanitize_file_name(attachment.file_name)
            storage_path = (
                f"{user_id}/{metadata.message_id}/"
                f"{attachment.attachment_id}-{safe_name}"
            )
            await self._resume_storage.upload(
                storage_path=storage_path,
                content=content,
                mime_type=attachment.mime_type,
            )
            try:
                await self._email_attachments.create(
                    {
                        "email_log_id": email_log_id,
                        "gmail_attachment_id": attachment.attachment_id,
                        "file_name": safe_name,
                        "mime_type": attachment.mime_type,
                        "size_bytes": len(content),
                        "storage_bucket": RESUME_BUCKET,
                        "storage_path": storage_path,
                        "status": "stored",
                    }
                )
            except Exception:
                await self._resume_storage.remove(storage_path)
                raise
            stored_count += 1
        return stored_count

    async def _get_valid_access_token(
        self,
        user_id: UUID,
        integration: dict[str, Any],
    ) -> str:
        _, cipher = self._security_components()
        encrypted_access_token = integration.get("encrypted_access_token")
        expires_at = self._parse_datetime(integration.get("token_expires_at"))
        if (
            encrypted_access_token
            and expires_at
            and expires_at
            > datetime.now(UTC) + timedelta(seconds=TOKEN_EXPIRY_BUFFER_SECONDS)
        ):
            return cipher.decrypt(str(encrypted_access_token))

        encrypted_refresh_token = integration.get("encrypted_refresh_token")
        if not encrypted_refresh_token:
            raise IntegrationError("The Gmail refresh token is missing. Reconnect Gmail.")
        token_data = await self._refresh_access_token(
            cipher.decrypt(str(encrypted_refresh_token))
        )
        access_token = self._required_string(token_data, "access_token")
        expires_in = int(token_data.get("expires_in", 3600))
        await self._queries.update(
            user_id,
            {
                "encrypted_access_token": cipher.encrypt(access_token),
                "token_expires_at": (
                    datetime.now(UTC) + timedelta(seconds=expires_in)
                ).isoformat(),
                "status": "connected",
                "last_error": None,
            },
        )
        return access_token

    async def _exchange_code(self, code: str) -> dict[str, Any]:
        return await self._post_google_token(
            {
                "client_id": self._settings.google_client_id,
                "client_secret": self._secret_value(
                    self._settings.google_client_secret
                ),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self._settings.google_redirect_uri,
            },
            failure_message="Google OAuth token exchange failed.",
        )

    async def _refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        return await self._post_google_token(
            {
                "client_id": self._settings.google_client_id,
                "client_secret": self._secret_value(
                    self._settings.google_client_secret
                ),
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            failure_message="Google OAuth token refresh failed. Reconnect Gmail.",
        )

    async def _post_google_token(
        self,
        data: dict[str, object],
        *,
        failure_message: str,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(GOOGLE_TOKEN_URL, data=data)
                response.raise_for_status()
            except httpx.HTTPError as exception:
                raise IntegrationError(failure_message) from exception
        return response.json()

    async def _get_profile(self, access_token: str) -> dict[str, Any]:
        return await self._gmail_get_json(
            GMAIL_PROFILE_URL,
            access_token,
            failure_message="Unable to read the connected Gmail profile.",
        )

    async def _list_resume_message_ids(
        self,
        access_token: str,
        *,
        max_messages: int,
    ) -> list[str]:
        payload = await self._gmail_get_json(
            f"{GMAIL_API_URL}/messages",
            access_token,
            params={
                "q": GMAIL_RESUME_QUERY,
                "maxResults": str(max_messages),
            },
            failure_message="Unable to search the connected Gmail inbox.",
        )
        messages = payload.get("messages")
        if not isinstance(messages, list):
            return []
        return [
            str(message["id"])
            for message in messages
            if isinstance(message, dict) and message.get("id")
        ]

    async def _get_message(
        self,
        access_token: str,
        message_id: str,
    ) -> dict[str, Any]:
        return await self._gmail_get_json(
            f"{GMAIL_API_URL}/messages/{message_id}",
            access_token,
            params={"format": "full"},
            failure_message=f"Unable to read Gmail message {message_id}.",
        )

    async def _download_attachment(
        self,
        access_token: str,
        message_id: str,
        attachment_id: str,
    ) -> bytes:
        payload = await self._gmail_get_json(
            (
                f"{GMAIL_API_URL}/messages/{message_id}/attachments/"
                f"{attachment_id}"
            ),
            access_token,
            failure_message=f"Unable to download attachment {attachment_id}.",
        )
        encoded_data = payload.get("data")
        if not isinstance(encoded_data, str):
            raise IntegrationError("Gmail attachment data is missing.")
        try:
            return base64.urlsafe_b64decode(
                encoded_data + ("=" * (-len(encoded_data) % 4))
            )
        except ValueError as exception:
            raise IntegrationError("Gmail attachment data is invalid.") from exception

    async def _mark_as_read(self, access_token: str, message_id: str) -> None:
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(
                    f"{GMAIL_API_URL}/messages/{message_id}/modify",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"removeLabelIds": ["UNREAD"]},
                )
                response.raise_for_status()
            except httpx.HTTPError as exception:
                raise IntegrationError(
                    f"Unable to mark Gmail message {message_id} as processed."
                ) from exception

    async def _gmail_get_json(
        self,
        url: str,
        access_token: str,
        *,
        failure_message: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params,
                )
                response.raise_for_status()
            except httpx.HTTPError as exception:
                raise IntegrationError(failure_message) from exception
        return response.json()

    @classmethod
    def _parse_message(
        cls,
        message: dict[str, Any],
        *,
        fallback_recipient: str,
    ) -> GmailMessageMetadata:
        message_id = cls._required_string(message, "id")
        payload = message.get("payload")
        if not isinstance(payload, dict):
            raise IntegrationError(f"Gmail message {message_id} has no payload.")

        raw_headers = payload.get("headers")
        headers = {
            str(item.get("name", "")).lower(): str(item.get("value", ""))
            for item in raw_headers
            if isinstance(item, dict)
        } if isinstance(raw_headers, list) else {}

        sender_email = parseaddr(headers.get("from", ""))[1]
        recipient_email = parseaddr(headers.get("to", ""))[1] or fallback_recipient
        if not sender_email:
            raise IntegrationError(
                f"Gmail message {message_id} has no valid sender address."
            )

        received_at = cls._message_received_at(message, headers.get("date"))
        return GmailMessageMetadata(
            message_id=message_id,
            thread_id=str(message["threadId"]) if message.get("threadId") else None,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=headers.get("subject", "").strip()[:1000],
            received_at=received_at,
            attachments=cls._extract_attachments(payload),
        )

    @classmethod
    def _extract_attachments(
        cls,
        payload: dict[str, Any],
    ) -> list[GmailAttachment]:
        attachments: list[GmailAttachment] = []
        parts: list[dict[str, Any]] = [payload]
        while parts:
            part = parts.pop()
            nested_parts = part.get("parts")
            if isinstance(nested_parts, list):
                parts.extend(item for item in nested_parts if isinstance(item, dict))

            file_name = str(part.get("filename") or "").strip()
            body = part.get("body")
            attachment_id = (
                str(body.get("attachmentId"))
                if isinstance(body, dict) and body.get("attachmentId")
                else ""
            )
            if not file_name or not attachment_id:
                continue

            extension = Path(file_name).suffix.lower()
            expected_mime_type = SUPPORTED_MIME_TYPES.get(extension)
            mime_type = str(part.get("mimeType") or "").lower()
            if expected_mime_type is None:
                continue
            if mime_type not in {expected_mime_type, "application/octet-stream"}:
                continue

            declared_size = int(body.get("size") or 0)
            if declared_size > MAX_ATTACHMENT_SIZE_BYTES:
                continue
            attachments.append(
                GmailAttachment(
                    attachment_id=attachment_id,
                    file_name=file_name,
                    mime_type=expected_mime_type,
                    declared_size=declared_size,
                )
            )
        return attachments

    @staticmethod
    def _message_received_at(
        message: dict[str, Any],
        date_header: str | None,
    ) -> datetime:
        if date_header:
            try:
                parsed = parsedate_to_datetime(date_header)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=UTC)
                return parsed.astimezone(UTC)
            except (TypeError, ValueError):
                pass
        internal_date = message.get("internalDate")
        if internal_date:
            try:
                return datetime.fromtimestamp(int(str(internal_date)) / 1000, tz=UTC)
            except ValueError:
                pass
        return datetime.now(UTC)

    def _security_components(self) -> tuple[OAuthStateSigner, TokenCipher]:
        if not self._is_configured():
            raise ConfigurationError(
                "Gmail OAuth is not configured on the backend."
            )
        return (
            OAuthStateSigner(
                self._secret_value(self._settings.google_oauth_state_secret)
            ),
            TokenCipher(
                self._secret_value(self._settings.google_token_encryption_key)
            ),
        )

    def _require_processing_dependencies(self) -> None:
        if not all(
            (self._email_logs, self._email_attachments, self._resume_storage)
        ):
            raise ConfigurationError(
                "Gmail inbox processing dependencies are not configured."
            )

    def _is_configured(self) -> bool:
        return all(
            (
                self._settings.google_client_id,
                self._secret_value(self._settings.google_client_secret),
                self._settings.google_redirect_uri,
                self._secret_value(self._settings.google_oauth_state_secret),
                self._secret_value(self._settings.google_token_encryption_key),
            )
        )

    @staticmethod
    def _required_string(payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not value:
            raise IntegrationError(f"Google did not return {key}.")
        return str(value)

    @staticmethod
    def _parse_datetime(value: object) -> datetime | None:
        if not value:
            return None
        if isinstance(value, datetime):
            parsed = value
        else:
            try:
                parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            except ValueError:
                return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @staticmethod
    def _sanitize_file_name(file_name: str) -> str:
        safe_name = _UNSAFE_FILE_NAME.sub("_", Path(file_name).name).strip("._")
        return (safe_name or "resume")[:255]

    @staticmethod
    def _safe_error_message(exception: Exception) -> str:
        if isinstance(exception, IntegrationError):
            return exception.message[:1000]
        return "Unexpected error while processing this recruitment email."

    @staticmethod
    def _secret_value(value: object) -> str:
        if value is None:
            return ""
        getter = getattr(value, "get_secret_value", None)
        return getter() if getter else str(value)
