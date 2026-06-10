# TalentFlow AI Frontend

Enterprise recruitment dashboard prototype built with Next.js 15, TypeScript,
Tailwind CSS, Shadcn UI, Lucide, and Recharts.

## Local development

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

All application routes are protected by Supabase authentication. Create a
recruiter through the Supabase Authentication dashboard, then sign in at
`http://localhost:3000/login`.

## Validation

```bash
npm run lint
npm run build
```

Dashboard, Jobs, Applicants, Reports, Gmail settings, and AI Assistant features
read from the FastAPI backend. Configure the backend URL with
`NEXT_PUBLIC_API_URL`.

For Vercel deployment, use `frontend` as the project root and configure the
three public variables documented in `../docs/deployment.md`.
