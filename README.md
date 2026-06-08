# TalentFlow AI

TalentFlow AI is an AI-powered recruitment management platform for processing
email applications, analyzing resumes, ranking candidates, and supporting
recruiter decisions.

## Technology

- Frontend: Next.js 15, TypeScript, Tailwind CSS, Shadcn UI, Recharts
- Backend: FastAPI, Python 3.12
- Database: Supabase PostgreSQL
- AI: Gemini API
- Email: Gmail API

## Repository

```text
frontend/   Next.js recruiter dashboard
backend/    FastAPI application
supabase/   Versioned database migrations, seed data, and schema tests
```

## Run both applications

After completing the frontend and backend setup, start TalentFlow AI from the
repository root:

```bash
npm install
npm run dev
```

This starts:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

Press `Ctrl+C` once to stop both development servers.

## Recruiter account

Dashboard routes require a Supabase recruiter account.

1. Open the linked Supabase project.
2. Go to **Authentication → Users**.
3. Select **Add user → Create new user**.
4. Enter the recruiter's email and a strong password.
5. Enable automatic email confirmation for the manually created account.

The database trigger creates the matching `public.users` profile. Sign in at
`http://localhost:3000/login`.

## Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

## Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`. Verify it with:

```bash
curl http://localhost:8000/api/v1/health
```

## Supabase

Repository-side Supabase configuration is initialized in `supabase/`.

1. Create a project at [database.new](https://database.new).
2. Open the project's **Connect** dialog.
3. Copy the project URL and publishable key to `frontend/.env.local`.
4. Copy the project URL, publishable key, and secret key to `backend/.env`.
5. Never place `SUPABASE_SECRET_KEY` in the frontend.
6. Authenticate and link the local CLI:

```bash
npx supabase login
npx supabase link --project-ref <project-ref>
```

The Phase 3 schema and applicant workflow migrations are available in
`supabase/migrations/`. Development sample data is opt-in through
`supabase/seed.sql`.

## Validation

```bash
cd frontend && npm run lint && npm run build
cd backend && ruff check . && pytest
```
