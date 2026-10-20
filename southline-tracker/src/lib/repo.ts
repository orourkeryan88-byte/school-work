import { classifyReply } from "@/lib/ai";
import { getStore } from "@/lib/store";
import type { Campaign, Channel, Direction, FollowUp, InboxRow, Lead, LeadStatus, Message, Note, ReplyTag } from "@/lib/types";
import { LEAD_STATUSES } from "@/lib/types";
import { businessKey, isoDay, newId, normalizeEmail, normalizePhone, nowIso, parseDate } from "@/lib/utils";

// All business logic lives here, on top of the table-level Store.

const rank = (s: LeadStatus) => LEAD_STATUSES.indexOf(s);

// ---------- Leads & matching ----------

export interface LeadInput {
  name?: string | null;
  business?: string | null;
  email?: string | null;
  phone?: string | null;
  trade?: string | null;
  county?: string | null;
}

/**
 * Find an existing lead for a contact, so one person has one timeline across
 * channels. Match order: email, then phone, then business name.
 */
export function matchLead(leads: Lead[], input: LeadInput): Lead | null {
  const email = normalizeEmail(input.email);
  const phone = normalizePhone(input.phone);
  const biz = businessKey(input.business);
  return (
    (email && leads.find((l) => l.email === email)) ||
    (phone && leads.find((l) => l.phone === phone)) ||
    (biz && leads.find((l) => businessKey(l.business) === biz)) ||
    null
  );
}

/**
 * Rows loaded once and reused while recording a batch of messages (CSV import),
 * so we don't re-read whole tables for every row. Kept in sync as we write.
 */
export interface Ctx {
  leads: Lead[];
  campaigns: Campaign[];
  messages: Message[];
}

export async function loadCtx(): Promise<Ctx> {
  const store = getStore();
  const [leads, campaigns, messages] = await Promise.all([store.all("leads"), store.all("campaigns"), store.all("messages")]);
  return { leads, campaigns, messages };
}

function replaceIn<T extends { id: string }>(rows: T[] | undefined, row: T) {
  if (!rows) return;
  const i = rows.findIndex((r) => r.id === row.id);
  if (i >= 0) rows[i] = row;
  else rows.push(row);
}

/** Find-or-create a lead, filling in any fields we didn't know before. */
export async function upsertLead(input: LeadInput, ctx?: Ctx): Promise<Lead> {
  const store = getStore();
  const existing = matchLead(ctx?.leads ?? (await store.all("leads")), input);
  const clean = {
    name: input.name?.trim() || null,
    business: input.business?.trim() || null,
    email: normalizeEmail(input.email),
    phone: normalizePhone(input.phone),
    trade: input.trade?.trim() || null,
    county: input.county?.trim().replace(/^co\.?\s+/i, "") || null,
  };
  if (existing) {
    const patch: Partial<Lead> = {};
    for (const [k, v] of Object.entries(clean) as [keyof typeof clean, string | null][]) {
      if (v && !existing[k]) patch[k] = v;
    }
    if (!Object.keys(patch).length) return existing;
    const updated = await store.update("leads", existing.id, { ...patch, updated_at: nowIso() });
    replaceIn(ctx?.leads, updated);
    return updated;
  }
  const now = nowIso();
  const lead = await store.insert("leads", {
    id: newId(), ...clean, status: "new", unsubscribed: false, booked_at: null, won_at: null, created_at: now, updated_at: now,
  });
  replaceIn(ctx?.leads, lead);
  return lead;
}

/**
 * Change a lead's status and log it on the timeline.
 * `auto` changes (from ingest) only ever move forward through the pipeline,
 * except "lost" which can come from a "no"/STOP reply.
 */
export async function setLeadStatus(leadId: string, status: LeadStatus, opts: { auto?: boolean; ctx?: Ctx } = {}) {
  const store = getStore();
  const lead = opts.ctx?.leads.find((l) => l.id === leadId) ?? (await store.get("leads", leadId));
  if (!lead || lead.status === status) return lead;
  if (opts.auto) {
    if (lead.status === "won" || lead.status === "lost") return lead;
    if (status !== "lost" && rank(status) < rank(lead.status)) return lead;
  }
  const now = nowIso();
  const patch: Partial<Lead> = { status, updated_at: now };
  if (status === "booked" && !lead.booked_at) patch.booked_at = now;
  if (status === "won" && !lead.won_at) patch.won_at = now;
  const updated = await store.update("leads", leadId, patch);
  replaceIn(opts.ctx?.leads, updated);
  await addNote(leadId, `Status → ${status}${opts.auto ? " (auto)" : ""}`, "status");
  return updated;
}

