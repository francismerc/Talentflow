from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.core.errors import ConflictError, NotFoundError
from app.database.queries.common import Pagination, QueryPage
from app.database.queries.jobs import JobFilters
from app.schemas.jobs import JobCreate, JobStatus, JobUpdate
from app.services.jobs import JobService

pytestmark = pytest.mark.anyio

JOB_ID = UUID("10000000-0000-4000-8000-000000000001")


def job_record(*, status: str = "active", applicants: list[dict] | None = None) -> dict:
    now = datetime(2026, 6, 6, tzinfo=UTC).isoformat()
    return {
        "id": str(JOB_ID),
        "created_by": None,
        "title": "Frontend Engineer",
        "description": "Build recruiter experiences.",
        "required_skills": ["React", "TypeScript"],
        "location": "Remote",
        "employment_type": "full_time",
        "status": status,
        "created_at": now,
        "updated_at": now,
        "closed_at": now if status == "closed" else None,
        "applicants": applicants or [],
    }


class FakeJobQueries:
    def __init__(self, record: dict | None = None) -> None:
        self.record = record
        self.created_values: dict | None = None
        self.updated_values: dict | None = None
        self.deleted = False

    async def list(
        self,
        *,
        filters: JobFilters,
        pagination: Pagination,
    ) -> QueryPage[dict]:
        return QueryPage(
            items=[job_record()],
            page=pagination.page,
            page_size=pagination.page_size,
            total=1,
        )

    async def get_by_id(self, _: UUID) -> dict | None:
        return self.record

    async def create(self, values: dict) -> dict:
        self.created_values = values
        return {**job_record(status=values["status"]), **values}

    async def update(self, _: UUID, values: dict) -> dict | None:
        self.updated_values = values
        if self.record is None:
            return None
        self.record = {**self.record, **values}
        return self.record

    async def delete(self, _: UUID) -> bool:
        self.deleted = True
        return True


async def test_create_job_normalizes_skills_and_closes_timestamp() -> None:
    queries = FakeJobQueries()
    service = JobService(queries)  # type: ignore[arg-type]

    result = await service.create_job(
        JobCreate(
            title="  Frontend Engineer  ",
            required_skills=["React", " react ", "TypeScript"],
            status=JobStatus.CLOSED,
        )
    )

    assert queries.created_values is not None
    assert queries.created_values["title"] == "Frontend Engineer"
    assert queries.created_values["required_skills"] == ["React", "TypeScript"]
    assert queries.created_values["closed_at"] is not None
    assert result.status is JobStatus.CLOSED


async def test_update_job_reopening_clears_closed_at() -> None:
    queries = FakeJobQueries(job_record(status="closed"))
    service = JobService(queries)  # type: ignore[arg-type]

    result = await service.update_job(
        JOB_ID,
        JobUpdate(status=JobStatus.ACTIVE),
    )

    assert queries.updated_values == {"status": "active", "closed_at": None}
    assert result.status is JobStatus.ACTIVE
    assert result.closed_at is None


async def test_get_missing_job_raises_not_found() -> None:
    service = JobService(FakeJobQueries())  # type: ignore[arg-type]

    with pytest.raises(NotFoundError):
        await service.get_job(JOB_ID)


async def test_delete_job_with_applicants_raises_conflict() -> None:
    queries = FakeJobQueries(
        job_record(
            applicants=[
                {
                    "id": "20000000-0000-4000-8000-000000000001",
                    "full_name": "Maya Chen",
                    "email": "maya@example.com",
                    "status": "new",
                    "applied_at": "2026-06-06T00:00:00Z",
                    "applicant_ai_analyses": [],
                }
            ]
        )
    )
    service = JobService(queries)  # type: ignore[arg-type]

    with pytest.raises(ConflictError):
        await service.delete_job(JOB_ID)

    assert queries.deleted is False
