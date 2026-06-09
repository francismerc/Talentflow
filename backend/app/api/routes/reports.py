from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import CurrentUserDependency, ReportServiceDependency
from app.schemas.reports import RecruitmentReportResponse

router = APIRouter(prefix="/reports")


@router.get("/overview", response_model=RecruitmentReportResponse)
async def get_recruitment_report(
    service: ReportServiceDependency,
    _: CurrentUserDependency,
    months: Annotated[int, Query(ge=1, le=24)] = 6,
) -> RecruitmentReportResponse:
    report = await service.get_overview(months=months)
    return RecruitmentReportResponse(
        message="Recruitment report retrieved successfully.",
        data=report,
    )
