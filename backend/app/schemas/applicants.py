from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.emails import CandidateEmailLog


class ApplicantStatus(StrEnum):
    NEW = "new"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicantSortField(StrEnum):
    APPLIED_AT = "applied_at"
    FULL_NAME = "full_name"
    STATUS = "status"


class ApplicantCreate(BaseModel):
    job_id: UUID
    full_name: str = Field(min_length=1, max_length=160)
    email: str = Field(min_length=3, max_length=320)
    phone: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=200)
    education: list[dict[str, Any]] = Field(default_factory=list, max_length=50)
    experience: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    total_experience_years: float | None = Field(default=None, ge=0, le=99.9)
    skills: list[str] = Field(default_factory=list, max_length=100)
    resume_file_name: str | None = Field(default=None, max_length=255)
    resume_storage_path: str | None = Field(default=None, max_length=1000)
    resume_mime_type: str | None = None
    source_email_message_id: str | None = Field(default=None, max_length=255)
    source_email_thread_id: str | None = Field(default=None, max_length=255)
    applied_at: datetime | None = None

    @field_validator(
        "full_name",
        "email",
        "phone",
        "location",
        "resume_file_name",
        "resume_storage_path",
        "resume_mime_type",
        "source_email_message_id",
        "source_email_thread_id",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def validate_email_shape(cls, value: str) -> str:
        local, separator, domain = value.partition("@")
        if not separator or not local or "." not in domain:
            raise ValueError("A valid email address is required.")
        return value.casefold()

    @field_validator("skills")
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


class ApplicantUpdate(BaseModel):
    job_id: UUID | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, min_length=3, max_length=320)
    phone: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=200)
    education: list[dict[str, Any]] | None = Field(default=None, max_length=50)
    experience: list[dict[str, Any]] | None = Field(default=None, max_length=100)
    total_experience_years: float | None = Field(default=None, ge=0, le=99.9)
    skills: list[str] | None = Field(default=None, max_length=100)
    resume_file_name: str | None = Field(default=None, max_length=255)
    resume_storage_path: str | None = Field(default=None, max_length=1000)
    resume_mime_type: str | None = None

    @field_validator(
        "full_name",
        "email",
        "phone",
        "location",
        "resume_file_name",
        "resume_storage_path",
        "resume_mime_type",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def validate_email_shape(cls, value: str | None) -> str | None:
        return ApplicantCreate.validate_email_shape(value) if value is not None else None

    @field_validator("skills")
    @classmethod
    def normalize_skills(cls, skills: list[str] | None) -> list[str] | None:
        return ApplicantCreate.normalize_skills(skills) if skills is not None else None

    @model_validator(mode="after")
    def reject_empty_update(self) -> "ApplicantUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class ApplicantStatusUpdate(BaseModel):
    status: ApplicantStatus
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("note", mode="before")
    @classmethod
    def strip_note(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ApplicantJob(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    title: str
    required_skills: list[str] = Field(default_factory=list)
    location: str | None = None
    employment_type: str | None = None
    status: str | None = None


class ApplicantAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID | None = None
    model_name: str | None = None
    prompt_version: str | None = None
    score: float
    summary: str | None = None
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendation: str
    recommendation_reason: str | None = None
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    is_current: bool
    generated_at: datetime | None = None


class ApplicantTimelineItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    actor_user_id: UUID | None
    event_type: str
    title: str
    description: str | None
    metadata: dict[str, Any]
    occurred_at: datetime


class ApplicantSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    job_id: UUID
    full_name: str
    email: str
    phone: str | None
    location: str | None
    status: ApplicantStatus
    applied_at: datetime
    created_at: datetime
    job: ApplicantJob | None = None
    current_analysis: ApplicantAnalysis | None = None


class ApplicantDetail(ApplicantSummary):
    education: list[dict[str, Any]]
    experience: list[dict[str, Any]]
    total_experience_years: float | None
    skills: list[str]
    resume_file_name: str | None
    resume_storage_path: str | None
    resume_mime_type: str | None
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    updated_at: datetime
    timeline: list[ApplicantTimelineItem] = Field(default_factory=list)
    emails: list[CandidateEmailLog] = Field(default_factory=list)


class ApplicantResponse(BaseModel):
    success: bool = True
    message: str
    data: ApplicantDetail


class ApplicantListData(BaseModel):
    items: list[ApplicantSummary]
    page: int
    page_size: int
    total: int


class ApplicantListResponse(BaseModel):
    success: bool = True
    message: str
    data: ApplicantListData


class ApplicantDeleteResponse(BaseModel):
    success: bool = True
    message: str
