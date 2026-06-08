from typing import Any

from supabase import AsyncClient


class EmailAttachmentQueries:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def create(self, values: dict[str, Any]) -> dict[str, Any]:
        response = await (
            self._client.table("email_attachments")
            .insert(values)
            .select(
                """
                id,
                email_log_id,
                gmail_attachment_id,
                file_name,
                mime_type,
                size_bytes,
                storage_bucket,
                storage_path,
                status,
                created_at
                """
            )
            .execute()
        )
        return response.data[0]

    async def list_storage_paths(self, email_log_id: str) -> list[str]:
        response = await (
            self._client.table("email_attachments")
            .select("storage_path")
            .eq("email_log_id", email_log_id)
            .execute()
        )
        return [
            str(item["storage_path"])
            for item in response.data
            if item.get("storage_path")
        ]

    async def list_stored_for_processing(
        self,
        *,
        limit: int,
    ) -> list[dict[str, Any]]:
        response = await (
            self._client.table("email_attachments")
            .select(
                """
                id,
                email_log_id,
                file_name,
                mime_type,
                storage_bucket,
                storage_path,
                status,
                created_at,
                email_logs!inner(
                  applicant_id,
                  gmail_message_id,
                  gmail_thread_id,
                  sender_email,
                  subject,
                  received_at
                )
                """
            )
            .eq("status", "stored")
            .is_("email_logs.applicant_id", "null")
            .order("created_at")
            .limit(limit)
            .execute()
        )
        return response.data

    async def update(
        self,
        attachment_id: str,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        response = await (
            self._client.table("email_attachments")
            .update(values)
            .eq("id", attachment_id)
            .select("id,status,error_message,parsed_at,updated_at")
            .execute()
        )
        return response.data[0]
