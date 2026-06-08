import asyncio

from app.database.queries.email_attachments import EmailAttachmentQueries
from app.database.queries.email_logs import EmailLogQueries
from tests.database.fakes import FakeQueryBuilder, FakeResponse, FakeSupabaseClient


def test_email_log_duplicate_lookup_scopes_to_incoming_messages() -> None:
    builder = FakeQueryBuilder(FakeResponse(data={"id": "log-1"}))
    client = FakeSupabaseClient(builder)
    queries = EmailLogQueries(client)

    result = asyncio.run(
        queries.get_incoming_by_gmail_message_id("gmail-message-1")
    )

    assert result == {"id": "log-1"}
    assert client.requested_tables == ["email_logs"]
    assert ("eq", ("gmail_message_id", "gmail-message-1"), {}) in builder.calls
    assert ("eq", ("direction", "incoming"), {}) in builder.calls


def test_email_attachment_create_uses_attachment_table() -> None:
    record = {
        "id": "attachment-1",
        "email_log_id": "log-1",
        "gmail_attachment_id": "gmail-attachment-1",
        "file_name": "resume.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 100,
        "storage_bucket": "resumes",
        "storage_path": "user/message/resume.pdf",
        "status": "stored",
    }
    builder = FakeQueryBuilder(FakeResponse(data=[record]))
    client = FakeSupabaseClient(builder)
    queries = EmailAttachmentQueries(client)

    result = asyncio.run(queries.create(record))

    assert result == record
    assert client.requested_tables == ["email_attachments"]
    assert ("insert", (record,), {}) in builder.calls


def test_lists_only_stored_unassigned_attachments() -> None:
    builder = FakeQueryBuilder(FakeResponse(data=[]))
    client = FakeSupabaseClient(builder)
    queries = EmailAttachmentQueries(client)

    result = asyncio.run(queries.list_stored_for_processing(limit=25))

    assert result == []
    assert ("eq", ("status", "stored"), {}) in builder.calls
    assert ("is_", ("email_logs.applicant_id", "null"), {}) in builder.calls
    assert ("limit", (25,), {}) in builder.calls