export async function updateLead(leadId: string, patch: LeadInput) {
  return getStore().update("leads", leadId, { ...patch, phone: normalizePhone(patch.phone), email: normalizeEmail(patch.email), updated_at: nowIso() });
}

export async function addNote(leadId: string, body: string, kind: Note["kind"] = "note") {
  return getStore().insert("notes", { id: newId(), lead_id: leadId, kind, body, created_at: nowIso() });
}

// ---------- Campaigns ----------

export async function getOrCreateCampaign(name: string | null | undefined, channel: Channel, source: string | null, ctx?: Ctx): Promise<Campaign | null> {
  const clean = name?.trim();
  if (!clean) return null;
  const store = getStore();
  const all = ctx?.campaigns ?? (await store.all("campaigns", { channel }));
  const found = all.find((c) => c.channel === channel && c.name.toLowerCase() === clean.toLowerCase());
  if (found) return found;
  const created = await store.insert("campaigns", { id: newId(), name: clean, channel, source, created_at: nowIso() });
  replaceIn(ctx?.campaigns, created);
  return created;
}

// ---------- Messages (the core of ingest) ----------

export interface MessageEvent extends LeadInput {
  channel: Channel;
  direction: Direction;
  body: string;
  subject?: string | null;
  campaign?: string | null;
  variant?: string | null;
  sent_at?: string | null;
  source?: string | null;
  external_id?: string | null;
}

export type RecordResult = { status: "created"; message: Message; lead: Lead } | { status: "duplicate"; message: Message };

/**
 * Record one sent message or reply. Used by the webhooks, CSV import and API sync.
 * - dedupes on (source, external_id) or identical lead+direction+time+body
 * - matches/creates the lead and campaign
 * - links a reply to the last thing we sent them on that channel
 * - AI-tags replies and moves the lead's status forward
 */
export async function recordMessage(ev: MessageEvent, ctx?: Ctx): Promise<RecordResult> {
  const store = getStore();
  const sentAt = parseDate(ev.sent_at) ?? nowIso();

  if (ev.external_id) {
    const pool = ctx?.messages ?? (await store.all("messages", { external_id: ev.external_id }));
    const dup = pool.find((m) => m.external_id === ev.external_id && m.source === (ev.source ?? null));
    if (dup) return { status: "duplicate", message: dup };
  }

  let lead = await upsertLead(ev, ctx);
  const history = ctx ? ctx.messages.filter((m) => m.lead_id === lead.id) : await store.all("messages", { lead_id: lead.id });
  const same = history.find((m) => m.direction === ev.direction && m.sent_at === sentAt && m.body === ev.body);
  if (same) return { status: "duplicate", message: same };

  const campaign = await getOrCreateCampaign(ev.campaign, ev.channel, ev.source ?? null, ctx);
  let replyTo: Message | null = null;
  let tag: { tag: ReplyTag; source: "ai" | "rules" } | null = null;
  if (ev.direction === "inbound") {
    replyTo =
      history
        .filter((m) => m.direction === "outbound" && m.channel === ev.channel && m.sent_at <= sentAt)
        .sort((a, b) => b.sent_at.localeCompare(a.sent_at))[0] ?? null;
    tag = await classifyReply(ev.body);
  }

  const message = await store.insert("messages", {
    id: newId(),
    lead_id: lead.id,
    campaign_id: campaign?.id ?? replyTo?.campaign_id ?? null,
    channel: ev.channel,
    direction: ev.direction,
    body: ev.body,
    subject: ev.subject ?? null,
    variant: ev.variant ?? replyTo?.variant ?? null,
    sent_at: sentAt,
    reply_to_id: replyTo?.id ?? null,
    ai_tag: tag?.tag ?? null,
    ai_tag_source: tag?.source ?? null,
    source: ev.source ?? null,
    external_id: ev.external_id ?? null,
    created_at: nowIso(),
  });
  ctx?.messages.push(message);

  lead = (await applyMessageToStatus(lead, message, ctx)) ?? lead;
  return { status: "created", message, lead };
}

/** What a new message means for the pipeline. */
async function applyMessageToStatus(lead: Lead, m: Message, ctx?: Ctx) {
  const opts = { auto: true, ctx };
  if (m.direction === "outbound") return setLeadStatus(lead.id, "contacted", opts);
  if (m.ai_tag === "unsubscribe") {
    replaceIn(ctx?.leads, await getStore().update("leads", lead.id, { unsubscribed: true }));
    return setLeadStatus(lead.id, "lost", opts);
  }
  if (m.ai_tag === "not_interested") return setLeadStatus(lead.id, "lost", opts);
  if (m.ai_tag === "interested") return setLeadStatus(lead.id, "interested", opts);
  return setLeadStatus(lead.id, "replied", opts);
}

