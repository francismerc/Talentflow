from typing import Any
from uuid import UUID

from supabase import AsyncClient

EMAIL_LOG_COLUMNS = """
id,
applicant_id,
gmail_message_id,
gmail_thread_id,
idempotency_key,
direction,
email_type,
sender_email,
recipient_email,
subject,
status,
error_message,
received_at,
sent_at,
processed_at,
created_at
"""


class EmailLogQueries:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_incoming_by_gmail_message_id(
        self,
        message_id: str,
    ) -> dict[str, Any] | None:
        response = await (
            self._client.table("email_logs")
            .select(EMAIL_LOG_COLUMNS)
            .eq("gmail_message_id", message_id)
            .eq("direction", "incoming")
            .maybe_single()
            .execute()
        )
        return response.data if response is not None else None

    async def reserve_outgoing(
        self,
        *,
        applicant_id: UUID,
        idempotency_key: str,
        email_type: str,
        sender_email: str,
        recipient_email: str,
        subject: str,
    ) -> tuple[dict[str, Any], bool]:
        response = await self._client.rpc(
            "reserve_outgoing_email",
            {
                "p_applicant_id": str(applicant_id),
                "p_idempotency_key": idempotency_key,
                "p_email_type": email_type,
                "p_sender_email": sender_email,
                "p_recipient_email": recipient_email,
                "p_subject": subject,
            },
        ).execute()
        payload = response.data[0] if isinstance(response.data, list) else response.data
        return payload["email_log"], bool(payload["reserved"])

    async def mark_sent(
        self,
        *,
        email_log_id: UUID,
        actor_user_id: UUID,
        gmail_message_id: str,
        gmail_thread_id: str | None,
    ) -> dict[str, Any]:
        response = await self._client.rpc(
            "record_outgoing_email_sent",
            {
                "p_email_log_id": str(email_log_id),
                "p_actor_user_id": str(actor_user_id),
                "p_gmail_message_id": gmail_message_id,
                "p_gmail_thread_id": gmail_thread_id,
            },
        ).execute()
        if isinstance(response.data, list):
            return response.data[0]
        return response.data

    async def mark_failed(
        self,
        email_log_id: UUID,
        error_message: str,
    ) -> dict[str, Any]:
        return await self.update(
            str(email_log_id),
            {
                "status": "failed",
                "error_message": error_message[:1000],
                "sent_at": None,
            },
        )

    async def create(self, values: dict[str, Any]) -> dict[str, Any]:
        response = await (
            self._client.table("email_logs")
            .insert(values)
            .select(EMAIL_LOG_COLUMNS)
            .execute()
        )
        return response.data[0]

    async def update(
        self,
        email_log_id: str,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        response = await (
            self._client.table("email_logs")
            .update(values)
            .eq("id", email_log_id)
            .select(EMAIL_LOG_COLUMNS)
            .execute()
        )
        return response.data[0]

    async def delete(self, email_log_id: str) -> bool:
        response = await (
            self._client.table("email_logs")
            .delete()
            .eq("id", email_log_id)
            .select("id")
            .execute()
        )
        return bool(response.data)
