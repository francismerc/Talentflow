from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import CurrentUserDependency, JobServiceDependency
from app.database.queries.common import Pagination
from app.database.queries.jobs import JobFilters
from app.schemas.jobs import (
    DeleteResponse,
    JobCreate,
    JobListData,
    JobListResponse,
    JobResponse,
    JobSortField,
    JobStatus,
    JobUpdate,
)

router = APIRouter(prefix="/jobs")


@router.get("", response_model=JobListResponse)
async def list_jobs(
    service: JobServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
    job_status: Annotated[JobStatus | None, Query(alias="status")] = None,
    required_skill: Annotated[str | None, Query(max_length=100)] = None,
    sort_by: JobSortField = JobSortField.CREATED_AT,
    descending: bool = True,
) -> JobListResponse:
    result = await service.list_jobs(
        filters=JobFilters(
            search=search,
            status=job_status,
            required_skill=required_skill,
            sort_by=sort_by,
            descending=descending,
        ),
        pagination=Pagination(page=page, page_size=page_size),
    )
    return JobListResponse(
        message="Jobs retrieved successfully.",
        data=JobListData(
            items=result.items,
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    service: JobServiceDependency,
) -> JobResponse:
    job = await service.get_job(job_id)
    return JobResponse(message="Job retrieved successfully.", data=job)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    service: JobServiceDependency,
    current_user: CurrentUserDependency,
) -> JobResponse:
    job = await service.create_job(payload, created_by=current_user.id)
    return JobResponse(message="Job created successfully.", data=job)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    payload: JobUpdate,
    service: JobServiceDependency,
    _: CurrentUserDependency,
) -> JobResponse:
    job = await service.update_job(job_id, payload)
    return JobResponse(message="Job updated successfully.", data=job)


@router.delete("/{job_id}", response_model=DeleteResponse)
async def delete_job(
    job_id: UUID,
    service: JobServiceDependency,
    _: CurrentUserDependency,
) -> DeleteResponse:
    await service.delete_job(job_id)
    return DeleteResponse(message="Job deleted successfully.")
