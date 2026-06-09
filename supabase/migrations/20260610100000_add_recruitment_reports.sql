create or replace function public.get_recruitment_report(
  p_months integer default 6
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_start_month date;
  v_result jsonb;
begin
  if p_months < 1 or p_months > 24 then
    raise exception 'Report range must be between 1 and 24 months.';
  end if;

  v_start_month := (
    date_trunc('month', now()) - make_interval(months => p_months - 1)
  )::date;

  with
  filtered_applicants as (
    select
      applicant.id,
      applicant.job_id,
      applicant.status,
      applicant.skills,
      applicant.applied_at
    from public.applicants as applicant
    where applicant.applied_at >= v_start_month
  ),
  current_analyses as (
    select analysis.applicant_id, analysis.score
    from public.applicant_ai_analyses as analysis
    join filtered_applicants as applicant
      on applicant.id = analysis.applicant_id
    where analysis.is_current
  ),
  month_series as (
    select generate_series(
      v_start_month::timestamptz,
      date_trunc('month', now()),
      interval '1 month'
    ) as month_start
  ),
  monthly_counts as (
    select
      date_trunc('month', applicant.applied_at) as month_start,
      count(*)::integer as applications,
      count(*) filter (
        where applicant.status in ('shortlisted', 'interview', 'hired')
      )::integer as shortlisted
    from filtered_applicants as applicant
    group by 1
  ),
  status_values(status, display_order) as (
    values
      ('new'::public.applicant_status, 1),
      ('under_review'::public.applicant_status, 2),
      ('shortlisted'::public.applicant_status, 3),
      ('interview'::public.applicant_status, 4),
      ('hired'::public.applicant_status, 5),
      ('rejected'::public.applicant_status, 6),
      ('withdrawn'::public.applicant_status, 7)
  ),
  status_counts as (
    select
      status_value.status,
      status_value.display_order,
      count(applicant.id)::integer as count
    from status_values as status_value
    left join filtered_applicants as applicant
      on applicant.status = status_value.status
    group by status_value.status, status_value.display_order
  ),
  skill_counts as (
    select
      skill,
      count(*)::integer as count
    from filtered_applicants as applicant
    cross join lateral unnest(applicant.skills) as skill
    where btrim(skill) <> ''
    group by skill
    order by count desc, skill
    limit 8
  ),
  position_counts as (
    select
      job.id as job_id,
      job.title,
      count(applicant.id)::integer as count
    from public.jobs as job
    join filtered_applicants as applicant
      on applicant.job_id = job.id
    group by job.id, job.title
    order by count desc, job.title
    limit 8
  ),
  totals as (
    select
      count(*)::integer as total_applications,
      count(*) filter (
        where status in ('shortlisted', 'interview', 'hired')
      )::integer as advanced_applications
    from filtered_applicants
  )
  select jsonb_build_object(
    'months', p_months,
    'period_start', v_start_month,
    'period_end', now(),
    'total_applications', totals.total_applications,
    'open_positions', (
      select count(*)::integer
      from public.jobs
      where status = 'active'
    ),
    'average_candidate_score', (
      select round(avg(score), 1)
      from current_analyses
    ),
    'shortlisted_rate', case
      when totals.total_applications = 0 then 0
      else round(
        totals.advanced_applications::numeric
        / totals.total_applications::numeric * 100,
        1
      )
    end,
    'monthly_applications', (
      select coalesce(
        jsonb_agg(
          jsonb_build_object(
            'month', to_char(month.month_start, 'Mon'),
            'month_start', month.month_start,
            'applications', coalesce(monthly.applications, 0),
            'shortlisted', coalesce(monthly.shortlisted, 0)
          )
          order by month.month_start
        ),
        '[]'::jsonb
      )
      from month_series as month
      left join monthly_counts as monthly
        on monthly.month_start = month.month_start
    ),
    'status_distribution', (
      select coalesce(
        jsonb_agg(
          jsonb_build_object(
            'status', status,
            'count', count
          )
          order by display_order
        ),
        '[]'::jsonb
      )
      from status_counts
    ),
    'top_skills', (
      select coalesce(
        jsonb_agg(
          jsonb_build_object('skill', skill, 'count', count)
          order by count desc, skill
        ),
        '[]'::jsonb
      )
      from skill_counts
    ),
    'top_positions', (
      select coalesce(
        jsonb_agg(
          jsonb_build_object(
            'job_id', job_id,
            'title', title,
            'count', count
          )
          order by count desc, title
        ),
        '[]'::jsonb
      )
      from position_counts
    )
  )
  into v_result
  from totals;

  return v_result;
end;
$$;

revoke all on function public.get_recruitment_report(integer)
from public, anon;

grant execute on function public.get_recruitment_report(integer)
to authenticated, service_role;
