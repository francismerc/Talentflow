# TalentFlow AI Backend

FastAPI service for TalentFlow AI. The backend provides typed configuration,
CORS, standardized error responses, Supabase repositories, authenticated write
APIs, and integration service layers.

## Requirements

- Python 3.12+

## Local setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.

- Health: `GET /api/v1/health`
- OpenAPI: `http://localhost:8000/docs`

## Jobs API

```text
GET    /api/v1/jobs
GET    /api/v1/jobs/{job_id}
POST   /api/v1/jobs
PATCH  /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}
```

Job reads are public during the current frontend integration stage. Create,
update, and delete require a valid Supabase access token:

```http
Authorization: Bearer <supabase-access-token>
```

## Applicants API

```text
GET    /api/v1/applicants
GET    /api/v1/applicants/{applicant_id}
POST   /api/v1/applicants
PATCH  /api/v1/applicants/{applicant_id}
PATCH  /api/v1/applicants/{applicant_id}/status
DELETE /api/v1/applicants/{applicant_id}
```

Applicant writes require a valid Supabase access token. Status changes use a
PostgreSQL RPC so the applicant record and timeline event update atomically.

## Gmail OAuth setup

The Gmail integration uses the `gmail.modify` scope so the recruitment agent can
read messages and attachments, mark messages as processed, and send mail.

1. Create a Google Cloud OAuth web application.
2. Add this authorized redirect URI:
   `http://localhost:8000/api/v1/gmail/oauth/callback`
3. Generate backend-only secrets:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

4. Put the generated values in `backend/.env` as
   `GOOGLE_OAUTH_STATE_SECRET` and `GOOGLE_TOKEN_ENCRYPTION_KEY`.
5. Add the Google client ID and client secret to `backend/.env`.
6. Apply the Gmail migrations in timestamp order:
   - `supabase/migrations/20260607090000_add_gmail_integrations.sql`
   - `supabase/migrations/20260608100000_add_email_attachments_and_resume_storage.sql`

Available endpoints:

```text
GET    /api/v1/gmail/status
GET    /api/v1/gmail/oauth/authorize
GET    /api/v1/gmail/oauth/callback
POST   /api/v1/gmail/process
DELETE /api/v1/gmail/connection
```

Status, authorization, and disconnect require a valid Supabase access token.
OAuth credentials are encrypted before storage and are never returned by the
API.

The process endpoint scans unread inbox messages with PDF, DOC, or DOCX
attachments. It refreshes expired Google access tokens, stores resume files in
the private `resumes` bucket, writes idempotent email and attachment records,
and removes the Gmail `UNREAD` label after successful processing.

## Resume processing

Apply `supabase/migrations/20260608150000_add_resume_processing_workflow.sql`,
then use:

```text
POST /api/v1/resumes/process
```

The endpoint parses pending PDF and DOCX files locally, extracts deterministic
candidate fields, matches the email subject to an active job title, and creates
the applicant through one atomic PostgreSQL function. Files that are scanned,
password-protected, legacy DOC, or missing a confident active-job match are
marked `needs_review` instead of being assigned incorrectly.

Legacy binary DOC parsing is intentionally deferred. Applicants should submit
PDF or DOCX for automatic processing.

## Validation

```bash
ruff check .
pytest
```

Gemini and resume-processing services will be implemented in their respective
development phases.

## Database queries

Read queries are grouped by feature under `app/database/queries/`:

- `jobs.py`: paginated job lists and job details
- `applicants.py`: applicant search, filters, score ranges, and details
- `common.py`: bounded pagination and safe search normalization

Routes should not call Supabase directly. The intended flow is:

```text
API route -> service -> query/repository -> Supabase
```
