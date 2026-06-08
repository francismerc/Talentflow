from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import AsyncClient

from app.core.config import get_settings
from app.database.client import get_supabase_auth_client, get_supabase_client
from app.database.queries.applicants import ApplicantQueries
from app.database.queries.email_attachments import EmailAttachmentQueries
from app.database.queries.email_logs import EmailLogQueries
from app.database.queries.gmail_integrations import GmailIntegrationQueries
from app.database.queries.jobs import JobQueries
from app.gmail.service import GmailService
from app.schemas.auth import AuthenticatedUser
from app.services.applicants import ApplicantService
from app.services.jobs import JobService
from app.services.resume_processing import ResumeProcessingService
from app.services.resume_storage import ResumeStorageService

SupabaseClient = Annotated[AsyncClient, Depends(get_supabase_client)]
SupabaseAuthClient = Annotated[AsyncClient, Depends(get_supabase_auth_client)]
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(HTTPBearer(auto_error=False)),
]


def get_job_service(client: SupabaseClient) -> JobService:
    return JobService(JobQueries(client))


JobServiceDependency = Annotated[JobService, Depends(get_job_service)]


def get_applicant_service(client: SupabaseClient) -> ApplicantService:
    return ApplicantService(
        ApplicantQueries(client),
        JobQueries(client),
    )


ApplicantServiceDependency = Annotated[
    ApplicantService,
    Depends(get_applicant_service),
]


def get_gmail_service(client: SupabaseClient) -> GmailService:
    return GmailService(
        GmailIntegrationQueries(client),
        get_settings(),
        email_logs=EmailLogQueries(client),
        email_attachments=EmailAttachmentQueries(client),
        resume_storage=ResumeStorageService(client),
    )


GmailServiceDependency = Annotated[GmailService, Depends(get_gmail_service)]


def get_resume_processing_service(client: SupabaseClient) -> ResumeProcessingService:
    return ResumeProcessingService(
        attachments=EmailAttachmentQueries(client),
        applicants=ApplicantQueries(client),
        jobs=JobQueries(client),
        storage=ResumeStorageService(client),
    )


ResumeProcessingServiceDependency = Annotated[
    ResumeProcessingService,
    Depends(get_resume_processing_service),
]


async def get_current_user(
    credentials: BearerCredentials,
    auth_client: SupabaseAuthClient,
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    try:
        response = await auth_client.auth.get_user(credentials.credentials)
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        ) from exception

    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )
    return AuthenticatedUser(
        id=response.user.id,
        email=response.user.email,
    )


CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
