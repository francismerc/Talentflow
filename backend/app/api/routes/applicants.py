from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import (
    AIAnalysisServiceDependency,
    ApplicantServiceDependency,
    AutomatedEmailServiceDependency,
    CurrentUserDependency,
)
from app.database.queries.applicants import ApplicantFilters
from app.database.queries.common import Pagination
from app.schemas.applicants import (
    ApplicantCreate,
    ApplicantDeleteResponse,
    ApplicantListData,
    ApplicantListResponse,
    ApplicantResponse,
    ApplicantSortField,
    ApplicantStatus,
    ApplicantStatusUpdate,
    ApplicantUpdate,
)
from app.schemas.emails import CandidateEmailResponse, CandidateEmailType

router = APIRouter(prefix="/applicants")


@router.get("", response_model=ApplicantListResponse)
async def list_applicants(
    service: ApplicantServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
    job_id: UUID | None = None,
    applicant_status: Annotated[
        ApplicantStatus | None,
        Query(alias="status"),
    ] = None,
    minimum_score: Annotated[float | None, Query(ge=0, le=100)] = None,
    maximum_score: Annotated[float | None, Query(ge=0, le=100)] = None,
    skill: Annotated[str | None, Query(max_length=100)] = None,
    sort_by: ApplicantSortField = ApplicantSortField.APPLIED_AT,
    descending: bool = True,
) -> ApplicantListResponse:
    if (
        minimum_score is not None
        and maximum_score is not None
        and minimum_score > maximum_score
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="minimum_score cannot exceed maximum_score.",
        )

    result = await service.list_applicants(
        filters=ApplicantFilters(
            search=search,
            job_id=job_id,
            status=applicant_status,
            minimum_score=minimum_score,
            maximum_score=maximum_score,
            skill=skill,
            sort_by=sort_by,
            descending=descending,
        ),
        pagination=Pagination(page=page, page_size=page_size),
    )
    return ApplicantListResponse(
        message="Applicants retrieved successfully.",
        data=ApplicantListData(
            items=result.items,
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/{applicant_id}", response_model=ApplicantResponse)
async def get_applicant(
    applicant_id: UUID,
    service: ApplicantServiceDependency,
) -> ApplicantResponse:
    applicant = await service.get_applicant(applicant_id)
    return ApplicantResponse(
        message="Applicant retrieved successfully.",
        data=applicant,
    )


@router.post(
    "",
    response_model=ApplicantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_applicant(
    payload: ApplicantCreate,
    service: ApplicantServiceDependency,
    _: CurrentUserDependency,
) -> ApplicantResponse:
    applicant = await service.create_applicant(payload)
    return ApplicantResponse(
        message="Applicant created successfully.",
        data=applicant,
    )


@router.post("/{applicant_id}/analysis", response_model=ApplicantResponse)
async def analyze_applicant(
    applicant_id: UUID,
    analysis_service: AIAnalysisServiceDependency,
    applicant_service: ApplicantServiceDependency,
    current_user: CurrentUserDependency,
) -> ApplicantResponse:
    await analysis_service.analyze_applicant(
        applicant_id,
        actor_user_id=current_user.id,
    )
    applicant = await applicant_service.get_applicant(applicant_id)
    return ApplicantResponse(
        message="Candidate analysis generated successfully.",
        data=applicant,
    )


@router.post(
    "/{applicant_id}/emails/{email_type}",
    response_model=CandidateEmailResponse,
)
async def send_candidate_email(
    applicant_id: UUID,
    email_type: CandidateEmailType,
    service: AutomatedEmailServiceDependency,
    current_user: CurrentUserDependency,
) -> CandidateEmailResponse:
    email_log = await service.send_candidate_email(
        applicant_id,
        email_type,
        actor_user_id=current_user.id,
    )
    return CandidateEmailResponse(
        message="Candidate email sent successfully.",
        data=email_log,
    )


@router.patch("/{applicant_id}", response_model=ApplicantResponse)
async def update_applicant(
    applicant_id: UUID,
    payload: ApplicantUpdate,
    service: ApplicantServiceDependency,
    _: CurrentUserDependency,
) -> ApplicantResponse:
    applicant = await service.update_applicant(applicant_id, payload)
    return ApplicantResponse(
        message="Applicant updated successfully.",
        data=applicant,
    )


@router.patch("/{applicant_id}/status", response_model=ApplicantResponse)
async def update_applicant_status(
    applicant_id: UUID,
    payload: ApplicantStatusUpdate,
    service: ApplicantServiceDependency,
    current_user: CurrentUserDependency,
) -> ApplicantResponse:
    applicant = await service.update_status(
        applicant_id,
        payload,
        actor_user_id=current_user.id,
    )
    return ApplicantResponse(
        message="Applicant status updated successfully.",
        data=applicant,
    )


@router.delete("/{applicant_id}", response_model=ApplicantDeleteResponse)
async def delete_applicant(
    applicant_id: UUID,
    service: ApplicantServiceDependency,
    _: CurrentUserDependency,
) -> ApplicantDeleteResponse:
    await service.delete_applicant(applicant_id)
    return ApplicantDeleteResponse(message="Applicant deleted successfully.")
