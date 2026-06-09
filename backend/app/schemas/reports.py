from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MonthlyApplications(BaseModel):
    month: str
    month_start: datetime
    applications: int = Field(ge=0)
    shortlisted: int = Field(ge=0)


class StatusDistribution(BaseModel):
    status: str
    count: int = Field(ge=0)


class SkillCount(BaseModel):
    skill: str
    count: int = Field(ge=0)


class PositionCount(BaseModel):
    job_id: UUID
    title: str
    count: int = Field(ge=0)


class RecruitmentReport(BaseModel):
    months: int = Field(ge=1, le=24)
    period_start: date
    period_end: datetime
    total_applications: int = Field(ge=0)
    open_positions: int = Field(ge=0)
    average_candidate_score: float | None = Field(default=None, ge=0, le=100)
    shortlisted_rate: float = Field(ge=0, le=100)
    monthly_applications: list[MonthlyApplications] = Field(default_factory=list)
    status_distribution: list[StatusDistribution] = Field(default_factory=list)
    top_skills: list[SkillCount] = Field(default_factory=list)
    top_positions: list[PositionCount] = Field(default_factory=list)
    summary: str


class RecruitmentReportResponse(BaseModel):
    success: bool = True
    message: str
    data: RecruitmentReport
