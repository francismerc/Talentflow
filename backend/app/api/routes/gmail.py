import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from app.api.dependencies import CurrentUserDependency, GmailServiceDependency
from app.core.config import get_settings
from app.schemas.gmail import (
    GmailAuthorizationResponse,
    GmailConnectionResponse,
    GmailDisconnectResponse,
    GmailProcessRequest,
    GmailProcessResponse,
    GmailSettingsUpdate,
)

router = APIRouter(prefix="/gmail")
logger = logging.getLogger(__name__)


@router.get("/status", response_model=GmailConnectionResponse)
async def get_gmail_status(
    service: GmailServiceDependency,
    current_user: CurrentUserDependency,
) -> GmailConnectionResponse:
    connection = await service.get_connection(current_user.id)
    return GmailConnectionResponse(
        message="Gmail connection status retrieved successfully.",
        data=connection,
    )


@router.get("/oauth/authorize", response_model=GmailAuthorizationResponse)
async def authorize_gmail(
    service: GmailServiceDependency,
    current_user: CurrentUserDependency,
) -> GmailAuthorizationResponse:
    authorization = service.create_authorization(current_user.id)
    return GmailAuthorizationResponse(
        message="Gmail authorization URL created successfully.",
        data=authorization,
    )


@router.get("/oauth/callback", include_in_schema=False)
async def gmail_oauth_callback(
    service: GmailServiceDependency,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> RedirectResponse:
    frontend_url = get_settings().frontend_url.rstrip("/")
    if error or not code or not state:
        query = urlencode({"gmail": "error", "reason": error or "missing_oauth_data"})
        return RedirectResponse(f"{frontend_url}/settings?{query}")

    try:
        await service.complete_oauth(code, state)
    except Exception as exception:
        logger.warning("Gmail OAuth callback failed: %s", exception)
        query = urlencode({"gmail": "error"})
        return RedirectResponse(f"{frontend_url}/settings?{query}")
    return RedirectResponse(f"{frontend_url}/settings?gmail=connected")


@router.delete("/connection", response_model=GmailDisconnectResponse)
async def disconnect_gmail(
    service: GmailServiceDependency,
    current_user: CurrentUserDependency,
) -> GmailDisconnectResponse:
    await service.disconnect(current_user.id)
    return GmailDisconnectResponse(message="Gmail account disconnected successfully.")


@router.patch("/settings", response_model=GmailConnectionResponse)
async def update_gmail_settings(
    payload: GmailSettingsUpdate,
    service: GmailServiceDependency,
    current_user: CurrentUserDependency,
) -> GmailConnectionResponse:
    connection = await service.update_settings(
        current_user.id,
        send_acknowledgment_emails=payload.send_acknowledgment_emails,
    )
    return GmailConnectionResponse(
        message="Gmail settings updated successfully.",
        data=connection,
    )


@router.post("/process", response_model=GmailProcessResponse)
async def process_gmail_inbox(
    payload: GmailProcessRequest,
    service: GmailServiceDependency,
    current_user: CurrentUserDependency,
) -> GmailProcessResponse:
    result = await service.process_inbox(
        current_user.id,
        max_messages=payload.max_messages,
    )
    return GmailProcessResponse(
        message="Gmail inbox processing completed.",
        data=result,
    )
