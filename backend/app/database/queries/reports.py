from typing import Any

from supabase import AsyncClient


class ReportQueries:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_overview(self, *, months: int) -> dict[str, Any]:
        response = await self._client.rpc(
            "get_recruitment_report",
            {"p_months": months},
        ).execute()
        if isinstance(response.data, list):
            return response.data[0] if response.data else {}
        return response.data or {}
