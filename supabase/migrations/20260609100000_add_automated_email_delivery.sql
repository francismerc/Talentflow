alter table public.gmail_integrations
add column if not exists send_acknowledgment_emails boolean not null default false;

alter table public.email_logs
drop constraint if exists email_logs_direction_timestamps;

alter table public.email_logs
add constraint email_logs_direction_timestamps check (
  (
    direction = 'incoming'
    and received_at is not null
    and sent_at is null
  )
  or (
    direction = 'outgoing'
    and received_at is null
    and (
      (status in ('queued', 'failed') and sent_at is null)
      or (status = 'sent' and sent_at is not null)
    )
  )
);

create or replace function public.reserve_outgoing_email(
  p_applicant_id uuid,
  p_idempotency_key text,
  p_email_type public.email_type,
  p_sender_email text,
  p_recipient_email text,
  p_subject text
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  email_log public.email_logs;
begin
  select *
  into email_log
  from public.email_logs
  where idempotency_key = p_idempotency_key
  for update;

  if found then
    if email_log.status = 'failed' then
      update public.email_logs
      set
        sender_email = p_sender_email,
        recipient_email = p_recipient_email,
        subject = p_subject,
        status = 'queued',
        error_message = null,
        sent_at = null
      where id = email_log.id
      returning * into email_log;
      return jsonb_build_object(
        'email_log',
        to_jsonb(email_log),
        'reserved',
        true
      );
    end if;
    return jsonb_build_object(
      'email_log',
      to_jsonb(email_log),
      'reserved',
      false
    );
  end if;

  insert into public.email_logs (
    applicant_id,
    idempotency_key,
    direction,
    email_type,
    sender_email,
    recipient_email,
    subject,
    status
  )
  values (
    p_applicant_id,
    p_idempotency_key,
    'outgoing',
    p_email_type,
    p_sender_email,
    p_recipient_email,
    p_subject,
    'queued'
  )
  returning * into email_log;

  return jsonb_build_object(
    'email_log',
    to_jsonb(email_log),
    'reserved',
    true
  );
end;
$$;

create or replace function public.record_outgoing_email_sent(
  p_email_log_id uuid,
  p_actor_user_id uuid,
  p_gmail_message_id text,
  p_gmail_thread_id text
)
returns public.email_logs
language plpgsql
security definer
set search_path = ''
as $$
declare
  email_log public.email_logs;
begin
  update public.email_logs
  set
    gmail_message_id = p_gmail_message_id,
    gmail_thread_id = p_gmail_thread_id,
    status = 'sent',
    error_message = null,
    sent_at = now()
  where id = p_email_log_id
  returning * into email_log;

  if not found then
    raise exception 'Email log not found'
      using errcode = 'P0002';
  end if;

  insert into public.applicant_timeline (
    applicant_id,
    actor_user_id,
    event_type,
    title,
    description,
    metadata,
    occurred_at
  )
  values (
    email_log.applicant_id,
    p_actor_user_id,
    'email_sent',
    'Candidate email sent',
    email_log.subject,
    jsonb_build_object(
      'email_log_id',
      email_log.id,
      'email_type',
      email_log.email_type,
      'gmail_message_id',
      p_gmail_message_id
    ),
    now()
  );

  return email_log;
end;
$$;

revoke all on function public.reserve_outgoing_email(
  uuid,
  text,
  public.email_type,
  text,
  text,
  text
) from public, anon, authenticated;

revoke all on function public.record_outgoing_email_sent(
  uuid,
  uuid,
  text,
  text
) from public, anon, authenticated;

grant execute on function public.reserve_outgoing_email(
  uuid,
  text,
  public.email_type,
  text,
  text,
  text
) to service_role;

grant execute on function public.record_outgoing_email_sent(
  uuid,
  uuid,
  text,
  text
) to service_role;
