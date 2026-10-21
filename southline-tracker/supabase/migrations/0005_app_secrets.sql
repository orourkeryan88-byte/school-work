-- API keys entered on the app's "API keys" page. Values are encrypted by the app
-- (AES-256-GCM, key derived from SECRETS_KEY / AUTH_SECRET) before they get here.
-- RLS on with no policies: only the server's service-role key can read or write.
create table if not exists app_secrets (
  id text primary key,          -- the setting name, e.g. SENDMODE_ACCESS_KEY
  value_enc text not null,
  updated_at timestamptz not null default now(),
  updated_by text
);
alter table app_secrets enable row level security;
