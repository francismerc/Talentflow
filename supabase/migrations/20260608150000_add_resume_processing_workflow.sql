alter type public.email_attachment_status add value if not exists 'needs_review';

create or replace function public.create_applicant_from_resume(
  p_attachment_id uuid,
  p_job_id uuid,
  p_full_name text,
  p_email text,
  p_phone text,
  p_location text,
  p_education jsonb,
  p_experience jsonb,
  p_total_experience_years numeric,
  p_skills text[],
  p_resume_text text
)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  attachment_record record;
  job_record public.jobs;
  created_applicant_id uuid;
begin
  select
    attachment.id,
    attachment.file_name,
    attachment.mime_type,
    attachment.storage_path,
    attachment.status,
    log.id as email_log_id,
    log.gmail_message_id,
    log.gmail_thread_id,
    log.received_at
  into attachment_record
  from public.email_attachments as attachment
  join public.email_logs as log on log.id = attachment.email_log_id
  where attachment.id = p_attachment_id
  for update of attachment;

  if not found then
    raise exception 'Resume attachment not found'
      using errcode = 'P0002';
  end if;

  if attachment_record.status <> 'stored' then
    raise exception 'Resume attachment is not ready for parsing'
      using errcode = 'P0001';
  end if;

  select *
  into job_record
  from public.jobs
  where id = p_job_id;

  if not found or job_record.status <> 'active' then
    raise exception 'Active job not found'
      using errcode = 'P0002';
  end if;

  if exists (
    select 1
    from public.applicants
    where source_email_message_id = attachment_record.gmail_message_id
  ) then
    raise exception 'Recruitment email already has an applicant'
      using errcode = '23505';
  end if;

  insert into public.applicants (
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
    resume_storage_path,
    resume_mime_type,
    resume_text,
    source_email_message_id,
    source_email_thread_id,
    status,
    applied_at
  )
  values (
    p_job_id,
    p_full_name,
    p_email,
    p_phone,
    p_location,
    coalesce(p_education, '[]'::jsonb),
    coalesce(p_experience, '[]'::jsonb),
    p_total_experience_years,
    coalesce(p_skills, '{}'),
    attachment_record.file_name,
    attachment_record.storage_path,
    attachment_record.mime_type,
    p_resume_text,
    attachment_record.gmail_message_id,
    attachment_record.gmail_thread_id,
    'new',
    coalesce(attachment_record.received_at, now())
  )
  returning id into created_applicant_id;

  update public.email_logs
  set applicant_id = created_applicant_id
  where id = attachment_record.email_log_id;

  update public.email_attachments
  set
    status = 'parsed',
    error_message = null,
    parsed_at = now()
  where id = p_attachment_id;

  insert into public.applicant_timeline (
    applicant_id,
    event_type,
    title,
    description,
    metadata,
    occurred_at
  )
  values (
    created_applicant_id,
    'resume_processed',
    'Resume processed',
    'Candidate information was extracted from the stored resume.',
    jsonb_build_object('email_attachment_id', p_attachment_id),
    now()
  );

  return created_applicant_id;
end;
$$;

revoke all on function public.create_applicant_from_resume(
  uuid,
  uuid,
  text,
  text,
  text,
  text,
  jsonb,
  jsonb,
  numeric,
  text[],
  text
) from public, anon, authenticated;

grant execute on function public.create_applicant_from_resume(
  uuid,
  uuid,
  text,
  text,
  text,
  text,
  jsonb,
  jsonb,
  numeric,
  text[],
  text
) to service_role;
