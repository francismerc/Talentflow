from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import AsyncClient

from app.database.client import get_supabase_client
from app.database.queries.applicants import ApplicantQueries
from app.database.queries.jobs import JobQueries
from app.schemas.auth import AuthenticatedUser
from app.services.applicants import ApplicantService
from app.services.jobs import JobService

SupabaseClient = Annotated[AsyncClient, Depends(get_supabase_client)]
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


async def get_current_user(
    credentials: BearerCredentials,
    client: SupabaseClient,
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    try:
        response = await client.auth.get_user(credentials.credentials)
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
