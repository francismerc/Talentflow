from uuid import UUID

import pytest

from app.resume.extractor import ExtractedCandidate
from app.resume.job_matcher import JobMatch
from app.resume.parser import ResumeParsingError
from app.services.resume_processing import ResumeProcessingService

pytestmark = pytest.mark.anyio

ATTACHMENT_ID = "60000000-0000-4000-8000-000000000001"
JOB_ID = UUID("10000000-0000-4000-8000-000000000002")


def attachment_record(subject: str = "Application for Frontend Engineer") -> dict:
    return {
        "id": ATTACHMENT_ID,
        "email_log_id": "50000000-0000-4000-8000-000000000001",
        "file_name": "resume.pdf",
        "mime_type": "application/pdf",
        "storage_path": "user/message/resume.pdf",
        "email_logs": {
            "sender_email": "candidate@example.com",
            "subject": subject,
        },
    }


class FakeAttachments:
    def __init__(self, records: list[dict]) -> None:
        self.records = records
        self.updates: list[tuple[str, dict]] = []

    async def list_stored_for_processing(self, *, limit: int) -> list[dict]:
        return self.records[:limit]

    async def update(self, attachment_id: str, values: dict) -> dict:
        self.updates.append((attachment_id, values))
        return values


class FakeApplicants:
    def __init__(self) -> None:
        self.created: dict | None = None

    async def create_from_resume(self, **values: object) -> UUID:
        self.created = values
        return UUID("20000000-0000-4000-8000-000000000001")


class FakeJobs:
    async def list_active_for_matching(self) -> list[dict]:
        return [
            {
                "id": str(JOB_ID),
                "title": "Frontend Engineer",
                "required_skills": ["React"],
            }
        ]


class FakeStorage:
    async def download(self, _: str) -> bytes:
        return b"resume-bytes"


class FakeParser:
    def __init__(self, error: bool = False) -> None:
        self.error = error

    def extract_text(self, _: bytes, __: str) -> str:
        if self.error:
            raise ResumeParsingError("Image-only resume.")
        return "Candidate Name\ncandidate@example.com\nReact experience"


class FakeExtractor:
    def extract(self, *_: object, **__: object) -> ExtractedCandidate:
        return ExtractedCandidate(
            full_name="Candidate Name",
            email="candidate@example.com",
            skills=["React"],
        )


class FakeJobMatcher:
    def __init__(self, matched: bool = True) -> None:
        self.matched = matched

    def match(self, *_: object) -> JobMatch | None:
        if not self.matched:
            return None
        return JobMatch(
            job_id=JOB_ID,
            title="Frontend Engineer",
            required_skills=["React"],
            confidence=1,
        )


async def test_process_pending_creates_applicant() -> None:
    applicants = FakeApplicants()
    service = ResumeProcessingService(  # type: ignore[arg-type]
        attachments=FakeAttachments([attachment_record()]),
        applicants=applicants,
        jobs=FakeJobs(),
        storage=FakeStorage(),
        parser=FakeParser(),
        extractor=FakeExtractor(),
        job_matcher=FakeJobMatcher(),
    )

    result = await service.process_pending()

    assert result.applicants_created == 1
    assert result.needs_review == 0
    assert applicants.created is not None
    assert applicants.created["job_id"] == JOB_ID
    assert applicants.created["full_name"] == "Candidate Name"


async def test_unmatched_job_is_marked_for_review() -> None:
    attachments = FakeAttachments([attachment_record("General application")])
    service = ResumeProcessingService(  # type: ignore[arg-type]
        attachments=attachments,
        applicants=FakeApplicants(),
        jobs=FakeJobs(),
        storage=FakeStorage(),
        parser=FakeParser(),
        extractor=FakeExtractor(),
        job_matcher=FakeJobMatcher(matched=False),
    )

    result = await service.process_pending()

    assert result.needs_review == 1
    assert attachments.updates[0][1]["status"] == "needs_review"


async def test_unreadable_resume_is_marked_for_review() -> None:
    attachments = FakeAttachments([attachment_record()])
    service = ResumeProcessingService(  # type: ignore[arg-type]
        attachments=attachments,
        applicants=FakeApplicants(),
        jobs=FakeJobs(),
        storage=FakeStorage(),
        parser=FakeParser(error=True),
        extractor=FakeExtractor(),
        job_matcher=FakeJobMatcher(),
    )

    result = await service.process_pending()

    assert result.needs_review == 1
    assert attachments.updates[0][1]["error_message"] == "Image-only resume."
