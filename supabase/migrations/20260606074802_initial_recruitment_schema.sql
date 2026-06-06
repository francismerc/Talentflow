create extension if not exists citext with schema extensions;
create extension if not exists pgcrypto with schema extensions;

create type public.user_role as enum ('admin', 'recruiter');
create type public.job_status as enum ('draft', 'active', 'closed');
create type public.employment_type as enum (
  'full_time',
  'part_time',
  'contract',
  'internship',
  'temporary'
);
create type public.applicant_status as enum (
  'new',
  'under_review',
  'shortlisted',
  'interview',
  'hired',
  'rejected',
  'withdrawn'
);
create type public.timeline_event_type as enum (
  'application_received',
  'resume_processed',
  'ai_analysis_completed',
  'status_changed',
  'recruiter_note',
  'email_sent',
  'interview_scheduled'
);
create type public.email_direction as enum ('incoming', 'outgoing');
create type public.email_status as enum (
  'received',
  'processing',
  'processed',
  'queued',
  'sent',
  'failed'
);
create type public.email_type as enum (
  'application',
  'acknowledgment',
  'shortlisted',
  'rejected',
  'status_update',
  'other'
);
create type public.ai_recommendation as enum (
  'strong_yes',
  'yes',
  'review',
  'no',
  'strong_no'
);

create table public.users (
  id uuid primary key references auth.users (id) on delete cascade,
  email extensions.citext not null unique,
  full_name text not null default '',
  role public.user_role not null default 'recruiter',
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint users_full_name_length check (char_length(full_name) <= 160)
);

create table public.jobs (
  id uuid primary key default extensions.gen_random_uuid(),
  created_by uuid references public.users (id) on delete set null,
  title text not null,
  description text not null default '',
  required_skills text[] not null default '{}',
  location text,
  employment_type public.employment_type not null default 'full_time',
  status public.job_status not null default 'draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  closed_at timestamptz,
  constraint jobs_title_not_blank check (char_length(btrim(title)) between 1 and 160),
  constraint jobs_description_length check (char_length(description) <= 20000),
  constraint jobs_closed_at_consistency check (
    (status = 'closed' and closed_at is not null)
    or (status <> 'closed' and closed_at is null)
  )
);

