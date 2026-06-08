from uuid import UUID

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user, get_resume_processing_service
from app.main import app
from app.schemas.auth import AuthenticatedUser
from app.schemas.resumes import ResumeProcessResult


class FakeResumeProcessingService:
    async def process_pending(self, *, max_attachments: int) -> ResumeProcessResult:
        assert max_attachments == 25
        return ResumeProcessResult(
            attachments_scanned=1,
            applicants_created=1,
        )


def get_fake_service() -> FakeResumeProcessingService:
    return FakeResumeProcessingService()


def get_fake_current_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id=UUID("90000000-0000-4000-8000-000000000001"),
        email="recruiter@example.com",
    )


app.dependency_overrides[get_resume_processing_service] = get_fake_service
app.dependency_overrides[get_current_user] = get_fake_current_user
client = TestClient(app)


def test_process_stored_resumes_returns_summary() -> None:
    response = client.post(
        "/api/v1/resumes/process",
        json={"max_attachments": 25},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "attachments_scanned": 1,
        "applicants_created": 1,
        "needs_review": 0,
        "failed": 0,
    }
