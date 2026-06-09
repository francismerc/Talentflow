import json
import re
from typing import Any
from uuid import UUID

from app.ai.gemini import GeminiClient
from app.core.errors import ConflictError, NotFoundError
from app.database.queries.ai_analyses import AIAnalysisQueries

PROMPT_VERSION = "candidate-analysis-v1"
MAX_RESUME_CHARACTERS = 60_000
_EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)
_PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s().-]*)?(?:\d[\s().-]*){7,14}\d(?!\w)"
)


class AIAnalysisService:
    def __init__(
        self,
        queries: AIAnalysisQueries,
        client: GeminiClient,
    ) -> None:
        self._queries = queries
        self._client = client

    async def analyze_applicant(
        self,
        applicant_id: UUID,
        *,
        actor_user_id: UUID,
    ) -> UUID:
        context = await self._queries.get_context(applicant_id)
        if context is None:
            raise NotFoundError("Applicant not found.")
        resume_text = str(context.get("resume_text") or "").strip()
        if len(resume_text) < 40:
            raise ConflictError(
                "The applicant does not have enough parsed resume text for analysis."
            )
        job = context.get("jobs")
        if not isinstance(job, dict):
            raise ConflictError("The applicant is not assigned to a valid job.")

        candidate_skills = [
            str(skill) for skill in context.get("skills") or [] if str(skill).strip()
        ]
        required_skills = [
            str(skill) for skill in job.get("required_skills") or [] if str(skill).strip()
        ]
        matched_skills, missing_skills = self._match_skills(
            candidate_skills,
            required_skills,
            resume_text,
        )
        result = await self._client.analyze(
            self._build_prompt(
                context=context,
                job=job,
                resume_text=self._redact(resume_text),
                matched_skills=matched_skills,
                missing_skills=missing_skills,
            )
        )
        output = result.output
        return await self._queries.record(
            applicant_id=applicant_id,
            actor_user_id=actor_user_id,
            model_name=self._client.model,
            prompt_version=PROMPT_VERSION,
            score=round(output.score, 2),
            summary=output.summary,
            strengths=output.strengths,
            weaknesses=output.weaknesses,
            recommendation=output.recommendation.value,
            recommendation_reason=output.recommendation_reason,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            raw_response=result.metadata,
        )

    @staticmethod
    def _build_prompt(
        *,
        context: dict[str, Any],
        job: dict[str, Any],
        resume_text: str,
        matched_skills: list[str],
        missing_skills: list[str],
    ) -> str:
        analysis_context = {
            "job": {
                "title": job.get("title"),
                "description": job.get("description"),
                "required_skills": job.get("required_skills") or [],
                "employment_type": job.get("employment_type"),
            },
            "candidate": {
                "skills": context.get("skills") or [],
                "education": context.get("education") or [],
                "experience": context.get("experience") or [],
                "total_experience_years": context.get("total_experience_years"),
                "resume_text": resume_text[:MAX_RESUME_CHARACTERS],
            },
            "deterministic_skill_comparison": {
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
            },
        }
        return (
            "Evaluate this candidate for this specific job. Use the deterministic "
            "skill comparison as fixed evidence; do not contradict it. Score rubric: "
            "50% required-skill evidence, 30% relevant experience evidence, and 20% "
            "role-specific accomplishments or education. Missing information is not "
            "negative evidence, but should lower confidence. Recommendations are "
            "advisory and must be explainable to a recruiter.\n\n"
            "UNTRUSTED_ANALYSIS_DATA_START\n"
            f"{json.dumps(analysis_context, ensure_ascii=True)}\n"
            "UNTRUSTED_ANALYSIS_DATA_END"
        )

    @staticmethod
    def _match_skills(
        candidate_skills: list[str],
        required_skills: list[str],
        resume_text: str,
    ) -> tuple[list[str], list[str]]:
        candidate_keys = {
            AIAnalysisService._normalize_skill(skill) for skill in candidate_skills
        }
        normalized_resume = (
            f" {AIAnalysisService._normalize_skill(resume_text)} "
        )
        matched: list[str] = []
        missing: list[str] = []
        for skill in required_skills:
            normalized_skill = AIAnalysisService._normalize_skill(skill)
            if normalized_skill in candidate_keys or (
                normalized_skill and f" {normalized_skill} " in normalized_resume
            ):
                matched.append(skill)
            else:
                missing.append(skill)
        return matched, missing

    @staticmethod
    def _normalize_skill(value: str) -> str:
        return " ".join(
            re.sub(r"[^a-z0-9+#.]+", " ", value.casefold()).split()
        )

    @staticmethod
    def _redact(value: str) -> str:
        value = _EMAIL_PATTERN.sub("[EMAIL REDACTED]", value)
        return _PHONE_PATTERN.sub("[PHONE REDACTED]", value)
