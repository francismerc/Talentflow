from app.email.templates import CandidateEmailTemplates
from app.schemas.emails import CandidateEmailType


def test_candidate_template_escapes_html_and_has_plain_text() -> None:
    template = CandidateEmailTemplates(
        company_name="TalentFlow AI",
        recruitment_team_name="Talent Team",
    ).render(
        CandidateEmailType.ACKNOWLEDGMENT,
        candidate_name="<Candidate>",
        job_title="Frontend Engineer",
    )

    assert template.subject == "Application received - Frontend Engineer"
    assert "Hello <Candidate>" in template.text_body
    assert "Hello &lt;Candidate&gt;" in template.html_body
    assert "Hiring decisions are reviewed by people." in template.html_body
