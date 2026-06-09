from fastapi import APIRouter

from app.api.dependencies import (
    CurrentUserDependency,
    ResumeProcessingServiceDependency,
)
from app.schemas.resumes import (
    ResumeProcessRequest,
    ResumeProcessResponse,
)

router = APIRouter(prefix="/resumes")


@router.post("/process", response_model=ResumeProcessResponse)
async def process_stored_resumes(
    payload: ResumeProcessRequest,
    service: ResumeProcessingServiceDependency,
    current_user: CurrentUserDependency,
) -> ResumeProcessResponse:
    result = await service.process_pending(
        max_attachments=payload.max_attachments,
        actor_user_id=current_user.id,
    )
    return ResumeProcessResponse(
        message="Stored resume processing completed.",
        data=result,
    )
