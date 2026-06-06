from uuid import UUID

from app.core.errors import ConflictError, NotFoundError
from app.database.queries.applicants import ApplicantFilters, ApplicantQueries
from app.database.queries.common import Pagination, QueryPage
from app.database.queries.jobs import JobQueries
from app.schemas.applicants import (
    ApplicantCreate,
    ApplicantDetail,
    ApplicantStatus,
    ApplicantStatusUpdate,
    ApplicantSummary,
    ApplicantUpdate,
)
from app.schemas.jobs import JobStatus

ALLOWED_STATUS_TRANSITIONS: dict[ApplicantStatus, set[ApplicantStatus]] = {
    ApplicantStatus.NEW: {
        ApplicantStatus.UNDER_REVIEW,
        ApplicantStatus.SHORTLISTED,
        ApplicantStatus.REJECTED,
        ApplicantStatus.WITHDRAWN,
    },
    ApplicantStatus.UNDER_REVIEW: {
        ApplicantStatus.SHORTLISTED,
        ApplicantStatus.INTERVIEW,
        ApplicantStatus.REJECTED,
        ApplicantStatus.WITHDRAWN,
    },
    ApplicantStatus.SHORTLISTED: {
        ApplicantStatus.INTERVIEW,
        ApplicantStatus.REJECTED,
        ApplicantStatus.WITHDRAWN,
    },
    ApplicantStatus.INTERVIEW: {
        ApplicantStatus.HIRED,
        ApplicantStatus.REJECTED,
        ApplicantStatus.WITHDRAWN,
    },
    ApplicantStatus.HIRED: set(),
    ApplicantStatus.REJECTED: {ApplicantStatus.UNDER_REVIEW},
    ApplicantStatus.WITHDRAWN: set(),
}

STATUS_TITLES: dict[ApplicantStatus, str] = {
    ApplicantStatus.NEW: "Applicant marked as new",
    ApplicantStatus.UNDER_REVIEW: "Applicant moved under review",
    ApplicantStatus.SHORTLISTED: "Applicant shortlisted",
    ApplicantStatus.INTERVIEW: "Applicant moved to interview",
    ApplicantStatus.HIRED: "Applicant hired",
    ApplicantStatus.REJECTED: "Applicant rejected",
    ApplicantStatus.WITHDRAWN: "Application withdrawn",
}


class ApplicantService:
    def __init__(
        self,
        applicant_queries: ApplicantQueries,
        job_queries: JobQueries,
    ) -> None:
        self._applicant_queries = applicant_queries
        self._job_queries = job_queries

    async def list_applicants(
        self,
        *,
        filters: ApplicantFilters,
        pagination: Pagination,
    ) -> QueryPage[ApplicantSummary]:
        result = await self._applicant_queries.list(
            filters=filters,
            pagination=pagination,
        )
        return QueryPage(
            items=[self._to_summary(record) for record in result.items],
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        )

    async def get_applicant(self, applicant_id: UUID) -> ApplicantDetail:
        record = await self._applicant_queries.get_by_id(applicant_id)
        if record is None:
            raise NotFoundError("Applicant not found.")
        return self._to_detail(record)

    async def create_applicant(self, payload: ApplicantCreate) -> ApplicantDetail:
        await self._validate_job(payload.job_id)
        if (
            payload.source_email_message_id
            and await self._applicant_queries.get_by_source_email_message_id(
                payload.source_email_message_id
            )
        ):
            raise ConflictError("This recruitment email has already been processed.")

        values = payload.model_dump(mode="json", exclude_none=True)
        values["status"] = ApplicantStatus.NEW.value
        record = await self._applicant_queries.create(values)
        return await self.get_applicant(UUID(record["id"]))

    async def update_applicant(
        self,
        applicant_id: UUID,
        payload: ApplicantUpdate,
    ) -> ApplicantDetail:
        await self.get_applicant(applicant_id)
        if payload.job_id is not None:
            await self._validate_job(payload.job_id)

        values = payload.model_dump(exclude_unset=True, mode="json")
        record = await self._applicant_queries.update(applicant_id, values)
        if record is None:
            raise NotFoundError("Applicant not found.")
        return await self.get_applicant(applicant_id)

    async def update_status(
        self,
        applicant_id: UUID,
        payload: ApplicantStatusUpdate,
        *,
        actor_user_id: UUID,
    ) -> ApplicantDetail:
        applicant = await self.get_applicant(applicant_id)
        allowed = ALLOWED_STATUS_TRANSITIONS[applicant.status]
        if payload.status not in allowed:
            raise ConflictError(
                f"Cannot move applicant from {applicant.status.value} "
                f"to {payload.status.value}."
            )

        await self._applicant_queries.update_status(
            applicant_id=applicant_id,
            status=payload.status,
            actor_user_id=actor_user_id,
            title=STATUS_TITLES[payload.status],
            description=payload.note,
        )
        return await self.get_applicant(applicant_id)

    async def delete_applicant(self, applicant_id: UUID) -> None:
        await self.get_applicant(applicant_id)
        if not await self._applicant_queries.delete(applicant_id):
            raise NotFoundError("Applicant not found.")

    async def _validate_job(self, job_id: UUID) -> None:
        job = await self._job_queries.get_by_id(job_id)
        if job is None:
            raise NotFoundError("Job not found.")
        if job["status"] == JobStatus.CLOSED.value:
            raise ConflictError("Applicants cannot be assigned to a closed job.")

    @staticmethod
    def _current_analysis(record: dict) -> dict | None:
        analyses = record.get("applicant_ai_analyses") or []
        return next(
            (analysis for analysis in analyses if analysis.get("is_current")),
            None,
        )

    @classmethod
    def _to_summary(cls, record: dict) -> ApplicantSummary:
        return ApplicantSummary.model_validate(
            {
                **record,
                "job": record.get("jobs"),
                "current_analysis": cls._current_analysis(record),
            }
        )

    @classmethod
    def _to_detail(cls, record: dict) -> ApplicantDetail:
        return ApplicantDetail.model_validate(
            {
                **record,
                "job": record.get("jobs"),
                "current_analysis": cls._current_analysis(record),
                "timeline": record.get("applicant_timeline") or [],
            }
        )
