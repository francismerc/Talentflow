from uuid import UUID

import pytest

from app.core.config import Settings
from app.core.errors import ConflictError
from app.gmail.service import GmailSendResult
from app.schemas.emails import CandidateEmailType
from app.schemas.gmail import GmailConnection
from app.services.automated_email import AutomatedEmailService

pytestmark = pytest.mark.anyio

APPLICANT_ID = UUID("20000000-0000-4000-8000-000000000001")
USER_ID = UUID("90000000-0000-4000-8000-000000000001")
EMAIL_LOG_ID = UUID("50000000-0000-4000-8000-000000000001")


class FakeApplicants:
    def __init__(self, status: str = "new") -> None:
        self.status = status

    async def get_email_context(self, _: UUID) -> dict:
        return {
            "id": str(APPLICANT_ID),
            "full_name": "Maya Chen",
            "email": "maya@example.com",
            "status": self.status,
            "source_email_thread_id": "thread-1",
            "jobs": {"id": "job-1", "title": "Frontend Engineer"},
        }


class FakeEmailLogs:
    def __init__(self, status: str = "queued") -> None:
        self.status = status
        self.failed = False

    async def reserve_outgoing(self, **_: object) -> tuple[dict, bool]:
        return (
            {"id": str(EMAIL_LOG_ID), "status": self.status},
            self.status != "sent",
        )

    async def mark_sent(self, **_: object) -> dict:
        return {
            "id": str(EMAIL_LOG_ID),
            "email_type": "acknowledgment",
            "recipient_email": "maya@example.com",
            "subject": "Application received - Frontend Engineer",
            "status": "sent",
            "error_message": None,
            "sent_at": "2026-06-09T00:00:00Z",
            "created_at": "2026-06-09T00:00:00Z",
        }

    async def mark_failed(self, *_: object) -> dict:
        self.failed = True
        return {}


class FakeGmail:
    async def get_connection(self, _: UUID) -> GmailConnection:
        return GmailConnection(
            oauth_configured=True,
            connected=True,
            gmail_address="recruitment@example.com",
            status="connected",
            send_acknowledgment_emails=True,
        )

    async def send_message(self, _: UUID, **values: object) -> GmailSendResult:
        assert values["recipient_email"] == "maya@example.com"
        assert values["thread_id"] == "thread-1"
        return GmailSendResult(message_id="gmail-1", thread_id="thread-1")


async def test_sends_and_records_candidate_email() -> None:
    service = AutomatedEmailService(  # type: ignore[arg-type]
        applicants=FakeApplicants(),
        email_logs=FakeEmailLogs(),
        gmail=FakeGmail(),
        settings=Settings(),
    )

    result = await service.send_candidate_email(
        APPLICANT_ID,
        CandidateEmailType.ACKNOWLEDGMENT,
        actor_user_id=USER_ID,
    )

    assert result.status == "sent"
    assert result.email_type is CandidateEmailType.ACKNOWLEDGMENT


async def test_prevents_duplicate_sent_email() -> None:
    service = AutomatedEmailService(  # type: ignore[arg-type]
        applicants=FakeApplicants(),
        email_logs=FakeEmailLogs(status="sent"),
        gmail=FakeGmail(),
        settings=Settings(),
    )

    with pytest.raises(ConflictError):
        await service.send_candidate_email(
            APPLICANT_ID,
            CandidateEmailType.ACKNOWLEDGMENT,
            actor_user_id=USER_ID,
        )


async def test_shortlist_email_requires_shortlisted_status() -> None:
    service = AutomatedEmailService(  # type: ignore[arg-type]
        applicants=FakeApplicants(status="new"),
        email_logs=FakeEmailLogs(),
        gmail=FakeGmail(),
        settings=Settings(),
    )

    with pytest.raises(ConflictError):
        await service.send_candidate_email(
            APPLICANT_ID,
            CandidateEmailType.SHORTLISTED,
            actor_user_id=USER_ID,
        )
