import { classifyReply } from "@/lib/ai";
import { sendSms } from "@/lib/adapters/sendmode";
import { awaitingReply, scoreLead, sendWindow, type Score } from "@/lib/crm";
import { draftMessage } from "@/lib/ai";
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
  ghl_contact_id?: string | null;
}

/**
 * Find an existing lead for a contact, so one person has one timeline across
 * channels. Match order: GHL contact id, email, phone, then business name.
 */
export function matchLead(leads: Lead[], input: LeadInput): Lead | null {
  const email = normalizeEmail(input.email);
  const phone = normalizePhone(input.phone);
  const biz = businessKey(input.business);
  const ghl = input.ghl_contact_id;
  return (
    (ghl && leads.find((l) => l.ghl_contact_id === ghl)) ||
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
    ghl_contact_id: input.ghl_contact_id?.trim() || null,
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

export async function updateLead(leadId: string, patch: LeadInput & { deal_value?: number | null }) {
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
  score: Score;
}

export async function listLeads(f: { q?: string; status?: LeadStatus | ""; channel?: Channel | ""; trade?: string; sort?: "recent" | "score" | "name"; hot?: boolean } = {}): Promise<LeadRow[]> {
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
        score: scoreLead(l, msgs),
      };
    })
    .filter((l) => {
      if (f.status && l.status !== f.status) return false;
      if (f.channel && !l.channels.includes(f.channel)) return false;
      if (f.trade && l.trade?.toLowerCase() !== f.trade.toLowerCase()) return false;
      if (f.hot && !l.score.hot) return false;
      if (q && ![l.name, l.business, l.email, l.phone, l.county, l.trade].some((s) => s?.toLowerCase().includes(q))) return false;
      return true;
    })
    .sort((a, b) =>
      f.sort === "score"
        ? b.score.score - a.score.score
        : f.sort === "name"
          ? (a.name ?? a.business ?? "").localeCompare(b.name ?? b.business ?? "")
          : b.last_activity.localeCompare(a.last_activity),
    );
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

// ---------- SendMode: send from the app + delivery reports ----------

/**
 * Send an SMS to a lead through SendMode and log it on their timeline.
 * Refuses unsubscribed leads and leads without a phone number.
 */
export async function sendSmsToLead(leadId: string, text: string, send: typeof sendSms = sendSms) {
  const lead = await getStore().get("leads", leadId);
  if (!lead) return { ok: false as const, error: "Lead not found" };
  if (lead.unsubscribed) return { ok: false as const, error: "This lead has unsubscribed - not sending." };
  if (!lead.phone) return { ok: false as const, error: "This lead has no phone number." };
  if (!text.trim()) return { ok: false as const, error: "Message is empty." };

  // Quiet hours: never text outside the allowed window (SMS_SEND_HOURS / SMS_SEND_DAYS).
  const window = sendWindow();
  if (!window.ok) return { ok: false as const, error: window.reason ?? "Outside sending hours" };

  // Our reference goes to SendMode as customerid and comes back on delivery reports.
  const ref = newId().replace(/-/g, "");
  const res = await send({ to: lead.phone, text: text.trim(), customerId: ref });
  if (!res.ok) return { ok: false as const, error: res.error ?? "Send failed" };

  const recorded = await recordMessage({ channel: "sms", direction: "outbound", body: text.trim(), phone: lead.phone, source: "sendmode", external_id: ref });
  if (recorded.status === "created") await getStore().update("messages", recorded.message.id, { delivery_status: "sent" });
  return { ok: true as const };
}

/** Apply a SendMode delivery report to the message it belongs to. */
export async function applyDeliveryReport(customerId: string | null, status: string | null) {
  if (!customerId || !status) return false;
  const store = getStore();
  const m = (await store.all("messages", { external_id: customerId })).find((x) => x.source === "sendmode");
  if (!m) return false;
  await store.update("messages", m.id, { delivery_status: status.toLowerCase() });
  return true;
}

// ---------- Reply queue (Claude drafts, you approve) ----------

export interface ReplyQueueItem {
  lead: Lead;
  reply: Message; // their message I haven't answered
  messages: Message[];
  score: Score;
  waitingMinutes: number;
}

