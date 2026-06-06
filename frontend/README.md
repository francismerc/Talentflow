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

## Validation

```bash
npm run lint
npm run build
```

Jobs and Applicants list/detail screens read from the FastAPI backend. Dashboard,
reports, settings, and AI Assistant data remain UI fixtures while their backend
features are implemented. Configure the backend URL with
`NEXT_PUBLIC_API_URL`.
