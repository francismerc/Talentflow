from typing import Any

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
