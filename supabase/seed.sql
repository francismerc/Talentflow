-- Development-only seed data. Run locally with `npx supabase db reset`.

insert into public.jobs (
  id,
  title,
  description,
  required_skills,
  location,
  employment_type,
  status,
  created_at
)
values
  (
    '10000000-0000-4000-8000-000000000001',
    'Senior Product Designer',
    'Lead end-to-end product design for TalentFlow recruiting workflows.',
    array['Figma', 'Design Systems', 'User Research', 'Prototyping', 'B2B SaaS'],
    'San Francisco / Remote',
    'full_time',
    'active',
    '2026-05-14T09:00:00Z'
  ),
  (
    '10000000-0000-4000-8000-000000000002',
    'Frontend Engineer',
    'Build accessible recruiter experiences with React, TypeScript, and Next.js.',
    array['React', 'TypeScript', 'Next.js', 'Tailwind CSS', 'Testing'],
    'Remote, US',
    'full_time',
    'active',
    '2026-05-18T09:00:00Z'
  ),
  (
    '10000000-0000-4000-8000-000000000003',
    'Backend Engineer',
    'Design reliable APIs and data pipelines for recruitment automation.',
    array['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS'],
    'Remote, US',
    'full_time',
    'active',
    '2026-05-20T09:00:00Z'
  )
on conflict (id) do update set
  title = excluded.title,
  description = excluded.description,
  required_skills = excluded.required_skills,
  location = excluded.location,
  employment_type = excluded.employment_type,
  status = excluded.status;

insert into public.applicants (
  id,
  job_id,
  full_name,
  email,
  phone,
  location,
  education,
  experience,
  total_experience_years,
  skills,
  resume_file_name,
  resume_mime_type,
  source_email_message_id,
  source_email_thread_id,
  status,
  applied_at
)
values
  (
    '20000000-0000-4000-8000-000000000001',
    '10000000-0000-4000-8000-000000000001',
    'Maya Chen',
    'maya.chen@example.com',
    '+1 (415) 555-0142',
    'San Francisco, CA',
    '[{"degree":"BFA Interaction Design","school":"California College of the Arts"}]'::jsonb,
    '[{"title":"Senior Product Designer","company":"Northstar","years":4}]'::jsonb,
    7.0,
    array['Figma', 'Design Systems', 'User Research', 'Prototyping', 'B2B SaaS'],
    'maya_chen_resume.pdf',
    'application/pdf',
    'seed-message-maya',
    'seed-thread-maya',
    'shortlisted',
    '2026-06-05T09:42:00Z'
  ),
  (
    '20000000-0000-4000-8000-000000000002',
    '10000000-0000-4000-8000-000000000002',
    'Ethan Wright',
    'ethan.wright@example.com',
    '+1 (206) 555-0188',
    'Seattle, WA',
    '[{"degree":"BS Computer Science","school":"University of Washington"}]'::jsonb,
    '[{"title":"Frontend Engineer","company":"Orbit","years":4}]'::jsonb,
    6.0,
    array['React', 'TypeScript', 'Next.js', 'Tailwind CSS', 'Playwright'],
    'ethan_wright_resume.pdf',
    'application/pdf',
    'seed-message-ethan',
    'seed-thread-ethan',
    'interview',
    '2026-06-04T10:15:00Z'
  ),
  (
    '20000000-0000-4000-8000-000000000003',
    '10000000-0000-4000-8000-000000000003',
    'Noah Williams',
    'noah.williams@example.com',
    '+1 (312) 555-0165',
    'Chicago, IL',
    '[{"degree":"MS Computer Science","school":"Northwestern University"}]'::jsonb,
    '[{"title":"Backend Engineer","company":"Cloudline","years":3}]'::jsonb,
    5.0,
    array['Python', 'FastAPI', 'AWS', 'Docker', 'Redis'],
    'noah_williams_resume.pdf',
    'application/pdf',
    'seed-message-noah',
    'seed-thread-noah',
    'under_review',
    '2026-06-03T13:05:00Z'
  )
on conflict (id) do update set
  job_id = excluded.job_id,
  full_name = excluded.full_name,
  email = excluded.email,
  phone = excluded.phone,
  location = excluded.location,
  education = excluded.education,
  experience = excluded.experience,
  total_experience_years = excluded.total_experience_years,
  skills = excluded.skills,
  status = excluded.status,
  applied_at = excluded.applied_at;

