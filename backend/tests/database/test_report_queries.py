import asyncio

from app.database.queries.reports import ReportQueries
from tests.database.fakes import FakeQueryBuilder, FakeResponse, FakeSupabaseClient


def test_report_query_calls_bounded_database_rpc() -> None:
    payload = {"months": 6, "total_applications": 12}
    builder = FakeQueryBuilder(FakeResponse(data=payload))
    client = FakeSupabaseClient(builder)
    queries = ReportQueries(client)  # type: ignore[arg-type]

    result = asyncio.run(queries.get_overview(months=6))

    assert result == payload
    assert client.requested_tables == ["rpc:get_recruitment_report"]
    assert (
        "rpc",
        ("get_recruitment_report", {"p_months": 6}),
        {},
    ) in builder.calls
