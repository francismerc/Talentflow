from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.core.errors import ConflictError, NotFoundError
from app.database.queries.common import QueryPage
from app.schemas.applicants import (
    ApplicantCreate,
    ApplicantStatus,
    ApplicantStatusUpdate,
    ApplicantUpdate,
)
from app.services.applicants import ApplicantService

pytestmark = pytest.mark.anyio

APPLICANT_ID = UUID("20000000-0000-4000-8000-000000000001")
JOB_ID = UUID("10000000-0000-4000-8000-000000000001")
USER_ID = UUID("90000000-0000-4000-8000-000000000001")


def applicant_record(status: str = "new") -> dict:
    now = datetime(2026, 6, 6, tzinfo=UTC).isoformat()
    return {
        "id": str(APPLICANT_ID),
        "job_id": str(JOB_ID),
        "full_name": "Maya Chen",
        "email": "maya@example.com",
        "phone": None,
        "location": "Singapore",
        "education": [],
        "experience": [],
        "total_experience_years": 7,
        "skills": ["Figma"],
        "resume_file_name": None,
        "resume_storage_path": None,
        "resume_mime_type": None,
        "status": status,
        "applied_at": now,
        "reviewed_by": None,
        "reviewed_at": None,
        "created_at": now,
        "updated_at": now,
        "jobs": {
            "id": str(JOB_ID),
            "title": "Senior Product Designer",
            "required_skills": ["Figma"],
            "location": "Remote",
            "employment_type": "full_time",
            "status": "active",
        },
        "applicant_ai_analyses": [],
        "applicant_timeline": [],
    }


class FakeApplicantQueries:
    def __init__(
        self,
        record: dict | None = None,
        *,
        duplicate: bool = False,
    ) -> None:
        self.record = record
        self.duplicate = duplicate
        self.created_values: dict | None = None
        self.updated_values: dict | None = None
        self.status_values: dict | None = None
        self.deleted = False

    async def list(self, **_: object) -> QueryPage[dict]:
        return QueryPage(items=[], page=1, page_size=20, total=0)

    async def get_by_id(self, _: UUID) -> dict | None:
        return self.record

    async def get_by_source_email_message_id(self, _: str) -> dict | None:
        return {"id": str(APPLICANT_ID)} if self.duplicate else None

    async def create(self, values: dict) -> dict:
        self.created_values = values
        self.record = applicant_record()
        return {"id": str(APPLICANT_ID)}

    async def update(self, _: UUID, values: dict) -> dict | None:
        self.updated_values = values
        if self.record is None:
            return None
        self.record = {**self.record, **values}
        return self.record

    async def update_status(self, **values: object) -> dict:
        self.status_values = values
        assert self.record is not None
        self.record = {**self.record, "status": values["status"].value}
        return self.record

    async def delete(self, _: UUID) -> bool:
        self.deleted = True
        return True


class FakeJobQueries:
    def __init__(self, status: str = "active", exists: bool = True) -> None:
        self.status = status
        self.exists = exists

    async def get_by_id(self, _: UUID) -> dict | None:
        if not self.exists:
            return None
        return {"id": str(JOB_ID), "status": self.status}


async def test_create_applicant_rejects_duplicate_email_message() -> None:
    applicants = FakeApplicantQueries(duplicate=True)
    service = ApplicantService(  # type: ignore[arg-type]
        applicants,
        FakeJobQueries(),
    )

    with pytest.raises(ConflictError):
        await service.create_applicant(
            ApplicantCreate(
                job_id=JOB_ID,
                full_name="Maya Chen",
                email="maya@example.com",
                source_email_message_id="gmail-message-1",
            )
        )

    assert applicants.created_values is None


async def test_create_applicant_rejects_closed_job() -> None:
    service = ApplicantService(  # type: ignore[arg-type]
        FakeApplicantQueries(),
        FakeJobQueries(status="closed"),
    )

    with pytest.raises(ConflictError):
        await service.create_applicant(
            ApplicantCreate(
                job_id=JOB_ID,
                full_name="Maya Chen",
                email="maya@example.com",
            )
        )


async def test_valid_status_transition_calls_atomic_query() -> None:
    applicants = FakeApplicantQueries(applicant_record("under_review"))
    service = ApplicantService(  # type: ignore[arg-type]
        applicants,
        FakeJobQueries(),
    )

    result = await service.update_status(
        APPLICANT_ID,
        ApplicantStatusUpdate(
            status=ApplicantStatus.SHORTLISTED,
            note="Strong match.",
        ),
        actor_user_id=USER_ID,
    )

    assert result.status is ApplicantStatus.SHORTLISTED
    assert applicants.status_values is not None
    assert applicants.status_values["actor_user_id"] == USER_ID
    assert applicants.status_values["title"] == "Applicant shortlisted"


async def test_invalid_status_transition_raises_conflict() -> None:
    service = ApplicantService(  # type: ignore[arg-type]
        FakeApplicantQueries(applicant_record("new")),
        FakeJobQueries(),
    )

    with pytest.raises(ConflictError):
        await service.update_status(
            APPLICANT_ID,
            ApplicantStatusUpdate(status=ApplicantStatus.HIRED),
            actor_user_id=USER_ID,
        )


async def test_update_missing_applicant_raises_not_found() -> None:
    service = ApplicantService(  # type: ignore[arg-type]
        FakeApplicantQueries(),
        FakeJobQueries(),
    )

    with pytest.raises(NotFoundError):
        await service.update_applicant(
            APPLICANT_ID,
            ApplicantUpdate(full_name="Updated Name"),
        )
