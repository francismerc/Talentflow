from typing import Any
from uuid import UUID

from supabase import AsyncClient


class AIAnalysisQueries:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_context(self, applicant_id: UUID) -> dict[str, Any] | None:
        response = await (
            self._client.table("applicants")
            .select(
                """
                id,
                full_name,
                education,
                experience,
                total_experience_years,
                skills,
                resume_text,
                jobs!inner(
                  id,
                  title,
                  description,
                  required_skills,
                  location,
                  employment_type,
                  status
                )
                """
            )
            .eq("id", str(applicant_id))
            .maybe_single()
            .execute()
        )
        return response.data if response is not None else None

    async def record(
        self,
        *,
        applicant_id: UUID,
        actor_user_id: UUID,
        model_name: str,
        prompt_version: str,
        score: float,
        summary: str,
        strengths: list[str],
        weaknesses: list[str],
        recommendation: str,
        recommendation_reason: str,
        matched_skills: list[str],
        missing_skills: list[str],
        raw_response: dict[str, Any],
    ) -> UUID:
        response = await self._client.rpc(
            "record_applicant_ai_analysis",
            {
                "p_applicant_id": str(applicant_id),
                "p_actor_user_id": str(actor_user_id),
                "p_model_name": model_name,
                "p_prompt_version": prompt_version,
                "p_score": score,
                "p_summary": summary,
                "p_strengths": strengths,
                "p_weaknesses": weaknesses,
                "p_recommendation": recommendation,
                "p_recommendation_reason": recommendation_reason,
                "p_matched_skills": matched_skills,
                "p_missing_skills": missing_skills,
                "p_raw_response": raw_response,
            },
        ).execute()
        value = response.data[0] if isinstance(response.data, list) else response.data
        return UUID(str(value))