create table public.applicants (
  id uuid primary key default extensions.gen_random_uuid(),
  job_id uuid not null references public.jobs (id) on delete restrict,
  full_name text not null,
  email extensions.citext not null,
  phone text,
  location text,
  education jsonb not null default '[]'::jsonb,
  experience jsonb not null default '[]'::jsonb,
  total_experience_years numeric(4, 1),
  skills text[] not null default '{}',
  resume_file_name text,
  resume_storage_path text,
  resume_mime_type text,
  resume_text text,
  source_email_message_id text,
  source_email_thread_id text,
  status public.applicant_status not null default 'new',
  applied_at timestamptz not null default now(),
  reviewed_by uuid references public.users (id) on delete set null,
  reviewed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint applicants_full_name_not_blank check (
    char_length(btrim(full_name)) between 1 and 160
  ),
  constraint applicants_email_not_blank check (char_length(btrim(email::text)) > 3),
  constraint applicants_experience_years_range check (
    total_experience_years is null
    or total_experience_years between 0 and 99.9
  ),
  constraint applicants_resume_mime_type check (
    resume_mime_type is null
    or resume_mime_type in (
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
  ),
  constraint applicants_review_consistency check (
    (reviewed_by is null and reviewed_at is null)
    or (reviewed_by is not null and reviewed_at is not null)
  )
);

create table public.applicant_ai_analyses (
  id uuid primary key default extensions.gen_random_uuid(),
  applicant_id uuid not null references public.applicants (id) on delete cascade,
  model_name text not null,
  prompt_version text not null,
  score numeric(5, 2) not null,
  summary text not null,
  strengths text[] not null default '{}',
  weaknesses text[] not null default '{}',
  recommendation public.ai_recommendation not null,
  recommendation_reason text not null,
  matched_skills text[] not null default '{}',
  missing_skills text[] not null default '{}',
  raw_response jsonb not null default '{}'::jsonb,
  is_current boolean not null default true,
  generated_at timestamptz not null default now(),
  constraint applicant_ai_analyses_score_range check (score between 0 and 100),
  constraint applicant_ai_analyses_model_not_blank check (char_length(btrim(model_name)) > 0),
  constraint applicant_ai_analyses_prompt_not_blank check (
    char_length(btrim(prompt_version)) > 0
  )
);

create table public.applicant_timeline (
  id uuid primary key default extensions.gen_random_uuid(),
  applicant_id uuid not null references public.applicants (id) on delete cascade,
  actor_user_id uuid references public.users (id) on delete set null,
  event_type public.timeline_event_type not null,
  title text not null,
  description text,
  metadata jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  constraint applicant_timeline_title_not_blank check (
    char_length(btrim(title)) between 1 and 200
  )
);

create table public.email_logs (
  id uuid primary key default extensions.gen_random_uuid(),
  applicant_id uuid references public.applicants (id) on delete set null,
  gmail_message_id text,
  gmail_thread_id text,
  idempotency_key text not null unique,
  direction public.email_direction not null,
  email_type public.email_type not null default 'other',
  sender_email extensions.citext not null,
  recipient_email extensions.citext not null,
  subject text not null default '',
  status public.email_status not null,
  error_message text,
  received_at timestamptz,
  sent_at timestamptz,
  processed_at timestamptz,
  created_at timestamptz not null default now(),
  constraint email_logs_idempotency_key_not_blank check (
    char_length(btrim(idempotency_key)) > 0
  ),
  constraint email_logs_direction_timestamps check (
    (direction = 'incoming' and received_at is not null and sent_at is null)
    or (direction = 'outgoing' and sent_at is not null and received_at is null)
  ),
  constraint email_logs_failure_message check (
    status <> 'failed'
    or error_message is not null
  )
);

create unique index applicants_source_email_message_id_unique
  on public.applicants (source_email_message_id)
  where source_email_message_id is not null;

create unique index applicant_ai_analyses_one_current_per_applicant
  on public.applicant_ai_analyses (applicant_id)
  where is_current;

create unique index email_logs_gmail_message_direction_unique
  on public.email_logs (gmail_message_id, direction)
  where gmail_message_id is not null;

create index jobs_status_created_at_idx
  on public.jobs (status, created_at desc);
create index jobs_created_by_idx
  on public.jobs (created_by);
create index jobs_required_skills_gin_idx
  on public.jobs using gin (required_skills);

create index applicants_job_status_applied_at_idx
  on public.applicants (job_id, status, applied_at desc);
create index applicants_status_applied_at_idx
  on public.applicants (status, applied_at desc);
create index applicants_email_idx
  on public.applicants (email);
create index applicants_skills_gin_idx
  on public.applicants using gin (skills);
create index applicants_source_email_thread_id_idx
  on public.applicants (source_email_thread_id);

create index applicant_ai_analyses_applicant_generated_at_idx
  on public.applicant_ai_analyses (applicant_id, generated_at desc);
create index applicant_ai_analyses_score_idx
  on public.applicant_ai_analyses (score desc);

create index applicant_timeline_applicant_occurred_at_idx
  on public.applicant_timeline (applicant_id, occurred_at desc);

create index email_logs_applicant_created_at_idx
  on public.email_logs (applicant_id, created_at desc);
create index email_logs_status_created_at_idx
  on public.email_logs (status, created_at desc);
create index email_logs_gmail_thread_id_idx
  on public.email_logs (gmail_thread_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger users_set_updated_at
before update on public.users
for each row execute function public.set_updated_at();

create trigger jobs_set_updated_at
before update on public.jobs
for each row execute function public.set_updated_at();

create trigger applicants_set_updated_at
before update on public.applicants
for each row execute function public.set_updated_at();

create or replace function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.users (id, email, full_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'full_name', '')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_auth_user();

alter table public.users enable row level security;
alter table public.jobs enable row level security;
alter table public.applicants enable row level security;
alter table public.applicant_ai_analyses enable row level security;
alter table public.applicant_timeline enable row level security;
alter table public.email_logs enable row level security;

create policy "users can read their own profile"
on public.users
for select
to authenticated
using ((select auth.uid()) = id);

create policy "users can update their own profile"
on public.users
for update
to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

create policy "authenticated users can read jobs"
on public.jobs
for select
to authenticated
using (true);

create policy "authenticated users can read applicants"
on public.applicants
for select
to authenticated
using (true);

create policy "authenticated users can read ai analyses"
on public.applicant_ai_analyses
for select
to authenticated
using (true);

create policy "authenticated users can read applicant timeline"
on public.applicant_timeline
for select
to authenticated
using (true);

create policy "authenticated users can read email logs"
on public.email_logs
for select
to authenticated
using (true);

revoke all on table public.users from anon, authenticated;
revoke all on table public.jobs from anon, authenticated;
revoke all on table public.applicants from anon, authenticated;
revoke all on table public.applicant_ai_analyses from anon, authenticated;
revoke all on table public.applicant_timeline from anon, authenticated;
revoke all on table public.email_logs from anon, authenticated;

grant select on table public.users to authenticated;
grant update (full_name, avatar_url) on table public.users to authenticated;
grant select on table public.jobs to authenticated;
grant select on table public.applicants to authenticated;
grant select on table public.applicant_ai_analyses to authenticated;
grant select on table public.applicant_timeline to authenticated;
grant select on table public.email_logs to authenticated;

comment on table public.applicant_ai_analyses is
  'Immutable, reviewable AI analysis history. Recruiter-owned applicant records are updated separately.';
comment on column public.email_logs.idempotency_key is
  'Stable application-generated key used to prevent duplicate incoming processing and outgoing sends.';
