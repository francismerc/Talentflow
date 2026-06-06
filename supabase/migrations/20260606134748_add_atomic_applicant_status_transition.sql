create or replace function public.handle_new_applicant()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.applicant_timeline (
    applicant_id,
    event_type,
    title,
    description,
    occurred_at
  )
  values (
    new.id,
    'application_received',
    'Application received',
    'Applicant record created in TalentFlow AI.',
    new.applied_at
  );
  return new;
end;
$$;

create trigger on_applicant_created
after insert on public.applicants
for each row execute function public.handle_new_applicant();

create or replace function public.update_applicant_status(
  p_applicant_id uuid,
  p_status public.applicant_status,
  p_actor_user_id uuid,
  p_title text,
  p_description text default null
)
returns public.applicants
language plpgsql
security definer
set search_path = ''
as $$
declare
  current_applicant public.applicants;
  updated_applicant public.applicants;
begin
  select *
  into current_applicant
  from public.applicants
  where id = p_applicant_id
  for update;

  if not found then
    raise exception 'Applicant not found'
      using errcode = 'P0002';
  end if;

  if current_applicant.status = p_status then
    raise exception 'Applicant already has the requested status'
      using errcode = 'P0001';
  end if;

  if not (
    (current_applicant.status = 'new' and p_status in (
      'under_review',
      'shortlisted',
      'rejected',
      'withdrawn'
    ))
    or (current_applicant.status = 'under_review' and p_status in (
      'shortlisted',
      'interview',
      'rejected',
      'withdrawn'
    ))
    or (current_applicant.status = 'shortlisted' and p_status in (
      'interview',
      'rejected',
      'withdrawn'
    ))
    or (current_applicant.status = 'interview' and p_status in (
      'hired',
      'rejected',
      'withdrawn'
    ))
    or (current_applicant.status = 'rejected' and p_status = 'under_review')
  ) then
    raise exception 'Invalid applicant status transition: % -> %',
      current_applicant.status,
      p_status
      using errcode = 'P0001';
  end if;

  update public.applicants
  set
    status = p_status,
    reviewed_by = case
      when p_status in ('under_review', 'shortlisted', 'interview', 'hired', 'rejected')
        then p_actor_user_id
      else reviewed_by
    end,
    reviewed_at = case
      when p_status in ('under_review', 'shortlisted', 'interview', 'hired', 'rejected')
        then now()
      else reviewed_at
    end
  where id = p_applicant_id
  returning * into updated_applicant;

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
    p_applicant_id,
    p_actor_user_id,
    'status_changed',
    p_title,
    p_description,
    jsonb_build_object(
      'previous_status',
      current_applicant.status,
      'new_status',
      p_status
    ),
    now()
  );

  return updated_applicant;
end;
$$;

revoke all on function public.update_applicant_status(
  uuid,
  public.applicant_status,
  uuid,
  text,
  text
) from public, anon, authenticated;

grant execute on function public.update_applicant_status(
  uuid,
  public.applicant_status,
  uuid,
  text,
  text
) to service_role;
