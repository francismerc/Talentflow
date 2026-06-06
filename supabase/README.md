# TalentFlow AI Database

This directory contains the versioned Supabase configuration, SQL migrations,
development seed data, and database contract tests.

## Linked project

- Project: TalentFlow AI
- Region: Southeast Asia (Singapore)

The project reference is stored only in Supabase's ignored `.temp` directory
after linking.

## Migrations

Apply pending migrations:

```bash
npx supabase db push --linked
```

Check migration state and schema health:

```bash
npx supabase migration list
npx supabase db lint --linked --level warning
```

## Local development

Docker Desktop is required to run the local Supabase stack:

```bash
npx supabase start
npx supabase db reset
npx supabase test db
```

`db reset` rebuilds only the local database, applies migrations, and loads
`seed.sql`. Do not use remote reset commands on production projects.

## Security

- Row Level Security is enabled on every application table.
- Browser users receive read-only access after authentication.
- Mutations will go through the FastAPI backend.
- The backend Supabase secret key must never be exposed to the frontend.
- AI analysis history is stored separately from recruiter-owned applicant data.