/** Everyone waiting on an answer from me, hottest first. */
export async function replyQueue(now = Date.now()): Promise<ReplyQueueItem[]> {
  const store = getStore();
  const [leads, messages] = await Promise.all([store.all("leads"), store.all("messages")]);
  const byLead = groupBy(messages, (m) => m.lead_id);
  const items: ReplyQueueItem[] = [];
  for (const lead of leads) {
    const msgs = sortByTime(byLead.get(lead.id) ?? []);
    const reply = awaitingReply(lead, msgs);
    if (!reply) continue;
    items.push({ lead, reply, messages: msgs, score: scoreLead(lead, msgs, now), waitingMinutes: (now - Date.parse(reply.sent_at)) / 60000 });
  }
  return items.sort((a, b) => b.score.score - a.score.score || b.waitingMinutes - a.waitingMinutes);
}

/**
 * Claude's draft answer to a reply. Drafts are cached on the reply so the
 * queue opens instantly and you only pay for each draft once.
 */
export async function draftForReply(messageId: string, opts: { regenerate?: boolean; goal?: string } = {}) {
  const store = getStore();
  const reply = await store.get("messages", messageId);
  if (!reply) throw new Error("reply not found");
  if (reply.ai_draft && !opts.regenerate) return { text: reply.ai_draft, source: reply.ai_draft_source ?? "ai" };
  const detail = await getLeadDetail(reply.lead_id);
  if (!detail) throw new Error("lead not found");
  const draft = await draftMessage(detail.lead, detail.messages, reply.channel, opts.goal);
  await store.update("messages", messageId, { ai_draft: draft.text, ai_draft_source: draft.source });
  return draft;
}

/** Take a reply out of the queue without answering in the app (e.g. you rang them). */
export async function dismissReply(messageId: string, note?: string) {
  const m = await getStore().update("messages", messageId, { reply_handled_at: nowIso() });
  if (note) await addNote(m.lead_id, note);
  return m;
}

// ---------- Check number ----------

/** Everything the CRM already knows about a phone number. */
export async function crmLookup(raw: string) {
  const phone = normalizePhone(raw);
  if (!phone) return null;
  const store = getStore();
  const lead = (await store.all("leads", { phone }))[0] ?? null;
  if (!lead) return { phone, lead: null, messages: [] as Message[], score: null, campaigns: [] as string[] };
  const [messages, campaigns] = await Promise.all([store.all("messages", { lead_id: lead.id }), store.all("campaigns")]);
  const sorted = sortByTime(messages);
  const names = [...new Set(sorted.map((m) => campaigns.find((c) => c.id === m.campaign_id)?.name).filter(Boolean) as string[])];
  return { phone, lead, messages: sorted.slice(-3), score: scoreLead(lead, sorted), campaigns: names };
}

// ---------- Change requests (ask Claude to build/fix something) ----------

/** The GitHub issue text Claude works from. */
export function changeRequestIssue(kind: "feature" | "bug", text: string, page: string | null, by: string | null) {
  const firstLine = text.trim().split("\n")[0];
  const title = `${kind === "bug" ? "Bug" : "Feature"}: ${firstLine.length > 80 ? `${firstLine.slice(0, 77)}...` : firstLine}`;
  const body = `@claude please ${kind === "bug" ? "fix this bug" : "build this feature"} in the Southline CRM (\`southline-tracker/\`). Follow \`southline-tracker/CLAUDE.md\`.

**Request${by ? ` from ${by}` : ""}:**
${text.trim()}

${page ? `**Reported on page:** \`${page}\`\n\n` : ""}When done: run \`npm test\`, \`npm run typecheck\`, \`npm run lint\` and \`npm run build\` in \`southline-tracker/\`, then open a pull request that explains the change in plain English.

_Sent from the Southline app's "Request a change" button._`;
  return { title, body };
}

export async function submitChangeRequest(
  input: { kind: "feature" | "bug"; text: string; page: string | null; by: string | null },
  send: (title: string, body: string, labels: string[]) => Promise<{ url: string; number: number } | null> | null,
) {
  const { title, body } = changeRequestIssue(input.kind, input.text, input.page, input.by);
  let issue: { url: string; number: number } | null = null;
  let error: string | null = null;
  try {
    issue = await (send(title, body, ["claude", input.kind === "bug" ? "bug" : "enhancement"]) ?? null);
    if (!issue) error = "GitHub isn't connected yet - add a GitHub token and repository on the API keys page";
  } catch (e) {
    error = (e as Error).message;
  }
  return getStore().insert("change_requests", {
    id: newId(), kind: input.kind, title, body: input.text.trim(), page: input.page, created_by: input.by,
    issue_url: issue?.url ?? null, issue_number: issue?.number ?? null, error, created_at: nowIso(),
  });
}
