import pytest

from app.services.reports import ReportService

pytestmark = pytest.mark.anyio


class FakeReportQueries:
    async def get_overview(self, *, months: int) -> dict:
        return {
            "months": months,
            "period_start": "2026-01-01",
            "period_end": "2026-06-10T00:00:00Z",
            "total_applications": 12,
            "open_positions": 3,
            "average_candidate_score": "84.5",
            "shortlisted_rate": "25.0",
            "monthly_applications": [
                {
                    "month": "Jun",
                    "month_start": "2026-06-01T00:00:00Z",
                    "applications": 12,
                    "shortlisted": 3,
                }
            ],
            "status_distribution": [
                {"status": "new", "count": 9},
                {"status": "shortlisted", "count": 3},
            ],
            "top_skills": [{"skill": "React", "count": 8}],
            "top_positions": [
                {
                    "job_id": "10000000-0000-4000-8000-000000000001",
                    "title": "Frontend Engineer",
                    "count": 7,
                }
            ],
        }


async def test_report_service_normalizes_metrics_and_builds_summary() -> None:
    service = ReportService(FakeReportQueries())  # type: ignore[arg-type]

    result = await service.get_overview(months=6)

    assert result.average_candidate_score == 84.5
    assert result.shortlisted_rate == 25
    assert result.top_skills[0].skill == "React"
    assert "Frontend Engineer attracted the most applicants" in result.summary
