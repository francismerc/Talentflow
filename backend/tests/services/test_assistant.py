from uuid import UUID

import pytest

from app.ai.gemini import GeminiStructuredResult
from app.schemas.assistant import (
    AssistantChatRequest,
    AssistantOutput,
)
from app.services.assistant import AssistantService

pytestmark = pytest.mark.anyio

APPLICANT_ID = UUID("20000000-0000-4000-8000-000000000001")
UNKNOWN_ID = UUID("20000000-0000-4000-8000-000000000099")


class FakeQueries:
    async def get_snapshot(self) -> dict:
        return {
            "applicants": [
                {
                    "id": str(APPLICANT_ID),
                    "full_name": "Maya Chen",
                    "email": "private@example.com",
                    "resume_text": "SECRET RESUME CONTENT",
                    "status": "shortlisted",
                    "skills": ["React", "TypeScript"],
                    "total_experience_years": 6,
                    "applied_at": "2026-06-09T00:00:00Z",
                    "jobs": {
                        "id": "10000000-0000-4000-8000-000000000001",
                        "title": "Frontend Engineer",
                        "required_skills": ["React"],
                        "status": "active",
                    },
                    "applicant_ai_analyses": [
                        {
                            "score": 91,
                            "summary": "Strong frontend evidence.",
                            "recommendation": "yes",
                            "recommendation_reason": "Relevant React delivery experience.",
                            "matched_skills": ["React"],
                            "missing_skills": [],
                            "is_current": True,
                        }
                    ],
                }
            ],
            "jobs": [
                {
                    "id": "10000000-0000-4000-8000-000000000001",
                    "title": "Frontend Engineer",
                    "required_skills": ["React"],
                    "location": "Remote",
                    "employment_type": "full_time",
                    "status": "active",
                    "applicants": [{"count": 1}],
                }
            ],
        }


class FakeGeminiClient:
    def __init__(self) -> None:
        self.prompt = ""
        self.system_instruction = ""

    async def generate_structured(self, **values: object) -> GeminiStructuredResult:
        self.prompt = str(values["prompt"])
        self.system_instruction = str(values["system_instruction"])
        return GeminiStructuredResult(
            output=AssistantOutput(
                answer=(
                    f"Maya Chen ({APPLICANT_ID}) is the top React candidate "
                    "with a score of 91."
                ),
                candidate_ids=[APPLICANT_ID, UNKNOWN_ID],
                suggested_prompts=[f"Explain {APPLICANT_ID}'s score"],
            ),
            metadata={},
        )


async def test_chat_uses_safe_snapshot_and_filters_unknown_candidate_ids() -> None:
    client = FakeGeminiClient()
    service = AssistantService(FakeQueries(), client)  # type: ignore[arg-type]

    result = await service.chat(
        AssistantChatRequest(message="Show top React candidates")
    )

    assert result.answer.startswith("Maya Chen")
    assert str(APPLICANT_ID) not in result.answer
    assert result.suggested_prompts == ["Explain Maya Chen's score"]
    assert [candidate.applicant_id for candidate in result.candidates] == [
        APPLICANT_ID
    ]
    assert "private@example.com" not in client.prompt
    assert "SECRET RESUME CONTENT" not in client.prompt
    assert "React" in client.prompt
    assert "Never display UUIDs or database IDs" in client.prompt
    assert "You cannot shortlist, reject, email" in client.system_instruction


async def test_chat_includes_only_recent_conversation_history() -> None:
    client = FakeGeminiClient()
    service = AssistantService(FakeQueries(), client)  # type: ignore[arg-type]
    history = [
        {"role": "user", "content": f"Question {index}"}
        for index in range(10)
    ]

    await service.chat(
        AssistantChatRequest(
            message="Continue",
            history=history,
        )
    )

    assert "Question 0" not in client.prompt
    assert "Question 1" not in client.prompt
    assert "Question 2" in client.prompt
    assert "Question 9" in client.prompt