insert into public.applicant_ai_analyses (
  id,
  applicant_id,
  model_name,
  prompt_version,
  score,
  summary,
  strengths,
  weaknesses,
  recommendation,
  recommendation_reason,
  matched_skills,
  missing_skills,
  raw_response,
  is_current,
  generated_at
)
values
  (
    '30000000-0000-4000-8000-000000000001',
    '20000000-0000-4000-8000-000000000001',
    'gemini-development-placeholder',
    'candidate-analysis-v1',
    94,
    'Senior product designer with strong enterprise workflow experience.',
    array['Systems thinking', 'Enterprise design', 'Cross-functional leadership'],
    array['Limited fintech exposure'],
    'strong_yes',
    'The candidate closely matches the role requirements.',
    array['Figma', 'Design Systems', 'User Research', 'Prototyping', 'B2B SaaS'],
    array['Fintech'],
    '{"seed":true}'::jsonb,
    true,
    '2026-06-05T09:44:00Z'
  ),
  (
    '30000000-0000-4000-8000-000000000002',
    '20000000-0000-4000-8000-000000000002',
    'gemini-development-placeholder',
    'candidate-analysis-v1',
    91,
    'Frontend specialist with strong React and accessibility experience.',
    array['React expertise', 'Accessibility', 'Product intuition'],
    array['Limited backend ownership'],
    'strong_yes',
    'The candidate is an excellent fit for the frontend scope.',
    array['React', 'TypeScript', 'Next.js', 'Tailwind CSS', 'Testing'],
    array['Python'],
    '{"seed":true}'::jsonb,
    true,
    '2026-06-04T10:17:00Z'
  ),
  (
    '30000000-0000-4000-8000-000000000003',
    '20000000-0000-4000-8000-000000000003',
    'gemini-development-placeholder',
    'candidate-analysis-v1',
    86,
    'Backend engineer with strong Python API and cloud infrastructure experience.',
    array['Python', 'Production APIs', 'System design'],
    array['Limited PostgreSQL optimization examples'],
    'yes',
    'Advance to a technical screen focused on database depth.',
    array['Python', 'FastAPI', 'Docker', 'AWS'],
    array['PostgreSQL'],
    '{"seed":true}'::jsonb,
    true,
    '2026-06-03T13:07:00Z'
  )
on conflict (id) do update set
  score = excluded.score,
  summary = excluded.summary,
  strengths = excluded.strengths,
  weaknesses = excluded.weaknesses,
  recommendation = excluded.recommendation,
  recommendation_reason = excluded.recommendation_reason,
  matched_skills = excluded.matched_skills,
  missing_skills = excluded.missing_skills,
  raw_response = excluded.raw_response;

insert into public.applicant_timeline (
  id,
  applicant_id,
  event_type,
  title,
  description,
  occurred_at
)
values
  (
    '40000000-0000-4000-8000-000000000001',
    '20000000-0000-4000-8000-000000000001',
    'application_received',
    'Application received',
    'Resume received through the recruitment inbox.',
    '2026-06-05T09:42:00Z'
  ),
  (
    '40000000-0000-4000-8000-000000000002',
    '20000000-0000-4000-8000-000000000001',
    'resume_processed',
    'Resume processed',
    'Candidate data extracted from the resume.',
    '2026-06-05T09:43:00Z'
  ),
  (
    '40000000-0000-4000-8000-000000000003',
    '20000000-0000-4000-8000-000000000001',
    'ai_analysis_completed',
    'AI analysis completed',
    'Candidate analysis was generated for recruiter review.',
    '2026-06-05T09:44:00Z'
  )
on conflict (id) do update set
  title = excluded.title,
  description = excluded.description,
  occurred_at = excluded.occurred_at;

insert into public.email_logs (
  id,
  applicant_id,
  gmail_message_id,
  gmail_thread_id,
  idempotency_key,
  direction,
  email_type,
  sender_email,
  recipient_email,
  subject,
  status,
  received_at,
  processed_at
)
values
  (
    '50000000-0000-4000-8000-000000000001',
    '20000000-0000-4000-8000-000000000001',
    'seed-message-maya',
    'seed-thread-maya',
    'incoming:seed-message-maya',
    'incoming',
    'application',
    'maya.chen@example.com',
    'recruiting@example.com',
    'Application: Senior Product Designer',
    'processed',
    '2026-06-05T09:42:00Z',
    '2026-06-05T09:44:00Z'
  )
on conflict (id) do update set
  status = excluded.status,
  processed_at = excluded.processed_at;
