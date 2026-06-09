from fastapi import APIRouter

from app.api.dependencies import (
    AssistantActionServiceDependency,
    AssistantServiceDependency,
    CurrentUserDependency,
)
from app.schemas.assistant import (
    AssistantActionRequest,
    AssistantActionResponse,
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


@router.post("/actions", response_model=AssistantActionResponse)
async def execute_assistant_action(
    payload: AssistantActionRequest,
    service: AssistantActionServiceDependency,
    current_user: CurrentUserDependency,
) -> AssistantActionResponse:
    result = await service.execute(
        payload,
        actor_user_id=current_user.id,
    )
    return AssistantActionResponse(
        message="Assistant action completed successfully.",
        data=result,
    )
