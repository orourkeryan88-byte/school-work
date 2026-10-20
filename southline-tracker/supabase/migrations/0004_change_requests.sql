-- Feature requests / bug reports sent from the app to Claude via GitHub issues.
create table if not exists change_requests (
  id uuid primary key default gen_random_uuid(),
  kind text not null check (kind in ('feature','bug')),
  title text not null,
  body text not null,
  page text,
  created_by text,
  issue_url text,
  issue_number int,
  error text,
  created_at timestamptz not null default now()
);
alter table change_requests enable row level security;
