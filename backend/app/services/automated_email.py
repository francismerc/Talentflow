from typing import Any
from uuid import UUID

from app.core.config import Settings
from app.core.errors import ConflictError, IntegrationError, NotFoundError
from app.database.queries.applicants import ApplicantQueries
from app.database.queries.email_logs import EmailLogQueries
from app.email.templates import CandidateEmailTemplates
from app.gmail.service import GmailService
from app.schemas.emails import CandidateEmailLog, CandidateEmailType


class AutomatedEmailService:
    def __init__(
        self,
        *,
        applicants: ApplicantQueries,
        email_logs: EmailLogQueries,
        gmail: GmailService,
        settings: Settings,
        templates: CandidateEmailTemplates | None = None,
    ) -> None:
        self._applicants = applicants
        self._email_logs = email_logs
        self._gmail = gmail
        self._settings = settings
        self._templates = templates or CandidateEmailTemplates(
            company_name=settings.email_company_name,
            recruitment_team_name=settings.email_recruitment_team_name,
            careers_url=settings.email_careers_url,
        )

    async def send_candidate_email(
        self,
        applicant_id: UUID,
        email_type: CandidateEmailType,
        *,
        actor_user_id: UUID,
    ) -> CandidateEmailLog:
        context = await self._applicants.get_email_context(applicant_id)
        if context is None:
            raise NotFoundError("Applicant not found.")
        self._validate_email_type(context, email_type)

        connection = await self._gmail.get_connection(actor_user_id)
        if not connection.connected or not connection.gmail_address:
            raise ConflictError("Connect Gmail before sending candidate emails.")

        job = context.get("jobs")
        if not isinstance(job, dict):
            raise ConflictError("Applicant job information is unavailable.")
        template = self._templates.render(
            email_type,
            candidate_name=str(context["full_name"]),
            job_title=str(job["title"]),
        )
        reserved, owns_attempt = await self._email_logs.reserve_outgoing(
            applicant_id=applicant_id,
            idempotency_key=f"candidate:{applicant_id}:{email_type.value}",
            email_type=email_type.value,
            sender_email=connection.gmail_address,
            recipient_email=str(context["email"]),
            subject=template.subject,
        )
        if not owns_attempt:
            if reserved.get("status") == "sent":
                raise ConflictError(
                    f"The {email_type.value} email has already been sent."
                )
            raise ConflictError(
                f"The {email_type.value} email is already being sent."
            )

        email_log_id = UUID(str(reserved["id"]))
        try:
            result = await self._gmail.send_message(
                actor_user_id,
                recipient_email=str(context["email"]),
                subject=template.subject,
                text_body=template.text_body,
                html_body=template.html_body,
                reply_to=self._settings.email_reply_to,
                thread_id=(
                    str(context["source_email_thread_id"])
                    if context.get("source_email_thread_id")
                    else None
                ),
            )
            sent = await self._email_logs.mark_sent(
                email_log_id=email_log_id,
                actor_user_id=actor_user_id,
                gmail_message_id=result.message_id,
                gmail_thread_id=result.thread_id,
            )
        except Exception as exception:
            await self._email_logs.mark_failed(
                email_log_id,
                self._safe_error_message(exception),
            )
            raise
        return CandidateEmailLog.model_validate(sent)

    async def send_acknowledgment_if_enabled(
        self,
        applicant_id: UUID,
        *,
        actor_user_id: UUID,
    ) -> CandidateEmailLog | None:
        connection = await self._gmail.get_connection(actor_user_id)
        if not connection.connected or not connection.send_acknowledgment_emails:
            return None
        return await self.send_candidate_email(
            applicant_id,
            CandidateEmailType.ACKNOWLEDGMENT,
            actor_user_id=actor_user_id,
        )

    @staticmethod
    def _validate_email_type(
        context: dict[str, Any],
        email_type: CandidateEmailType,
    ) -> None:
        status = str(context.get("status") or "")
        required_status = {
            CandidateEmailType.SHORTLISTED: "shortlisted",
            CandidateEmailType.REJECTED: "rejected",
        }.get(email_type)
        if required_status and status != required_status:
            raise ConflictError(
                f"Applicant must be {required_status} before sending this email."
            )

    @staticmethod
    def _safe_error_message(exception: Exception) -> str:
        if isinstance(exception, (ConflictError, IntegrationError)):
            return exception.message
        return "Unexpected error while sending the candidate email."
