from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CandidateEmailType(StrEnum):
    ACKNOWLEDGMENT = "acknowledgment"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"


class CandidateEmailLog(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    email_type: CandidateEmailType
    recipient_email: str
    subject: str
    status: str
    error_message: str | None = None
    sent_at: datetime | None = None
    created_at: datetime


class CandidateEmailResponse(BaseModel):
    success: bool = True
    message: str
    data: CandidateEmailLog
