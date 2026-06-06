begin;

select plan(18);

select has_table('public', 'users', 'users table exists');
select has_table('public', 'jobs', 'jobs table exists');
select has_table('public', 'applicants', 'applicants table exists');
select has_table(
  'public',
  'applicant_ai_analyses',
  'applicant_ai_analyses table exists'
);
select has_table(
  'public',
  'applicant_timeline',
  'applicant_timeline table exists'
);
select has_table('public', 'email_logs', 'email_logs table exists');

select col_is_fk(
  'public',
  'jobs',
  'created_by',
  'jobs.created_by references users'
);
select col_is_fk(
  'public',
  'applicants',
  'job_id',
  'applicants.job_id references jobs'
);
select col_is_fk(
  'public',
  'applicant_ai_analyses',
  'applicant_id',
  'AI analysis references applicants'
);
select col_is_fk(
  'public',
  'applicant_timeline',
  'applicant_id',
  'timeline references applicants'
);
select col_is_fk(
  'public',
  'email_logs',
  'applicant_id',
  'email logs reference applicants'
);

select has_index(
  'public',
  'applicants',
  'applicants_source_email_message_id_unique',
  'incoming application message IDs are unique'
);
select has_index(
  'public',
  'applicant_ai_analyses',
  'applicant_ai_analyses_one_current_per_applicant',
  'only one current AI analysis is allowed per applicant'
);
select has_index(
  'public',
  'email_logs',
  'email_logs_gmail_message_direction_unique',
  'email message direction pairs are unique'
);

select is(
  (select relrowsecurity from pg_class where oid = 'public.users'::regclass),
  true,
  'RLS is enabled on users'
);
select is(
  (select relrowsecurity from pg_class where oid = 'public.jobs'::regclass),
  true,
  'RLS is enabled on jobs'
);
select is(
  (select relrowsecurity from pg_class where oid = 'public.applicants'::regclass),
  true,
  'RLS is enabled on applicants'
);
select is(
  (select relrowsecurity from pg_class where oid = 'public.email_logs'::regclass),
  true,
  'RLS is enabled on email logs'
);

select * from finish();

rollback;
