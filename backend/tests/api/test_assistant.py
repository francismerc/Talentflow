from uuid import UUID

from fastapi.testclient import TestClient

from app.api.dependencies import get_assistant_service, get_current_user
from app.main import app
from app.schemas.assistant import (
    AssistantCandidateReference,
    AssistantChatData,
    AssistantChatRequest,
)
from app.schemas.auth import AuthenticatedUser

USER_ID = UUID("90000000-0000-4000-8000-000000000001")
APPLICANT_ID = UUID("20000000-0000-4000-8000-000000000001")


class FakeAssistantService:
    async def chat(self, payload: AssistantChatRequest) -> AssistantChatData:
        assert payload.message == "Show top candidates"
        return AssistantChatData(
            answer="Maya Chen is currently the highest-scoring candidate.",
            candidates=[
                AssistantCandidateReference(
                    applicant_id=APPLICANT_ID,
                    name="Maya Chen",
                    job_title="Frontend Engineer",
                    score=91,
                    status="shortlisted",
                    reason="Relevant React delivery experience.",
                )
            ],
            suggested_prompts=["Explain Maya's score"],
        )


def get_fake_assistant_service() -> FakeAssistantService:
    return FakeAssistantService()


def get_fake_current_user() -> AuthenticatedUser:
    return AuthenticatedUser(id=USER_ID, email="recruiter@example.com")


app.dependency_overrides[get_assistant_service] = get_fake_assistant_service
app.dependency_overrides[get_current_user] = get_fake_current_user
client = TestClient(app)


def test_assistant_chat_returns_grounded_candidate_references() -> None:
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "Show top candidates", "history": []},
    )

    assert response.status_code == 200
    assert response.json()["data"]["candidates"][0]["applicant_id"] == str(
        APPLICANT_ID
    )


def test_assistant_chat_validates_message_length() -> None:
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "", "history": []},
    )

    assert response.status_code == 422
