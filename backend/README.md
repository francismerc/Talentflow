# TalentFlow AI Backend

FastAPI service for TalentFlow AI. This Phase 1 foundation provides typed
configuration, CORS, standardized error responses, and a health endpoint.

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

## Validation

```bash
ruff check .
pytest
```

Supabase repositories, Gmail integration, Gemini services, and business APIs
will be implemented in their respective development phases.

## Database queries

Read queries are grouped by feature under `app/database/queries/`:

- `jobs.py`: paginated job lists and job details
- `applicants.py`: applicant search, filters, score ranges, and details
- `common.py`: bounded pagination and safe search normalization

Routes should not call Supabase directly. The intended flow is:

```text
API route -> service -> query/repository -> Supabase
```
