from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.errors import ConflictError, NotFoundError
from app.database.queries.common import Pagination, QueryPage
from app.database.queries.jobs import JobFilters, JobQueries
from app.schemas.jobs import JobCreate, JobDetail, JobStatus, JobSummary, JobUpdate


class JobService:
    def __init__(self, queries: JobQueries) -> None:
        self._queries = queries

    async def list_jobs(
        self,
        *,
        filters: JobFilters,
        pagination: Pagination,
    ) -> QueryPage[JobSummary]:
        result = await self._queries.list(filters=filters, pagination=pagination)
        return QueryPage(
            items=[self._to_summary(record) for record in result.items],
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        )

    async def get_job(self, job_id: UUID) -> JobDetail:
        record = await self._queries.get_by_id(job_id)
        if record is None:
            raise NotFoundError("Job not found.")
        return self._to_detail(record)

    async def create_job(
        self,
        payload: JobCreate,
        *,
        created_by: UUID | None = None,
    ) -> JobDetail:
        values = payload.model_dump(mode="json")
        values["created_by"] = str(created_by) if created_by else None
        self._apply_closed_at(values, payload.status)

        record = await self._queries.create(values)
        return self._to_detail({**record, "applicants": []})

    async def update_job(self, job_id: UUID, payload: JobUpdate) -> JobDetail:
        await self.get_job(job_id)
        values = payload.model_dump(exclude_unset=True, mode="json")
        if payload.status is not None:
            self._apply_closed_at(values, payload.status)

        record = await self._queries.update(job_id, values)
        if record is None:
            raise NotFoundError("Job not found.")
        return await self.get_job(job_id)

    async def delete_job(self, job_id: UUID) -> None:
        job = await self.get_job(job_id)
        if job.applicant_count > 0:
            raise ConflictError(
                "Jobs with applicants cannot be deleted. Close the job instead."
            )
        if not await self._queries.delete(job_id):
            raise NotFoundError("Job not found.")

    @staticmethod
    def _apply_closed_at(values: dict[str, Any], status: JobStatus) -> None:
        values["closed_at"] = (
            datetime.now(UTC).isoformat() if status is JobStatus.CLOSED else None
        )

    @staticmethod
    def _extract_applicant_count(record: dict[str, Any]) -> int:
        aggregate = record.get("applicants")
        if (
            isinstance(aggregate, list)
            and aggregate
            and isinstance(aggregate[0], dict)
        ):
            return int(aggregate[0].get("count", 0))
        return len(aggregate) if isinstance(aggregate, list) else 0

    @classmethod
    def _to_summary(cls, record: dict[str, Any]) -> JobSummary:
        return JobSummary.model_validate(
            {
                **record,
                "applicant_count": cls._extract_applicant_count(record),
            }
        )

    @classmethod
    def _to_detail(cls, record: dict[str, Any]) -> JobDetail:
        applicants = record.get("applicants")
        applicant_items = (
            applicants
            if isinstance(applicants, list)
            and (not applicants or "count" not in applicants[0])
            else []
        )
        return JobDetail.model_validate(
            {
                **record,
                "applicants": applicant_items,
                "applicant_count": len(applicant_items),
            }
        )
