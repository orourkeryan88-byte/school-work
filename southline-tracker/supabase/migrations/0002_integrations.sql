-- GoHighLevel + SendMode integration fields.
alter table leads add column if not exists ghl_contact_id text;
create index if not exists leads_ghl_idx on leads (ghl_contact_id);

-- Delivery status for outbound SMS (from SendMode delivery reports).
alter table messages add column if not exists delivery_status text;
