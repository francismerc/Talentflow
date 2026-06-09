from dataclasses import dataclass
from html import escape

from app.schemas.emails import CandidateEmailType


@dataclass(frozen=True, slots=True)
class CandidateEmailTemplate:
    subject: str
    text_body: str
    html_body: str


class CandidateEmailTemplates:
    def __init__(
        self,
        *,
        company_name: str,
        recruitment_team_name: str,
        careers_url: str | None = None,
    ) -> None:
        self._company_name = company_name.strip() or "TalentFlow AI"
        self._team_name = recruitment_team_name.strip() or "Talent Acquisition Team"
        self._careers_url = careers_url.strip() if careers_url else None

    def render(
        self,
        email_type: CandidateEmailType,
        *,
        candidate_name: str,
        job_title: str,
    ) -> CandidateEmailTemplate:
        content = {
            CandidateEmailType.ACKNOWLEDGMENT: (
                f"We received your application for {job_title}. "
                "Our recruitment team will review your information and contact you "
                "if your background matches the next stage of the process."
            ),
            CandidateEmailType.SHORTLISTED: (
                f"We are pleased to let you know that your application for "
                f"{job_title} has been shortlisted. A recruiter will contact you "
                "with details about the next stage."
            ),
            CandidateEmailType.REJECTED: (
                f"Thank you for your interest in the {job_title} position. "
                "After careful review, we will not be progressing your application "
                "for this role. We appreciate the time you invested in applying."
            ),
        }[email_type]
        subject = {
            CandidateEmailType.ACKNOWLEDGMENT: (
                f"Application received - {job_title}"
            ),
            CandidateEmailType.SHORTLISTED: (
                f"Application update - {job_title}"
            ),
            CandidateEmailType.REJECTED: (
                f"Application update - {job_title}"
            ),
        }[email_type]

        safe_name = escape(candidate_name.strip() or "Candidate")
        safe_content = escape(content)
        safe_company = escape(self._company_name)
        safe_team = escape(self._team_name)
        careers_html = (
            f'<p style="margin:24px 0 0"><a href="{escape(self._careers_url, quote=True)}">'
            "View career opportunities</a></p>"
            if self._careers_url
            else ""
        )
        careers_text = (
            f"\n\nCareer opportunities: {self._careers_url}"
            if self._careers_url
            else ""
        )
        return CandidateEmailTemplate(
            subject=subject,
            text_body=(
                f"Hello {candidate_name.strip() or 'Candidate'},\n\n"
                f"{content}\n\n"
                f"Regards,\n{self._team_name}\n{self._company_name}"
                f"{careers_text}"
            ),
            html_body=(
                '<div style="font-family:Arial,sans-serif;max-width:640px;'
                'margin:0 auto;color:#1f2937;line-height:1.6">'
                f"<p>Hello {safe_name},</p>"
                f"<p>{safe_content}</p>"
                f"{careers_html}"
                '<p style="margin-top:32px">Regards,<br>'
                f"<strong>{safe_team}</strong><br>{safe_company}</p>"
                '<p style="margin-top:32px;color:#6b7280;font-size:12px">'
                "This message was sent by the recruitment team. "
                "Hiring decisions are reviewed by people.</p>"
                "</div>"
            ),
        )