/** Manually retag a reply (or retag with AI) and update the lead to match. */
export async function retagMessage(messageId: string, tag: ReplyTag, source: Message["ai_tag_source"] = "manual") {
  const store = getStore();
  const m = await store.update("messages", messageId, { ai_tag: tag, ai_tag_source: source });
  const lead = await store.get("leads", m.lead_id);
  if (lead) await applyMessageToStatus(lead, m);
  return m;
}

// ---------- Follow-ups ----------

export async function addFollowUp(leadId: string, dueDate: string, reason?: string | null) {
  return getStore().insert("follow_ups", { id: newId(), lead_id: leadId, due_date: dueDate, reason: reason || null, done_at: null, created_at: nowIso() });
}

export async function completeFollowUp(id: string) {
  return getStore().update("follow_ups", id, { done_at: nowIso() });
}

export interface QueueItem {
  lead: Lead;
  followUp: FollowUp | null; // null = suggested automatically, not scheduled
  reason: string;
  dueDate: string;
  overdue: boolean;
  lastMessage: Message | null;
  messages: Message[];
}

/**
 * Who needs a follow-up today:
 *  1. scheduled follow-ups due today or earlier
 *  2. auto: replied/interested leads with nothing from me in 2+ days
 *  3. auto: contacted leads sent one message 4-30 days ago with no reply
 *     (more than one send usually means a sequence tool is already nudging them)
 */
export async function followUpQueue(today = isoDay()): Promise<QueueItem[]> {
  const store = getStore();
  const [leads, messages, followUps] = await Promise.all([store.all("leads"), store.all("messages"), store.all("follow_ups")]);
  const byLead = groupBy(messages, (m) => m.lead_id);
  const items: QueueItem[] = [];
  const seen = new Set<string>();

  for (const f of followUps) {
    if (f.done_at || f.due_date > today) continue;
    const lead = leads.find((l) => l.id === f.lead_id);
    if (!lead) continue;
    const msgs = sortByTime(byLead.get(lead.id) ?? []);
    items.push({ lead, followUp: f, reason: f.reason || "Scheduled follow-up", dueDate: f.due_date, overdue: f.due_date < today, lastMessage: msgs.at(-1) ?? null, messages: msgs });
    seen.add(lead.id);
  }

  const scheduledLater = new Set(followUps.filter((f) => !f.done_at && f.due_date > today).map((f) => f.lead_id));
  for (const lead of leads) {
    if (seen.has(lead.id) || scheduledLater.has(lead.id) || lead.unsubscribed) continue;
    const msgs = sortByTime(byLead.get(lead.id) ?? []);
    const last = msgs.at(-1);
    if (!last) continue;
    const daysSince = (Date.parse(`${today}T23:59:59Z`) - Date.parse(last.sent_at)) / 864e5;
    let reason: string | null = null;
    if ((lead.status === "replied" || lead.status === "interested") && last.direction === "inbound" && daysSince >= 0) {
      reason = lead.status === "interested" ? "Interested - waiting on you" : "Replied - waiting on you";
    } else if ((lead.status === "replied" || lead.status === "interested") && daysSince >= 2) {
      reason = "No answer since your last message";
    } else if (lead.status === "contacted" && daysSince >= 4 && daysSince <= 30 && msgs.filter((m) => m.direction === "outbound").length === 1) {
      reason = "No reply yet - send a nudge";
    }
    if (reason) items.push({ lead, followUp: null, reason, dueDate: today, overdue: false, lastMessage: last, messages: msgs });
  }

  // Hottest first: interested > replied > the rest, then overdue first.
  const heat = (i: QueueItem) => (i.lead.status === "interested" ? 0 : i.lead.status === "replied" ? 1 : 2);
  return items.sort((a, b) => heat(a) - heat(b) || Number(b.overdue) - Number(a.overdue) || a.dueDate.localeCompare(b.dueDate));
}

// ---------- Read models for the UI ----------

export interface InboxFilters {
  channel?: Channel | "";
  status?: LeadStatus | "";
  tag?: ReplyTag | "";
  trade?: string;
  from?: string; // ISO
  to?: string; // ISO
  q?: string;
}

