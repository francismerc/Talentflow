from app.resume.job_matcher import JobMatcher

JOBS = [
    {
        "id": "10000000-0000-4000-8000-000000000001",
        "title": "Frontend Engineer",
        "required_skills": ["React", "TypeScript"],
    },
    {
        "id": "10000000-0000-4000-8000-000000000002",
        "title": "Backend Engineer",
        "required_skills": ["Python", "FastAPI"],
    },
]


def test_matches_job_title_in_application_subject() -> None:
    match = JobMatcher().match("Application for Frontend Developer", JOBS)

    assert match is not None
    assert match.title == "Frontend Engineer"


def test_returns_none_for_unrelated_subject() -> None:
    match = JobMatcher().match("General employment inquiry", JOBS)

    assert match is None
