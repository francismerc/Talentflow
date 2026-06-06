from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class JobStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class JobSortField(StrEnum):
    CREATED_AT = "created_at"
    TITLE = "title"
    STATUS = "status"


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=20_000)
    required_skills: list[str] = Field(default_factory=list, max_length=50)
    location: str | None = Field(default=None, max_length=200)
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    status: JobStatus = JobStatus.DRAFT

    @field_validator("title", "description", "location", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("required_skills")
    @classmethod
    def normalize_skills(cls, skills: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for skill in skills:
            clean_skill = " ".join(skill.strip().split())
            if not clean_skill:
                continue
            key = clean_skill.casefold()
            if key not in seen:
                normalized.append(clean_skill)
                seen.add(key)
        return normalized


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=20_000)
    required_skills: list[str] | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=200)
    employment_type: EmploymentType | None = None
    status: JobStatus | None = None

    @field_validator("title", "description", "location", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("required_skills")
    @classmethod
    def normalize_skills(cls, skills: list[str] | None) -> list[str] | None:
        return JobCreate.normalize_skills(skills) if skills is not None else None

    @model_validator(mode="after")
    def reject_empty_update(self) -> "JobUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class JobSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    title: str
    description: str
    required_skills: list[str]
    location: str | None
    employment_type: EmploymentType
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    applicant_count: int = 0


class JobCandidateAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    score: float
    recommendation: str
    recommendation_reason: str
    is_current: bool


class JobCandidate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    full_name: str
    email: str
    status: str
    applied_at: datetime
    applicant_ai_analyses: list[JobCandidateAnalysis] = Field(default_factory=list)


class JobDetail(JobSummary):
    created_by: UUID | None
    applicants: list[JobCandidate] = Field(default_factory=list)


class JobResponse(BaseModel):
    success: bool = True
    message: str
    data: JobDetail


class JobListData(BaseModel):
    items: list[JobSummary]
    page: int
    page_size: int
    total: int


class JobListResponse(BaseModel):
    success: bool = True
    message: str
    data: JobListData


class DeleteResponse(BaseModel):
    success: bool = True
    message: str