export async function listInbox(f: InboxFilters = {}): Promise<InboxRow[]> {
  const store = getStore();
  const [leads, messages, campaigns] = await Promise.all([store.all("leads"), store.all("messages"), store.all("campaigns")]);
  const leadById = new Map(leads.map((l) => [l.id, l]));
  const msgById = new Map(messages.map((m) => [m.id, m]));
  const cmpById = new Map(campaigns.map((c) => [c.id, c]));
  const q = f.q?.toLowerCase().trim();

  return messages
    .filter((m) => m.direction === "inbound")
    .map((reply) => ({
      reply,
      sent: reply.reply_to_id ? msgById.get(reply.reply_to_id) ?? null : null,
      lead: leadById.get(reply.lead_id)!,
      campaign: reply.campaign_id ? cmpById.get(reply.campaign_id) ?? null : null,
    }))
    .filter(({ reply, lead }) => {
      if (!lead) return false;
      if (f.channel && reply.channel !== f.channel) return false;
      if (f.status && lead.status !== f.status) return false;
      if (f.tag && reply.ai_tag !== f.tag) return false;
      if (f.trade && lead.trade?.toLowerCase() !== f.trade.toLowerCase()) return false;
      if (f.from && reply.sent_at < f.from) return false;
      if (f.to && reply.sent_at > f.to) return false;
      if (q && ![lead.name, lead.business, lead.email, lead.phone, reply.body].some((s) => s?.toLowerCase().includes(q))) return false;
      return true;
    })
    .sort((a, b) => b.reply.sent_at.localeCompare(a.reply.sent_at));
}

export interface LeadRow extends Lead {
  channels: Channel[];
  sent: number;
  replies: number;
  last_activity: string;
  last_reply: Message | null;
}

export async function listLeads(f: { q?: string; status?: LeadStatus | ""; channel?: Channel | ""; trade?: string } = {}): Promise<LeadRow[]> {
  const store = getStore();
  const [leads, messages] = await Promise.all([store.all("leads"), store.all("messages")]);
  const byLead = groupBy(messages, (m) => m.lead_id);
  const q = f.q?.toLowerCase().trim();
  return leads
    .map((l) => {
      const msgs = sortByTime(byLead.get(l.id) ?? []);
      return {
        ...l,
        channels: [...new Set(msgs.map((m) => m.channel))],
        sent: msgs.filter((m) => m.direction === "outbound").length,
        replies: msgs.filter((m) => m.direction === "inbound").length,
        last_activity: msgs.at(-1)?.sent_at ?? l.updated_at,
        last_reply: msgs.filter((m) => m.direction === "inbound").at(-1) ?? null,
      };
    })
    .filter((l) => {
      if (f.status && l.status !== f.status) return false;
      if (f.channel && !l.channels.includes(f.channel)) return false;
      if (f.trade && l.trade?.toLowerCase() !== f.trade.toLowerCase()) return false;
      if (q && ![l.name, l.business, l.email, l.phone, l.county, l.trade].some((s) => s?.toLowerCase().includes(q))) return false;
      return true;
    })
    .sort((a, b) => b.last_activity.localeCompare(a.last_activity));
}

export type TimelineItem =
  | { type: "message"; at: string; message: Message; campaign: Campaign | null }
  | { type: "note"; at: string; note: Note }
  | { type: "followup"; at: string; followUp: FollowUp };

export async function getLeadDetail(id: string) {
  const store = getStore();
  const lead = await store.get("leads", id);
  if (!lead) return null;
  const [messages, notes, followUps, campaigns] = await Promise.all([
    store.all("messages", { lead_id: id }),
    store.all("notes", { lead_id: id }),
    store.all("follow_ups", { lead_id: id }),
    store.all("campaigns"),
  ]);
  const cmp = new Map(campaigns.map((c) => [c.id, c]));
  const timeline: TimelineItem[] = [
    ...messages.map((m) => ({ type: "message" as const, at: m.sent_at, message: m, campaign: m.campaign_id ? cmp.get(m.campaign_id) ?? null : null })),
    ...notes.map((n) => ({ type: "note" as const, at: n.created_at, note: n })),
    ...followUps.map((f) => ({ type: "followup" as const, at: f.created_at, followUp: f })),
  ].sort((a, b) => b.at.localeCompare(a.at));
  return { lead, messages: sortByTime(messages), notes, followUps, timeline };
}

/** Distinct trades, for filter dropdowns. */
export async function listTrades() {
  const leads = await getStore().all("leads");
  return [...new Set(leads.map((l) => l.trade).filter(Boolean) as string[])].sort();
}

// ---------- helpers ----------

export function groupBy<T>(rows: T[], key: (r: T) => string) {
  const map = new Map<string, T[]>();
  for (const r of rows) {
    const k = key(r);
    const arr = map.get(k);
    if (arr) arr.push(r);
    else map.set(k, [r]);
  }
  return map;
}

export function sortByTime(messages: Message[]) {
  return [...messages].sort((a, b) => a.sent_at.localeCompare(b.sent_at));
}
