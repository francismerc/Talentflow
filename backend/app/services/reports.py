from typing import Any

from app.database.queries.reports import ReportQueries
from app.schemas.reports import RecruitmentReport


class ReportService:
    def __init__(self, queries: ReportQueries) -> None:
        self._queries = queries

    async def get_overview(self, *, months: int) -> RecruitmentReport:
        record = await self._queries.get_overview(months=months)
        values = {
            **record,
            "average_candidate_score": self._optional_float(
                record.get("average_candidate_score")
            ),
            "shortlisted_rate": float(record.get("shortlisted_rate") or 0),
        }
        values["summary"] = self._build_summary(values)
        return RecruitmentReport.model_validate(values)

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        return float(value) if value is not None else None

    @staticmethod
    def _build_summary(values: dict[str, Any]) -> str:
        total = int(values.get("total_applications") or 0)
        months = int(values.get("months") or 0)
        if total == 0:
            return (
                f"No applications were received during the selected "
                f"{months}-month reporting period."
            )

        top_positions = values.get("top_positions") or []
        top_position = (
            str(top_positions[0].get("title"))
            if top_positions and isinstance(top_positions[0], dict)
            else "No position"
        )
        average_score = values.get("average_candidate_score")
        score_text = (
            f"The average analyzed candidate score was {float(average_score):.1f}."
            if average_score is not None
            else "No current AI scores are available for this period."
        )
        return (
            f"{total} applications were received over the last {months} months. "
            f"{top_position} attracted the most applicants. "
            f"{float(values.get('shortlisted_rate') or 0):.1f}% of applicants "
            f"are currently shortlisted or further advanced. {score_text}"
        )
