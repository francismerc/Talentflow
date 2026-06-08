from uuid import UUID

import pytest

from app.database.queries.applicants import ApplicantFilters, ApplicantQueries
from app.schemas.applicants import ApplicantStatus
from tests.database.fakes import FakeQueryBuilder, FakeResponse, FakeSupabaseClient

pytestmark = pytest.mark.anyio


async def test_score_filter_uses_inner_ai_analysis_join() -> None:
    builder = FakeQueryBuilder(FakeResponse(data=[], count=0))
    client = FakeSupabaseClient(builder)
    queries = ApplicantQueries(client)  # type: ignore[arg-type]

    await queries.list(
        filters=ApplicantFilters(
            search="Maya,(Chen)",
            minimum_score=85,
            maximum_score=95,
        )
    )

    select_call = next(call for call in builder.calls if call[0] == "select")
    assert "applicant_ai_analyses!inner" in select_call[1][0]
    assert (
        "or_",
        ("full_name.ilike.%MayaChen%,email.ilike.%MayaChen%",),
        {},
    ) in builder.calls
    assert ("gte", ("applicant_ai_analyses.score", 85), {}) in builder.calls
    assert ("lte", ("applicant_ai_analyses.score", 95), {}) in builder.calls


async def test_get_applicant_returns_none_when_record_does_not_exist() -> None:
    builder = FakeQueryBuilder(None)
    client = FakeSupabaseClient(builder)

    result = await ApplicantQueries(client).get_by_id(  # type: ignore[arg-type]
        UUID("00000000-0000-0000-0000-000000000000")
    )

    assert result is None


async def test_status_update_calls_atomic_rpc() -> None:
    builder = FakeQueryBuilder(FakeResponse(data=[{"id": "applicant-1"}]))
    client = FakeSupabaseClient(builder)
    queries = ApplicantQueries(client)  # type: ignore[arg-type]
    applicant_id = UUID("20000000-0000-4000-8000-000000000001")
    actor_id = UUID("90000000-0000-4000-8000-000000000001")

    result = await queries.update_status(
        applicant_id=applicant_id,
        status=ApplicantStatus.SHORTLISTED,
        actor_user_id=actor_id,
        title="Applicant shortlisted",
        description="Strong role fit.",
    )

    assert result == {"id": "applicant-1"}
    assert client.requested_tables == ["rpc:update_applicant_status"]
    rpc_call = next(call for call in builder.calls if call[0] == "rpc")
    assert rpc_call[1][1]["p_status"] == "shortlisted"
    assert rpc_call[1][1]["p_actor_user_id"] == str(actor_id)


async def test_create_applicant_returns_first_mutation_row() -> None:
    row = {"id": "applicant-1"}
    builder = FakeQueryBuilder(FakeResponse(data=[row]))
    client = FakeSupabaseClient(builder)

    result = await ApplicantQueries(client).create(  # type: ignore[arg-type]
        {"full_name": "Maya Chen"}
    )

    assert result == row


async def test_delete_applicant_uses_exact_count() -> None:
    builder = FakeQueryBuilder(FakeResponse(data=[], count=1))
    client = FakeSupabaseClient(builder)

    deleted = await ApplicantQueries(client).delete(  # type: ignore[arg-type]
        UUID("20000000-0000-4000-8000-000000000001")
    )

    assert deleted is True
    assert ("delete", (), {"count": "exact"}) in builder.calls


async def test_create_from_resume_calls_atomic_rpc() -> None:
    applicant_id = UUID("20000000-0000-4000-8000-000000000001")
    builder = FakeQueryBuilder(FakeResponse(data=str(applicant_id)))
    client = FakeSupabaseClient(builder)

    result = await ApplicantQueries(client).create_from_resume(  # type: ignore[arg-type]
        attachment_id=UUID("60000000-0000-4000-8000-000000000001"),
        job_id=UUID("10000000-0000-4000-8000-000000000001"),
        full_name="Francis Barluado",
        email="francis@example.com",
        phone=None,
        location=None,
        education=[],
        experience=[],
        total_experience_years=5,
        skills=["React"],
        resume_text="Resume text",
    )

    assert result == applicant_id
    assert client.requested_tables == ["rpc:create_applicant_from_resume"]
