from typing import Any
from uuid import UUID

from supabase import AsyncClient

GMAIL_INTEGRATION_COLUMNS = """
id,
user_id,
gmail_address,
scopes,
status,
last_error,
last_synced_at,
token_expires_at,
send_acknowledgment_emails,
created_at,
updated_at
"""

GMAIL_INTEGRATION_TOKEN_COLUMNS = f"""
{GMAIL_INTEGRATION_COLUMNS},
encrypted_access_token,
encrypted_refresh_token
"""


class GmailIntegrationQueries:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_by_user_id(
        self,
        user_id: UUID,
        *,
        include_tokens: bool = False,
    ) -> dict[str, Any] | None:
        columns = (
            GMAIL_INTEGRATION_TOKEN_COLUMNS
            if include_tokens
            else GMAIL_INTEGRATION_COLUMNS
        )
        response = await (
            self._client.table("gmail_integrations")
            .select(columns)
            .eq("user_id", str(user_id))
            .maybe_single()
            .execute()
        )
        return response.data if response is not None else None

    async def upsert(self, values: dict[str, Any]) -> dict[str, Any]:
        response = await (
            self._client.table("gmail_integrations")
            .upsert(values, on_conflict="user_id")
            .select(GMAIL_INTEGRATION_COLUMNS)
            .execute()
        )
        return response.data[0]

    async def update(
        self,
        user_id: UUID,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        response = await (
            self._client.table("gmail_integrations")
            .update(values)
            .eq("user_id", str(user_id))
            .select(GMAIL_INTEGRATION_COLUMNS)
            .execute()
        )
        return response.data[0]

    async def delete(self, user_id: UUID) -> bool:
        response = await (
            self._client.table("gmail_integrations")
            .delete()
            .eq("user_id", str(user_id))
            .select("id")
            .execute()
        )
        return bool(response.data)
