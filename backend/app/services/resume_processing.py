from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.database.queries.applicants import ApplicantQueries
from app.database.queries.email_attachments import EmailAttachmentQueries
from app.database.queries.jobs import JobQueries
from app.resume.extractor import CandidateExtractor
from app.resume.job_matcher import JobMatcher
from app.resume.parser import ResumeParser, ResumeParsingError
from app.schemas.resumes import ResumeProcessResult
from app.services.automated_email import AutomatedEmailService
from app.services.resume_storage import ResumeStorageService


class ResumeProcessingService:
    def __init__(
        self,
        *,
        attachments: EmailAttachmentQueries,
        applicants: ApplicantQueries,
        jobs: JobQueries,
        storage: ResumeStorageService,
        parser: ResumeParser | None = None,
        extractor: CandidateExtractor | None = None,
        job_matcher: JobMatcher | None = None,
        automated_email: AutomatedEmailService | None = None,
    ) -> None:
        self._attachments = attachments
        self._applicants = applicants
        self._jobs = jobs
        self._storage = storage
        self._parser = parser or ResumeParser()
        self._extractor = extractor or CandidateExtractor()
        self._job_matcher = job_matcher or JobMatcher()
        self._automated_email = automated_email

    async def process_pending(
        self,
        *,
        max_attachments: int = 25,
        actor_user_id: UUID | None = None,
    ) -> ResumeProcessResult:
        records = await self._attachments.list_stored_for_processing(
            limit=max_attachments
        )
        active_jobs = await self._jobs.list_active_for_matching()
        result = ResumeProcessResult(attachments_scanned=len(records))
        processed_email_logs: set[str] = set()

        for record in records:
            attachment_id = str(record["id"])
            email_log = self._email_log(record)
            email_log_id = str(record["email_log_id"])
            if email_log_id in processed_email_logs:
                await self._mark_needs_review(
                    attachment_id,
                    "Multiple resume attachments were found in one email.",
                )
                result.needs_review += 1
                continue

            job_match = self._job_matcher.match(
                str(email_log.get("subject") or ""),
                active_jobs,
            )
            if job_match is None:
                await self._mark_needs_review(
                    attachment_id,
                    "No active job title matched the application email subject.",
                )
                result.needs_review += 1
                continue

            try:
                content = await self._storage.download(str(record["storage_path"]))
                resume_text = self._parser.extract_text(
                    content,
                    str(record["mime_type"]),
                )
                candidate = self._extractor.extract(
                    resume_text,
                    fallback_email=str(email_log["sender_email"]),
                    file_name=str(record["file_name"]),
                    job_skills=job_match.required_skills,
                )
                applicant_id = await self._applicants.create_from_resume(
                    attachment_id=UUID(attachment_id),
                    job_id=job_match.job_id,
                    full_name=candidate.full_name,
                    email=candidate.email,
                    phone=candidate.phone,
                    location=candidate.location,
                    education=candidate.education,
                    experience=candidate.experience,
                    total_experience_years=candidate.total_experience_years,
                    skills=candidate.skills,
                    resume_text=resume_text,
                )
                processed_email_logs.add(email_log_id)
                result.applicants_created += 1
                if self._automated_email and actor_user_id:
                    try:
                        acknowledgment = (
                            await self._automated_email.send_acknowledgment_if_enabled(
                                applicant_id,
                                actor_user_id=actor_user_id,
                            )
                        )
                        if acknowledgment is not None:
                            result.acknowledgments_sent += 1
                    except Exception:
                        # Applicant creation is authoritative; delivery failures are logged.
                        result.acknowledgment_errors += 1
            except ResumeParsingError as exception:
                await self._mark_needs_review(attachment_id, str(exception))
                result.needs_review += 1
            except Exception:
                await self._attachments.update(
                    attachment_id,
                    {
                        "status": "failed",
                        "error_message": (
                            "Unexpected error while creating the applicant record."
                        ),
                    },
                )
                result.failed += 1
        return result

    async def _mark_needs_review(
        self,
        attachment_id: str,
        reason: str,
    ) -> None:
        await self._attachments.update(
            attachment_id,
            {
                "status": "needs_review",
                "error_message": reason[:1000],
                "parsed_at": datetime.now(UTC).isoformat(),
            },
        )

    @staticmethod
    def _email_log(record: dict[str, Any]) -> dict[str, Any]:
        email_log = record.get("email_logs")
        if isinstance(email_log, list):
            return email_log[0] if email_log else {}
        return email_log if isinstance(email_log, dict) else {}
