from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from supabase import AsyncClient

from app.database.queries.common import Pagination, QueryPage, sanitize_search_term
from app.schemas.applicants import ApplicantSortField, ApplicantStatus

APPLICANT_WRITE_COLUMNS = """
id,
job_id,
full_name,
email,
phone,
location,
education,
experience,
total_experience_years,
skills,
resume_file_name,
resume_storage_path,
resume_mime_type,
status,
applied_at,
reviewed_by,
reviewed_at,
created_at,
updated_at
"""

APPLICANT_LIST_COLUMNS = """
id,
job_id,
full_name,
email,
phone,
location,
status,
applied_at,
created_at,
jobs(id,title),
applicant_ai_analyses{join_type}(
  score,
  recommendation,
  is_current,
  generated_at
)
"""

APPLICANT_DETAIL_COLUMNS = """
id,
job_id,
full_name,
email,
phone,
location,
education,
experience,
total_experience_years,
skills,
resume_file_name,
resume_storage_path,
resume_mime_type,
status,
applied_at,
reviewed_by,
reviewed_at,
created_at,
updated_at,
jobs(
  id,
  title,
  required_skills,
  location,
  employment_type,
  status
),
applicant_ai_analyses(
  id,
  model_name,
  prompt_version,
  score,
  summary,
  strengths,
  weaknesses,
  recommendation,
  recommendation_reason,
  matched_skills,
  missing_skills,
  is_current,
  generated_at
),
applicant_timeline(
  id,
  actor_user_id,
  event_type,
  title,
  description,
  metadata,
  occurred_at
)
"""


@dataclass(frozen=True, slots=True)
class ApplicantFilters:
    search: str | None = None
    job_id: UUID | None = None
    status: ApplicantStatus | None = None
    minimum_score: float | None = None
    maximum_score: float | None = None
    skill: str | None = None
    sort_by: ApplicantSortField = ApplicantSortField.APPLIED_AT
    descending: bool = True

    def __post_init__(self) -> None:
        for field_name, value in (
            ("minimum_score", self.minimum_score),
            ("maximum_score", self.maximum_score),
        ):
            if value is not None and not 0 <= value <= 100:
                raise ValueError(f"{field_name} must be between 0 and 100")
        if (
            self.minimum_score is not None
            and self.maximum_score is not None
            and self.minimum_score > self.maximum_score
        ):
            raise ValueError("minimum_score cannot exceed maximum_score")


class ApplicantQueries:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        filters: ApplicantFilters | None = None,
        pagination: Pagination | None = None,
    ) -> QueryPage[dict[str, Any]]:
        query_filters = filters or ApplicantFilters()
        page = pagination or Pagination()
        score_filter_enabled = (
            query_filters.minimum_score is not None
            or query_filters.maximum_score is not None
        )
        list_columns = APPLICANT_LIST_COLUMNS.format(
            join_type="!inner" if score_filter_enabled else ""
        )

        query = self._client.table("applicants").select(
            list_columns,
            count="exact",
        )

        search = sanitize_search_term(query_filters.search)
        if search:
            query = query.or_(
                f"full_name.ilike.%{search}%,email.ilike.%{search}%"
            )
        if query_filters.job_id:
            query = query.eq("job_id", str(query_filters.job_id))
        if query_filters.status:
            query = query.eq("status", query_filters.status.value)
        if query_filters.skill:
            query = query.contains("skills", [query_filters.skill])

        query = query.eq("applicant_ai_analyses.is_current", True)
        if query_filters.minimum_score is not None:
            query = query.gte(
                "applicant_ai_analyses.score",
                query_filters.minimum_score,
            )
        if query_filters.maximum_score is not None:
            query = query.lte(
                "applicant_ai_analyses.score",
                query_filters.maximum_score,
            )

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

    async def get_by_id(self, applicant_id: UUID) -> dict[str, Any] | None:
        response = await (
            self._client.table("applicants")
            .select(APPLICANT_DETAIL_COLUMNS)
            .eq("id", str(applicant_id))
            .eq("applicant_ai_analyses.is_current", True)
            .order(
                "occurred_at",
                desc=True,
                foreign_table="applicant_timeline",
            )
            .maybe_single()
            .execute()
        )
        return response.data if response is not None else None

    async def get_by_source_email_message_id(
        self,
        message_id: str,
    ) -> dict[str, Any] | None:
        response = await (
            self._client.table("applicants")
            .select("id")
            .eq("source_email_message_id", message_id)
            .maybe_single()
            .execute()
        )
        return response.data if response is not None else None

    async def create(self, values: dict[str, Any]) -> dict[str, Any]:
        response = await (
            self._client.table("applicants")
            .insert(values)
            .select(APPLICANT_WRITE_COLUMNS)
            .execute()
        )
        return response.data[0]

    async def create_from_resume(
        self,
        *,
        attachment_id: UUID,
        job_id: UUID,
        full_name: str,
        email: str,
        phone: str | None,
        location: str | None,
        education: list[dict[str, Any]],
        experience: list[dict[str, Any]],
        total_experience_years: float | None,
        skills: list[str],
        resume_text: str,
    ) -> UUID:
        response = await self._client.rpc(
            "create_applicant_from_resume",
            {
                "p_attachment_id": str(attachment_id),
                "p_job_id": str(job_id),
                "p_full_name": full_name,
                "p_email": email,
                "p_phone": phone,
                "p_location": location,
                "p_education": education,
                "p_experience": experience,
                "p_total_experience_years": total_experience_years,
                "p_skills": skills,
                "p_resume_text": resume_text,
            },
        ).execute()
        value = response.data[0] if isinstance(response.data, list) else response.data
        return UUID(str(value))

    async def update(
        self,
        applicant_id: UUID,
        values: dict[str, Any],
    ) -> dict[str, Any] | None:
        response = await (
            self._client.table("applicants")
            .update(values)
            .eq("id", str(applicant_id))
            .select(APPLICANT_WRITE_COLUMNS)
            .execute()
        )
        return response.data[0] if response.data else None

    async def update_status(
        self,
        *,
        applicant_id: UUID,
        status: ApplicantStatus,
        actor_user_id: UUID,
        title: str,
        description: str | None,
    ) -> dict[str, Any]:
        response = await self._client.rpc(
            "update_applicant_status",
            {
                "p_applicant_id": str(applicant_id),
                "p_status": status.value,
                "p_actor_user_id": str(actor_user_id),
                "p_title": title,
                "p_description": description,
            },
        ).execute()
        if isinstance(response.data, list):
            return response.data[0]
        return response.data

    async def delete(self, applicant_id: UUID) -> bool:
        response = await (
            self._client.table("applicants")
            .delete(count="exact")
            .eq("id", str(applicant_id))
            .execute()
        )
        return bool(response.count)
