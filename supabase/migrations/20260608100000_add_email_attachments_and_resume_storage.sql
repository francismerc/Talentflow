create type public.email_attachment_status as enum (
  'stored',
  'parsed',
  'failed'
);

create table public.email_attachments (
  id uuid primary key default extensions.gen_random_uuid(),
  email_log_id uuid not null references public.email_logs (id) on delete cascade,
  gmail_attachment_id text not null,
  file_name text not null,
  mime_type text not null,
  size_bytes bigint not null,
  storage_bucket text not null default 'resumes',
  storage_path text not null unique,
  status public.email_attachment_status not null default 'stored',
  error_message text,
  parsed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint email_attachments_file_name_not_blank check (
    char_length(btrim(file_name)) between 1 and 255
  ),
  constraint email_attachments_supported_mime_type check (
    mime_type in (
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
  ),
  constraint email_attachments_size_range check (
    size_bytes between 1 and 10485760
  ),
  constraint email_attachments_error_consistency check (
    status <> 'failed'
    or error_message is not null
  )
);

create unique index email_attachments_gmail_attachment_unique
  on public.email_attachments (email_log_id, gmail_attachment_id);

create index email_attachments_status_created_at_idx
  on public.email_attachments (status, created_at);

create trigger email_attachments_set_updated_at
before update on public.email_attachments
for each row execute function public.set_updated_at();

alter table public.email_attachments enable row level security;

create policy "authenticated users can read email attachments"
on public.email_attachments
for select
to authenticated
using (true);

revoke all on table public.email_attachments from anon, authenticated;
grant select on table public.email_attachments to authenticated;

insert into storage.buckets (
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types
)
values (
  'resumes',
  'resumes',
  false,
  10485760,
  array[
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]
)
on conflict (id) do update
set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

comment on table public.email_attachments is
  'Resume attachments downloaded from incoming recruitment emails and queued for parsing.';

comment on column public.email_attachments.storage_path is
  'Private Supabase Storage object path. Access should be mediated by the backend.';
