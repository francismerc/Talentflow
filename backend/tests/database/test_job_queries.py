from uuid import UUID

import pytest

from app.database.queries.common import Pagination
from app.database.queries.jobs import JobFilters, JobQueries, JobStatus
from tests.database.fakes import FakeQueryBuilder, FakeResponse, FakeSupabaseClient

pytestmark = pytest.mark.anyio


async def test_list_jobs_applies_filters_and_pagination() -> None:
    builder = FakeQueryBuilder(FakeResponse(data=[{"id": "job-1"}], count=12))
    client = FakeSupabaseClient(builder)
    queries = JobQueries(client)  # type: ignore[arg-type]

    result = await queries.list(
        filters=JobFilters(
            search="Frontend",
            status=JobStatus.ACTIVE,
            required_skill="React",
        ),
        pagination=Pagination(page=2, page_size=5),
    )

    assert client.requested_tables == ["jobs"]
    assert result.items == [{"id": "job-1"}]
    assert result.total == 12
    assert ("ilike", ("title", "%Frontend%"), {}) in builder.calls
    assert ("eq", ("status", "active"), {}) in builder.calls
    assert ("contains", ("required_skills", ["React"]), {}) in builder.calls
    assert ("range", (5, 9), {}) in builder.calls


async def test_get_job_returns_none_when_record_does_not_exist() -> None:
    builder = FakeQueryBuilder(None)
    client = FakeSupabaseClient(builder)

    result = await JobQueries(client).get_by_id(  # type: ignore[arg-type]
        UUID("00000000-0000-0000-0000-000000000000")
    )

    assert result is None


async def test_create_job_returns_first_mutation_row() -> None:
    row = {"id": "job-1", "title": "Frontend Engineer"}
    builder = FakeQueryBuilder(FakeResponse(data=[row]))
    client = FakeSupabaseClient(builder)

    result = await JobQueries(client).create(  # type: ignore[arg-type]
        {"title": "Frontend Engineer"}
    )

    assert result == row
    assert ("insert", ({"title": "Frontend Engineer"},), {}) in builder.calls


async def test_update_job_returns_none_when_no_row_is_updated() -> None:
    builder = FakeQueryBuilder(FakeResponse(data=[]))
    client = FakeSupabaseClient(builder)

    result = await JobQueries(client).update(  # type: ignore[arg-type]
        UUID("00000000-0000-0000-0000-000000000000"),
        {"title": "Updated"},
    )

    assert result is None
