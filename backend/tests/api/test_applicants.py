from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_ai_analysis_service,
    get_applicant_service,
    get_current_user,
)
from app.core.errors import ConflictError, NotFoundError
from app.database.queries.common import QueryPage
from app.main import app
from app.schemas.applicants import (
    ApplicantCreate,
    ApplicantDetail,
    ApplicantStatus,
    ApplicantStatusUpdate,
    ApplicantSummary,
    ApplicantUpdate,
)
from app.schemas.auth import AuthenticatedUser

APPLICANT_ID = UUID("20000000-0000-4000-8000-000000000001")
JOB_ID = UUID("10000000-0000-4000-8000-000000000001")
USER_ID = UUID("90000000-0000-4000-8000-000000000001")


def make_summary(status: ApplicantStatus = ApplicantStatus.NEW) -> ApplicantSummary:
    now = datetime(2026, 6, 6, tzinfo=UTC)
    return ApplicantSummary(
        id=APPLICANT_ID,
        job_id=JOB_ID,
        full_name="Maya Chen",
        email="maya@example.com",
        phone=None,
        location="Singapore",
        status=status,
        applied_at=now,
        created_at=now,
    )


def make_detail(status: ApplicantStatus = ApplicantStatus.NEW) -> ApplicantDetail:
    return ApplicantDetail(
        **make_summary(status).model_dump(),
        education=[],
        experience=[],
        total_experience_years=7,
        skills=["Figma"],
        resume_file_name=None,
        resume_storage_path=None,
        resume_mime_type=None,
        reviewed_by=None,
        reviewed_at=None,
        updated_at=datetime(2026, 6, 6, tzinfo=UTC),
        timeline=[],
    )


class FakeApplicantService:
    async def list_applicants(self, **_: object) -> QueryPage[ApplicantSummary]:
        return QueryPage(items=[make_summary()], page=1, page_size=20, total=1)

    async def get_applicant(self, applicant_id: UUID) -> ApplicantDetail:
        if applicant_id != APPLICANT_ID:
            raise NotFoundError("Applicant not found.")
        return make_detail()

    async def create_applicant(self, _: ApplicantCreate) -> ApplicantDetail:
        return make_detail()

    async def update_applicant(
        self,
        _: UUID,
        __: ApplicantUpdate,
    ) -> ApplicantDetail:
        return make_detail()

    async def update_status(
        self,
        _: UUID,
        payload: ApplicantStatusUpdate,
        *,
        actor_user_id: UUID,
    ) -> ApplicantDetail:
        if payload.status is ApplicantStatus.HIRED:
            raise ConflictError("Cannot move applicant from new to hired.")
        return make_detail(payload.status)

    async def delete_applicant(self, _: UUID) -> None:
        return None


class FakeAIAnalysisService:
    async def analyze_applicant(
        self,
        applicant_id: UUID,
        *,
        actor_user_id: UUID,
    ) -> UUID:
        assert applicant_id == APPLICANT_ID
        assert actor_user_id == USER_ID
        return UUID("70000000-0000-4000-8000-000000000001")


def get_fake_applicant_service() -> FakeApplicantService:
    return FakeApplicantService()


def get_fake_ai_analysis_service() -> FakeAIAnalysisService:
    return FakeAIAnalysisService()


def get_fake_current_user() -> AuthenticatedUser:
    return AuthenticatedUser(id=USER_ID, email="recruiter@example.com")


app.dependency_overrides[get_applicant_service] = get_fake_applicant_service
app.dependency_overrides[get_ai_analysis_service] = get_fake_ai_analysis_service
app.dependency_overrides[get_current_user] = get_fake_current_user
client = TestClient(app)


def test_list_applicants_returns_paginated_response() -> None:
    response = client.get("/api/v1/applicants?status=new&minimum_score=80")

    assert response.status_code == 200
    assert response.json()["data"]["total"] == 1
    assert response.json()["data"]["items"][0]["full_name"] == "Maya Chen"


def test_list_applicants_rejects_invalid_score_range() -> None:
    response = client.get(
        "/api/v1/applicants?minimum_score=90&maximum_score=80"
    )

    assert response.status_code == 422
    assert response.json() == {
        "success": False,
        "message": "minimum_score cannot exceed maximum_score.",
    }


def test_create_applicant_returns_201() -> None:
    response = client.post(
        "/api/v1/applicants",
        json={
            "job_id": str(JOB_ID),
            "full_name": "Maya Chen",
            "email": "maya@example.com",
        },
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Applicant created successfully."


def test_create_applicant_requires_authentication() -> None:
    override = app.dependency_overrides.pop(get_current_user)
    try:
        response = client.post(
            "/api/v1/applicants",
            json={
                "job_id": str(JOB_ID),
                "full_name": "Maya Chen",
                "email": "maya@example.com",
            },
        )
    finally:
        app.dependency_overrides[get_current_user] = override

    assert response.status_code == 401


def test_generate_analysis_returns_refreshed_applicant() -> None:
    response = client.post(f"/api/v1/applicants/{APPLICANT_ID}/analysis")

    assert response.status_code == 200
    assert response.json()["message"] == "Candidate analysis generated successfully."
    assert response.json()["data"]["id"] == str(APPLICANT_ID)


def test_invalid_status_transition_returns_conflict() -> None:
    response = client.patch(
        f"/api/v1/applicants/{APPLICANT_ID}/status",
        json={"status": "hired"},
    )

    assert response.status_code == 409
    assert response.json()["success"] is False


def test_missing_applicant_returns_404() -> None:
    response = client.get(
        "/api/v1/applicants/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


def test_delete_applicant_returns_success() -> None:
    response = client.delete(f"/api/v1/applicants/{APPLICANT_ID}")

    assert response.status_code == 200
    assert response.json()["message"] == "Applicant deleted successfully."
