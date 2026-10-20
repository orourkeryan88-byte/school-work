-- Southline outreach tracker schema.
-- Run in the Supabase SQL editor (or `supabase db push`).
-- The app talks to these tables server-side with the service role key, so
-- RLS is enabled with no policies: the anon key can't read anything.

create extension if not exists pgcrypto;

create table if not exists leads (
  id uuid primary key default gen_random_uuid(),
  name text,
  business text,
  email text,
  phone text,                -- E.164 (+353...)
  trade text,
  county text,
  status text not null default 'new'
    check (status in ('new','contacted','replied','interested','booked','won','lost')),
  unsubscribed boolean not null default false,
  booked_at timestamptz,
  won_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists leads_email_idx on leads (email);
create index if not exists leads_phone_idx on leads (phone);

create table if not exists campaigns (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  channel text not null check (channel in ('email','sms')),
  source text,
  created_at timestamptz not null default now()
);

create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references leads(id) on delete cascade,
  campaign_id uuid references campaigns(id) on delete set null,
  channel text not null check (channel in ('email','sms')),
  direction text not null check (direction in ('outbound','inbound')),
  body text not null,
  subject text,
  variant text,
  sent_at timestamptz not null,
  reply_to_id uuid references messages(id) on delete set null,
  ai_tag text check (ai_tag in ('interested','not_interested','question','objection','out_of_office','unsubscribe')),
  ai_tag_source text check (ai_tag_source in ('ai','rules','manual')),
  source text,
  external_id text,
  created_at timestamptz not null default now()
);
create index if not exists messages_lead_idx on messages (lead_id, sent_at);
create index if not exists messages_campaign_idx on messages (campaign_id);
create unique index if not exists messages_external_idx on messages (source, external_id) where external_id is not null;

create table if not exists notes (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references leads(id) on delete cascade,
  kind text not null default 'note' check (kind in ('note','status','system')),
  body text not null,
  created_at timestamptz not null default now()
);
create index if not exists notes_lead_idx on notes (lead_id);

create table if not exists follow_ups (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references leads(id) on delete cascade,
  due_date date not null,
  reason text,
  done_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists follow_ups_due_idx on follow_ups (due_date) where done_at is null;

create table if not exists import_logs (
  id uuid primary key default gen_random_uuid(),
  channel text not null check (channel in ('email','sms')),
  kind text not null check (kind in ('csv','webhook','sync')),
  source text,
  filename text,
  rows_total int not null default 0,
  rows_imported int not null default 0,
  rows_skipped int not null default 0,
  errors jsonb not null default '[]',
  created_at timestamptz not null default now()
);

alter table leads enable row level security;
alter table campaigns enable row level security;
alter table messages enable row level security;
alter table notes enable row level security;
alter table follow_ups enable row level security;
alter table import_logs enable row level security;
