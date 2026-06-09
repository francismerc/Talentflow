from uuid import UUID

import pytest

from app.ai.gemini import GeminiAnalysisResult
from app.core.errors import ConflictError
from app.schemas.ai import AIRecommendation, CandidateAnalysisOutput
from app.services.ai_analysis import AIAnalysisService

pytestmark = pytest.mark.anyio

APPLICANT_ID = UUID("20000000-0000-4000-8000-000000000001")
USER_ID = UUID("90000000-0000-4000-8000-000000000001")
ANALYSIS_ID = UUID("70000000-0000-4000-8000-000000000001")


class FakeQueries:
    def __init__(self, context: dict) -> None:
        self.context = context
        self.recorded: dict | None = None

    async def get_context(self, _: UUID) -> dict:
        return self.context

    async def record(self, **values: object) -> UUID:
        self.recorded = values
        return ANALYSIS_ID


class FakeGeminiClient:
    model = "gemini-test"

    def __init__(self) -> None:
        self.prompt = ""

    async def analyze(self, prompt: str) -> GeminiAnalysisResult:
        self.prompt = prompt
        return GeminiAnalysisResult(
            output=CandidateAnalysisOutput(
                score=84,
                summary="The candidate demonstrates relevant frontend delivery experience.",
                strengths=["Strong React evidence"],
                weaknesses=["No documented Next.js production experience"],
                recommendation=AIRecommendation.YES,
                recommendation_reason=(
                    "The candidate meets the core React requirement with relevant evidence."
                ),
            ),
            metadata={"usage_metadata": {"totalTokenCount": 200}},
        )


def make_context(resume_text: str | None = None) -> dict:
    return {
        "id": str(APPLICANT_ID),
        "full_name": "Candidate Name",
        "education": [],
        "experience": [{"title": "Frontend Engineer"}],
        "total_experience_years": 4,
        "skills": ["React", "TypeScript"],
        "resume_text": resume_text
        or (
            "Candidate Name candidate@example.com +63 912 345 6789. "
            "Built React applications with TypeScript for four years."
        ),
        "jobs": {
            "id": "10000000-0000-4000-8000-000000000001",
            "title": "Frontend Engineer",
            "description": "Build customer-facing web applications.",
            "required_skills": ["React", "Next.js"],
            "employment_type": "full_time",
        },
    }


async def test_analysis_records_deterministic_skill_match_and_redacts_contact_data() -> None:
    queries = FakeQueries(make_context())
    client = FakeGeminiClient()
    service = AIAnalysisService(queries, client)  # type: ignore[arg-type]

    result = await service.analyze_applicant(
        APPLICANT_ID,
        actor_user_id=USER_ID,
    )

    assert result == ANALYSIS_ID
    assert queries.recorded is not None
    assert queries.recorded["matched_skills"] == ["React"]
    assert queries.recorded["missing_skills"] == ["Next.js"]
    assert queries.recorded["recommendation"] == "yes"
    assert "candidate@example.com" not in client.prompt
    assert "+63 912 345 6789" not in client.prompt
    assert "[EMAIL REDACTED]" in client.prompt
    assert "[PHONE REDACTED]" in client.prompt


async def test_analysis_requires_parsed_resume_text() -> None:
    queries = FakeQueries(make_context("Too short"))
    service = AIAnalysisService(queries, FakeGeminiClient())  # type: ignore[arg-type]

    with pytest.raises(ConflictError):
        await service.analyze_applicant(
            APPLICANT_ID,
            actor_user_id=USER_ID,
        )
