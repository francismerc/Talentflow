from datetime import UTC, date, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user, get_report_service
from app.main import app
from app.schemas.auth import AuthenticatedUser
from app.schemas.reports import RecruitmentReport

USER_ID = UUID("90000000-0000-4000-8000-000000000001")


class FakeReportService:
    async def get_overview(self, *, months: int) -> RecruitmentReport:
        return RecruitmentReport(
            months=months,
            period_start=date(2026, 1, 1),
            period_end=datetime(2026, 6, 10, tzinfo=UTC),
            total_applications=12,
            open_positions=3,
            average_candidate_score=84.5,
            shortlisted_rate=25,
            monthly_applications=[],
            status_distribution=[],
            top_skills=[],
            top_positions=[],
            summary="Twelve applications were received.",
        )


def get_fake_report_service() -> FakeReportService:
    return FakeReportService()


def get_fake_current_user() -> AuthenticatedUser:
    return AuthenticatedUser(id=USER_ID, email="recruiter@example.com")


app.dependency_overrides[get_report_service] = get_fake_report_service
app.dependency_overrides[get_current_user] = get_fake_current_user
client = TestClient(app)


def test_report_endpoint_returns_requested_period() -> None:
    response = client.get("/api/v1/reports/overview?months=12")

    assert response.status_code == 200
    assert response.json()["data"]["months"] == 12
    assert response.json()["data"]["total_applications"] == 12


def test_report_endpoint_rejects_invalid_period() -> None:
    response = client.get("/api/v1/reports/overview?months=25")

    assert response.status_code == 422
