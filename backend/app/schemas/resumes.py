from pydantic import BaseModel, Field


class ResumeProcessRequest(BaseModel):
    max_attachments: int = Field(default=25, ge=1, le=100)


class ResumeProcessResult(BaseModel):
    attachments_scanned: int = 0
    applicants_created: int = 0
    needs_review: int = 0
    failed: int = 0
    acknowledgments_sent: int = 0
    acknowledgment_errors: int = 0


class ResumeProcessResponse(BaseModel):
    success: bool = True
    message: str
    data: ResumeProcessResult
