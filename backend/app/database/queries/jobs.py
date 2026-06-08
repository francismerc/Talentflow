from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from supabase import AsyncClient

from app.database.queries.common import Pagination, QueryPage, sanitize_search_term
from app.schemas.jobs import JobSortField, JobStatus

JOB_WRITE_COLUMNS = """
id,
created_by,
title,
description,
required_skills,
location,
employment_type,
status,
created_at,
updated_at,
closed_at
"""

JOB_LIST_COLUMNS = (
    JOB_WRITE_COLUMNS
    + """,
applicants(count)
"""
)

JOB_DETAIL_COLUMNS = """
id,
created_by,
title,
description,
required_skills,
location,
employment_type,
status,
created_at,
updated_at,
closed_at,
applicants(
  id,
  full_name,
  email,
  status,
  applied_at,
  applicant_ai_analyses(
    score,
    recommendation,
    recommendation_reason,
    is_current
  )
)
"""


@dataclass(frozen=True, slots=True)
class JobFilters:
    search: str | None = None
    status: JobStatus | None = None
    required_skill: str | None = None
    sort_by: JobSortField = JobSortField.CREATED_AT
    descending: bool = True


class JobQueries:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        filters: JobFilters | None = None,
        pagination: Pagination | None = None,
    ) -> QueryPage[dict[str, Any]]:
        query_filters = filters or JobFilters()
        page = pagination or Pagination()

        query = self._client.table("jobs").select(JOB_LIST_COLUMNS, count="exact")

        search = sanitize_search_term(query_filters.search)
        if search:
            query = query.ilike("title", f"%{search}%")
        if query_filters.status:
            query = query.eq("status", query_filters.status.value)
        if query_filters.required_skill:
            query = query.contains("required_skills", [query_filters.required_skill])

        response = await (
            query.order(query_filters.sort_by.value, desc=query_filters.descending)
            .range(page.range_start, page.range_end)
            .execute()
        )
        return QueryPage(
            items=response.data,
            page=page.page,
            page_size=page.page_size,
            total=response.count or 0,
        )

    async def get_by_id(self, job_id: UUID) -> dict[str, Any] | None:
        response = await (
            self._client.table("jobs")
            .select(JOB_DETAIL_COLUMNS)
            .eq("id", str(job_id))
            .maybe_single()
            .execute()
        )
        return response.data if response is not None else None

    async def list_active_for_matching(self) -> list[dict[str, Any]]:
        response = await (
            self._client.table("jobs")
            .select("id,title,required_skills,status")
            .eq("status", JobStatus.ACTIVE.value)
            .order("title")
            .execute()
        )
        return response.data

    async def create(self, values: dict[str, Any]) -> dict[str, Any]:
        response = await (
            self._client.table("jobs")
            .insert(values)
            .select(JOB_WRITE_COLUMNS)
            .execute()
        )
        return response.data[0]

    async def update(
        self,
        job_id: UUID,
        values: dict[str, Any],
    ) -> dict[str, Any] | None:
        response = await (
            self._client.table("jobs")
            .update(values)
            .eq("id", str(job_id))
            .select(JOB_WRITE_COLUMNS)
            .execute()
        )
        return response.data[0] if response.data else None

    async def delete(self, job_id: UUID) -> bool:
        response = await (
            self._client.table("jobs")
            .delete(count="exact")
            .eq("id", str(job_id))
            .execute()
        )
        return bool(response.count)
