# TalentFlow AI Deployment

TalentFlow uses three production services:

- Supabase for PostgreSQL, authentication, and private resume storage
- Render for the FastAPI backend
- Vercel for the Next.js frontend

Deploy in that order so every downstream service receives a stable URL.

## 1. Release Check

From the repository root:

```bash
npm run release:check
```

Do not deploy unless backend tests, Ruff, frontend lint, and the production
Next.js build all pass.

## 2. Supabase

Apply every migration in `supabase/migrations/` in timestamp order. The latest
required migration is:

```text
20260610100000_add_recruitment_reports.sql
```

Either run it in the Supabase SQL Editor or configure `SUPABASE_DB_PASSWORD`
locally and run:

```bash
npx supabase db push --linked
```

Then verify:

```bash
npx supabase db lint --linked --level warning
```

In Supabase Authentication:

1. Set the Site URL to the production Vercel URL after Vercel is deployed.
2. Add the Vercel URL and any approved preview URL to Redirect URLs.
3. Confirm the recruiter account exists and email confirmation is complete.
4. Confirm the private `resumes` bucket exists.

Never place the Supabase secret key in Vercel.

## 3. Render Backend

Create a Render Blueprint from this repository. Render reads `render.yaml` and
creates the `talentflow-api` web service.

Set these secret environment variables in Render:

```text
FRONTEND_URL=https://your-app.vercel.app
BACKEND_CORS_ORIGINS=https://your-app.vercel.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=...
SUPABASE_SECRET_KEY=...
GEMINI_API_KEY=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://your-api.onrender.com/api/v1/gmail/oauth/callback
GOOGLE_OAUTH_STATE_SECRET=...
GOOGLE_TOKEN_ENCRYPTION_KEY=...
EMAIL_REPLY_TO=recruitment@your-company.com
EMAIL_CAREERS_URL=https://your-company.com/careers
```

`GOOGLE_OAUTH_STATE_SECRET` must be a strong random value.
`GOOGLE_TOKEN_ENCRYPTION_KEY` must be a Fernet key generated with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

After deployment, verify:

```bash
curl https://your-api.onrender.com/api/v1/health
```

The response must report `healthy`.

## 4. Google OAuth

In the Google Cloud OAuth web client:

1. Add the production Render callback:
   `https://your-api.onrender.com/api/v1/gmail/oauth/callback`
2. Keep the localhost callback for development.
3. Add the recruiter Gmail account as a test user while the consent screen is
   in testing mode.
4. Reconnect Gmail from production Settings after deployment.

OAuth tokens from localhost should not be assumed to work after changing the
redirect configuration. Reconnecting establishes the production connection.

## 5. Vercel Frontend

Import the GitHub repository into Vercel and configure:

```text
Root Directory: frontend
Framework Preset: Next.js
Build Command: npm run build
Install Command: npm ci
```

Set:

```text
NEXT_PUBLIC_API_URL=https://your-api.onrender.com/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=...
```

Deploy, then update `FRONTEND_URL` and `BACKEND_CORS_ORIGINS` in Render with
the final Vercel URL and redeploy the backend.

## 6. Production Smoke Test

Run this sequence with a test applicant:

1. Sign in through the Vercel application.
2. Open Dashboard, Applicants, Jobs, Reports, Settings, and AI Assistant.
3. Connect Gmail in Settings.
4. Send a PDF or DOCX resume to the connected recruitment inbox.
5. Process Gmail and confirm the attachment is stored.
6. Process resumes and confirm an applicant is created.
7. Generate Gemini analysis and verify score explanations.
8. Ask the assistant to find and rank the candidate.
9. Confirm a status action and verify the applicant timeline.
10. Send a status email and verify `email_logs`.
11. Open Reports and export the CSV.

Check browser console errors, API logs, mobile layout, loading states, empty
states, and duplicate-action protection during the smoke test.

## 7. Rollback

- Vercel: promote the previous successful deployment.
- Render: redeploy the previous Git commit.
- Supabase: create a forward-only corrective migration. Do not delete or edit
  already-applied production migration files.

Database migrations should be applied before application code that depends on
them. Back up production data before destructive schema changes.
