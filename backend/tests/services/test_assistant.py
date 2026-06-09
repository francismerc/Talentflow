from types import SimpleNamespace
from uuid import UUID

import pytest

from app.ai.gemini import GeminiStructuredResult
from app.schemas.applicants import ApplicantStatus
from app.schemas.assistant import (
    AssistantActionOutput,
    AssistantActionRequest,
    AssistantActionType,
    AssistantChatRequest,
    AssistantOutput,
)
from app.schemas.emails import CandidateEmailType
from app.services.assistant import AssistantActionService, AssistantService

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
                proposed_actions=[
                    AssistantActionOutput(
                        action_type=AssistantActionType.SEND_SHORTLISTED_EMAIL,
                        applicant_id=APPLICANT_ID,
                    )
                ],
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
    assert result.proposed_actions[0].candidate_name == "Maya Chen"
    assert (
        result.proposed_actions[0].action_type
        is AssistantActionType.SEND_SHORTLISTED_EMAIL
    )
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


class FakeApplicantService:
    def __init__(self) -> None:
        self.status_update = None

    async def get_applicant(self, _: UUID) -> SimpleNamespace:
        return SimpleNamespace(
            id=APPLICANT_ID,
            full_name="Maya Chen",
            status=ApplicantStatus.SHORTLISTED,
        )

    async def update_status(
        self,
        _: UUID,
        payload: object,
        *,
        actor_user_id: UUID,
    ) -> SimpleNamespace:
        self.status_update = (payload, actor_user_id)
        return SimpleNamespace(
            id=APPLICANT_ID,
            full_name="Maya Chen",
            status=ApplicantStatus.SHORTLISTED,
        )


class FakeAutomatedEmail:
    def __init__(self) -> None:
        self.sent = None

    async def send_candidate_email(
        self,
        applicant_id: UUID,
        email_type: CandidateEmailType,
        *,
        actor_user_id: UUID,
    ) -> None:
        self.sent = (applicant_id, email_type, actor_user_id)


async def test_confirmed_shortlist_uses_applicant_service() -> None:
    applicants = FakeApplicantService()
    service = AssistantActionService(
        applicants,  # type: ignore[arg-type]
        FakeAutomatedEmail(),  # type: ignore[arg-type]
    )

    result = await service.execute(
        AssistantActionRequest(
            action_type=AssistantActionType.SHORTLIST_CANDIDATE,
            applicant_id=APPLICANT_ID,
        ),
        actor_user_id=UNKNOWN_ID,
    )

    assert result.status == "shortlisted"
    assert applicants.status_update is not None
    payload, actor_user_id = applicants.status_update
    assert payload.status is ApplicantStatus.SHORTLISTED
    assert payload.note == "Confirmed through TalentFlow AI Assistant."
    assert actor_user_id == UNKNOWN_ID


async def test_confirmed_email_uses_automated_email_service() -> None:
    email = FakeAutomatedEmail()
    service = AssistantActionService(
        FakeApplicantService(),  # type: ignore[arg-type]
        email,  # type: ignore[arg-type]
    )

    result = await service.execute(
        AssistantActionRequest(
            action_type=AssistantActionType.SEND_SHORTLISTED_EMAIL,
            applicant_id=APPLICANT_ID,
        ),
        actor_user_id=UNKNOWN_ID,
    )

    assert result.message == "The shortlisted email was sent to Maya Chen."
    assert email.sent == (
        APPLICANT_ID,
        CandidateEmailType.SHORTLISTED,
        UNKNOWN_ID,
    )
