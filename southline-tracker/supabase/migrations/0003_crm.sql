-- CRM upgrade: deal values for the pipeline, cached AI reply drafts, queue state.
alter table leads add column if not exists deal_value numeric;

alter table messages add column if not exists ai_draft text;
alter table messages add column if not exists ai_draft_source text check (ai_draft_source in ('ai','template'));
alter table messages add column if not exists reply_handled_at timestamptz;
