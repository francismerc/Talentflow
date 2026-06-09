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

## Gemini candidate analysis

Apply `supabase/migrations/20260608190000_add_atomic_ai_analysis.sql`, then add
Gemini settings to `backend/.env`:

```env
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT_SECONDS=30
```

Use:

```text
POST /api/v1/applicants/{applicant_id}/analysis
```

The endpoint requires a valid Supabase access token. It generates a structured
Gemini analysis, stores the result in `applicant_ai_analyses`, marks only the
latest analysis as current, and adds an applicant timeline event. AI output is
advisory only; it never changes applicant status or makes recruiter decisions.

## Automated candidate emails

Apply:

```text
supabase/migrations/20260609100000_add_automated_email_delivery.sql
```

Configure the recruitment identity in `backend/.env`:

```env
EMAIL_COMPANY_NAME=TalentFlow AI
EMAIL_RECRUITMENT_TEAM_NAME=Talent Acquisition Team
EMAIL_REPLY_TO=
EMAIL_CAREERS_URL=
```

Candidate emails use the recruiter Gmail connection and the existing
`gmail.modify` OAuth scope. Recruiters can enable acknowledgments in Settings.
Shortlist and rejection emails require an explicit confirmation after the
status update. Every attempt is idempotent and recorded in `email_logs`.

Available endpoint:

```text
POST /api/v1/applicants/{applicant_id}/emails/{email_type}
```

Supported email types are `acknowledgment`, `shortlisted`, and `rejected`.

## Recruiter assistant

The authenticated assistant endpoint is:

```text
POST /api/v1/assistant/chat
```

The assistant receives a bounded, read-only snapshot of jobs and applicants.
It can search candidates by skill or score, summarize the pipeline, explain
stored AI scores, and compare candidates. Raw resumes, email addresses, phone
numbers, Gmail tokens, and environment secrets are excluded from its context.
The chat endpoint cannot modify records. For explicit recruiter requests, it
may return one reviewable action proposal.

Confirmed actions use a separate authenticated endpoint:

```text
POST /api/v1/assistant/actions
```

Supported actions move an applicant under review, shortlist, move to
interview, mark hired, reject, or send an approved shortlisted/rejected email.
The frontend always requires recruiter confirmation before calling the action
endpoint. Status transitions, Gmail checks, idempotency, and timeline logging
remain enforced by the existing application services.

## Recruitment reports

Apply:

```text
supabase/migrations/20260610100000_add_recruitment_reports.sql
```

The authenticated reporting endpoint is:

```text
GET /api/v1/reports/overview?months=6
```

Supported ranges are 1 to 24 months. PostgreSQL performs the aggregation and
returns application totals, open positions, average current AI score,
shortlisted rate, monthly volume, status distribution, top skills, and top
positions. Candidate personal information is not included in report payloads.

## Validation

```bash
ruff check .
pytest
```

## Database queries

Read queries are grouped by feature under `app/database/queries/`:

- `jobs.py`: paginated job lists and job details
- `applicants.py`: applicant search, filters, score ranges, and details
- `common.py`: bounded pagination and safe search normalization

Routes should not call Supabase directly. The intended flow is:

```text
API route -> service -> query/repository -> Supabase
```
