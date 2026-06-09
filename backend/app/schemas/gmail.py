from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class GmailConnection(BaseModel):
    oauth_configured: bool
    connected: bool
    gmail_address: str | None = None
    scopes: list[str] = Field(default_factory=list)
    status: str = "disconnected"
    last_error: str | None = None
    last_synced_at: datetime | None = None
    token_expires_at: datetime | None = None
    send_acknowledgment_emails: bool = False


class GmailConnectionResponse(BaseModel):
    success: bool = True
    message: str
    data: GmailConnection


class GmailAuthorization(BaseModel):
    authorization_url: HttpUrl


class GmailAuthorizationResponse(BaseModel):
    success: bool = True
    message: str
    data: GmailAuthorization


class GmailDisconnectResponse(BaseModel):
    success: bool = True
    message: str


class GmailSettingsUpdate(BaseModel):
    send_acknowledgment_emails: bool


class GmailProcessRequest(BaseModel):
    max_messages: int = Field(default=25, ge=1, le=100)


class GmailProcessResult(BaseModel):
    messages_scanned: int = 0
    messages_processed: int = 0
    attachments_stored: int = 0
    duplicates_skipped: int = 0
    unsupported_skipped: int = 0
    errors: int = 0


class GmailProcessResponse(BaseModel):
    success: bool = True
    message: str
    data: GmailProcessResult
