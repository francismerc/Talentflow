create type public.gmail_integration_status as enum (
  'connected',
  'error',
  'revoked'
);

create table public.gmail_integrations (
  id uuid primary key default extensions.gen_random_uuid(),
  user_id uuid not null unique references public.users (id) on delete cascade,
  gmail_address extensions.citext not null,
  encrypted_access_token text not null,
  encrypted_refresh_token text not null,
  token_expires_at timestamptz,
  scopes text[] not null default '{}',
  status public.gmail_integration_status not null default 'connected',
  last_error text,
  last_synced_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint gmail_integrations_address_not_blank check (
    char_length(btrim(gmail_address::text)) > 3
  ),
  constraint gmail_integrations_access_token_not_blank check (
    char_length(btrim(encrypted_access_token)) > 0
  ),
  constraint gmail_integrations_refresh_token_not_blank check (
    char_length(btrim(encrypted_refresh_token)) > 0
  ),
  constraint gmail_integrations_error_consistency check (
    status <> 'error'
    or last_error is not null
  )
);

create index gmail_integrations_status_last_synced_at_idx
  on public.gmail_integrations (status, last_synced_at);

create trigger gmail_integrations_set_updated_at
before update on public.gmail_integrations
for each row execute function public.set_updated_at();

alter table public.gmail_integrations enable row level security;

create policy "users can read their own gmail connection"
on public.gmail_integrations
for select
to authenticated
using ((select auth.uid()) = user_id);

revoke all on table public.gmail_integrations from anon, authenticated;

grant select (
  id,
  user_id,
  gmail_address,
  token_expires_at,
  scopes,
  status,
  last_error,
  last_synced_at,
  created_at,
  updated_at
) on table public.gmail_integrations to authenticated;

comment on table public.gmail_integrations is
  'Per-recruiter Gmail OAuth connection. OAuth tokens are encrypted by the backend before storage.';

comment on column public.gmail_integrations.encrypted_access_token is
  'Fernet-encrypted OAuth access token. Never expose through application responses.';

comment on column public.gmail_integrations.encrypted_refresh_token is
  'Fernet-encrypted OAuth refresh token. Never expose through application responses.';
