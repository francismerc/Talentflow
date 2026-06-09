from typing import Any

from supabase import AsyncClient


class AssistantQueries:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_snapshot(self) -> dict[str, list[dict[str, Any]]]:
        applicants_response = await (
            self._client.table("applicants")
            .select(
                """
                id,
                full_name,
                status,
                skills,
                total_experience_years,
                applied_at,
                jobs(id,title,required_skills,status),
                applicant_ai_analyses(
                  score,
                  summary,
                  recommendation,
                  recommendation_reason,
                  matched_skills,
                  missing_skills,
                  is_current,
                  generated_at
                )
                """
            )
            .order("applied_at", desc=True)
            .limit(100)
            .execute()
        )
        jobs_response = await (
            self._client.table("jobs")
            .select(
                """
                id,
                title,
                required_skills,
                location,
                employment_type,
                status,
                created_at,
                applicants(count)
                """
            )
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return {
            "applicants": applicants_response.data or [],
            "jobs": jobs_response.data or [],
        }
