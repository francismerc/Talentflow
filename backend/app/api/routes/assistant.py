from fastapi import APIRouter

from app.api.dependencies import AssistantServiceDependency, CurrentUserDependency
from app.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
)

router = APIRouter(prefix="/assistant")


@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_assistant(
    payload: AssistantChatRequest,
    service: AssistantServiceDependency,
    _: CurrentUserDependency,
) -> AssistantChatResponse:
    result = await service.chat(payload)
    return AssistantChatResponse(
        message="Assistant response generated successfully.",
        data=result,
    )
