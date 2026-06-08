from app.resume.extractor import CandidateExtractor


def test_extracts_candidate_fields_with_job_skills() -> None:
    candidate = CandidateExtractor().extract(
        """
        FRANCIS MERC BARLUADO
        francis@example.com | +63 917 123 4567
        Location: Manila, Philippines

        Skills
        React, TypeScript, Next.js, Tailwind CSS

        Experience
        Frontend Engineer at Acme
        5 years of professional experience

        Education
        BS Information Technology - Example University
        """,
        fallback_email="sender@example.com",
        file_name="resume.pdf",
        job_skills=["React", "TypeScript", "Next.js"],
    )

    assert candidate.full_name == "Francis Merc Barluado"
    assert candidate.email == "francis@example.com"
    assert candidate.phone == "+63 917 123 4567"
    assert candidate.location == "Manila, Philippines"
    assert candidate.total_experience_years == 5
    assert set(candidate.skills) == {"Tailwind CSS", "TypeScript", "Next.js", "React"}
    assert candidate.experience
    assert candidate.education


def test_uses_sender_and_file_name_as_fallbacks() -> None:
    candidate = CandidateExtractor().extract(
        "Professional summary\nExperienced product contributor with strong communication.",
        fallback_email="candidate@example.com",
        file_name="Jane_Doe_Resume.pdf",
        job_skills=[],
    )

    assert candidate.email == "candidate@example.com"
    assert candidate.full_name == "Jane Doe"
