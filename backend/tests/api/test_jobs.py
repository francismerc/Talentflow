from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user, get_job_service
from app.core.errors import ConflictError, NotFoundError
from app.database.queries.common import QueryPage
from app.main import app
from app.schemas.auth import AuthenticatedUser
from app.schemas.jobs import (
    EmploymentType,
    JobCreate,
    JobDetail,
    JobStatus,
    JobSummary,
    JobUpdate,
)

JOB_ID = UUID("10000000-0000-4000-8000-000000000001")


def make_summary() -> JobSummary:
    now = datetime(2026, 6, 6, tzinfo=UTC)
    return JobSummary(
        id=JOB_ID,
        title="Frontend Engineer",
        description="Build recruiter experiences.",
        required_skills=["React", "TypeScript"],
        location="Remote",
        employment_type=EmploymentType.FULL_TIME,
        status=JobStatus.ACTIVE,
        created_at=now,
        updated_at=now,
        closed_at=None,
        applicant_count=0,
    )


def make_detail() -> JobDetail:
    return JobDetail(**make_summary().model_dump(), created_by=None, applicants=[])


class FakeJobService:
    async def list_jobs(self, **_: object) -> QueryPage[JobSummary]:
        return QueryPage(items=[make_summary()], page=1, page_size=20, total=1)

    async def get_job(self, job_id: UUID) -> JobDetail:
        if job_id != JOB_ID:
            raise NotFoundError("Job not found.")
        return make_detail()

    async def create_job(
        self,
        _: JobCreate,
        *,
        created_by: UUID | None = None,
    ) -> JobDetail:
        return make_detail()

    async def update_job(self, _: UUID, __: JobUpdate) -> JobDetail:
        return make_detail()

    async def delete_job(self, job_id: UUID) -> None:
        if job_id == JOB_ID:
            raise ConflictError(
                "Jobs with applicants cannot be deleted. Close the job instead."
            )


def get_fake_job_service() -> FakeJobService:
    return FakeJobService()


def get_fake_current_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id=UUID("90000000-0000-4000-8000-000000000001"),
        email="recruiter@example.com",
    )


app.dependency_overrides[get_job_service] = get_fake_job_service
app.dependency_overrides[get_current_user] = get_fake_current_user
client = TestClient(app)


def test_list_jobs_returns_standardized_page() -> None:
    response = client.get("/api/v1/jobs?page=1&page_size=20&status=active")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["total"] == 1
    assert payload["data"]["items"][0]["title"] == "Frontend Engineer"


def test_create_job_validates_and_returns_201() -> None:
    response = client.post(
        "/api/v1/jobs",
        json={
            "title": "Frontend Engineer",
            "description": "Build recruiter experiences.",
            "required_skills": ["React", "TypeScript"],
            "status": "active",
        },
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Job created successfully."


def test_create_job_requires_authentication() -> None:
    override = app.dependency_overrides.pop(get_current_user)
    try:
        response = client.post(
            "/api/v1/jobs",
            json={"title": "Frontend Engineer"},
        )
    finally:
        app.dependency_overrides[get_current_user] = override

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "message": "Authentication is required.",
    }


def test_empty_patch_returns_validation_error() -> None:
    response = client.patch(f"/api/v1/jobs/{JOB_ID}", json={})

    assert response.status_code == 422
    assert response.json()["success"] is False


def test_missing_job_returns_404() -> None:
    response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "message": "Job not found.",
    }


def test_delete_job_with_applicants_returns_409() -> None:
    response = client.delete(f"/api/v1/jobs/{JOB_ID}")

    assert response.status_code == 409
    assert response.json()["success"] is False
