create or replace function public.record_applicant_ai_analysis(
  p_applicant_id uuid,
  p_actor_user_id uuid,
  p_model_name text,
  p_prompt_version text,
  p_score numeric,
  p_summary text,
  p_strengths text[],
  p_weaknesses text[],
  p_recommendation public.ai_recommendation,
  p_recommendation_reason text,
  p_matched_skills text[],
  p_missing_skills text[],
  p_raw_response jsonb
)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  analysis_id uuid;
begin
  perform 1
  from public.applicants
  where id = p_applicant_id
  for update;

  if not found then
    raise exception 'Applicant not found'
      using errcode = 'P0002';
  end if;

  update public.applicant_ai_analyses
  set is_current = false
  where applicant_id = p_applicant_id
    and is_current;

  insert into public.applicant_ai_analyses (
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
    is_current
  )
  values (
    p_applicant_id,
    p_model_name,
    p_prompt_version,
    p_score,
    p_summary,
    coalesce(p_strengths, '{}'),
    coalesce(p_weaknesses, '{}'),
    p_recommendation,
    p_recommendation_reason,
    coalesce(p_matched_skills, '{}'),
    coalesce(p_missing_skills, '{}'),
    coalesce(p_raw_response, '{}'::jsonb),
    true
  )
  returning id into analysis_id;

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
    'ai_analysis_completed',
    'AI analysis completed',
    'A new candidate analysis was generated for recruiter review.',
    jsonb_build_object(
      'analysis_id',
      analysis_id,
      'model_name',
      p_model_name,
      'prompt_version',
      p_prompt_version
    ),
    now()
  );

  return analysis_id;
end;
$$;

revoke all on function public.record_applicant_ai_analysis(
  uuid,
  uuid,
  text,
  text,
  numeric,
  text,
  text[],
  text[],
  public.ai_recommendation,
  text,
  text[],
  text[],
  jsonb
) from public, anon, authenticated;

grant execute on function public.record_applicant_ai_analysis(
  uuid,
  uuid,
  text,
  text,
  numeric,
  text,
  text[],
  text[],
  public.ai_recommendation,
  text,
  text[],
  text[],
  jsonb
) to service_role;
