// Sales-CRM logic shared by Today, Reply queue, Pipeline and the dashboard.
// All pure functions (no I/O) so they're easy to test.

import type { Lead, LeadStatus, Message } from "@/lib/types";

// ---------- Pipeline & forecast ----------

/** Rough chance a lead at each stage becomes a customer - used for the weighted forecast. */
export const STAGE_PROBABILITY: Record<LeadStatus, number> = {
  new: 0.02,
  contacted: 0.05,
  replied: 0.15,
  interested: 0.35,
  booked: 0.6,
  won: 1,
  lost: 0,
};

/** Monthly value (EUR) assumed for a lead with no deal value set. DEFAULT_DEAL_VALUE env overrides. */
export function defaultDealValue() {
  const n = Number(process.env.DEFAULT_DEAL_VALUE);
  return Number.isFinite(n) && n > 0 ? n : 149;
}

export function dealValue(lead: Lead) {
  return lead.deal_value ?? defaultDealValue();
}

export function pipelineTotals(leads: Lead[]) {
  const open = leads.filter((l) => !["won", "lost", "new"].includes(l.status));
  return {
    openCount: open.length,
    openValue: open.reduce((s, l) => s + dealValue(l), 0),
    weighted: Math.round(open.reduce((s, l) => s + dealValue(l) * STAGE_PROBABILITY[l.status], 0)),
    wonMrr: leads.filter((l) => l.status === "won").reduce((s, l) => s + dealValue(l), 0),
  };
}

export const euro = (n: number) => new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);

// ---------- Who's waiting on me ----------

const NO_REPLY_NEEDED = new Set(["unsubscribe", "not_interested", "out_of_office"]);

/**
 * The reply a lead is waiting on me to answer, or null.
 * True when their latest message is newer than my latest message, and it
 * isn't a STOP / "no thanks" / auto-reply, and I haven't dismissed it.
 */
export function awaitingReply(lead: Lead, messages: Message[]): Message | null {
  if (lead.unsubscribed || lead.status === "lost" || lead.status === "won") return null;
  const sorted = [...messages].sort((a, b) => a.sent_at.localeCompare(b.sent_at));
  const last = sorted.at(-1);
  if (!last || last.direction !== "inbound") return null;
  if (last.ai_tag && NO_REPLY_NEEDED.has(last.ai_tag)) return null;
  if (last.reply_handled_at) return null;
  return last;
}

// ---------- Lead score ----------

export interface Score {
  score: number; // 0-100
  hot: boolean;
  reasons: string[];
}

const BASE: Record<LeadStatus, number> = { new: 0, contacted: 8, replied: 25, interested: 50, booked: 65, won: 0, lost: 0 };

/**
 * Transparent lead score: every point has a reason you can read, so you know
 * *why* someone is at the top of the list (and what to do about it).
 */
export function scoreLead(lead: Lead, messages: Message[], now = Date.now()): Score {
  if (lead.unsubscribed || lead.status === "lost") return { score: 0, hot: false, reasons: [lead.unsubscribed ? "Unsubscribed" : "Lost"] };
  if (lead.status === "won") return { score: 100, hot: false, reasons: ["Customer"] };

  const reasons: string[] = [];
  let s = BASE[lead.status];
  if (s) reasons.push(`Stage: ${lead.status}`);

  const inbound = messages.filter((m) => m.direction === "inbound").sort((a, b) => b.sent_at.localeCompare(a.sent_at));
  const lastIn = inbound[0];
  if (lastIn) {
    const tagPts: Partial<Record<string, number>> = { interested: 15, question: 10, objection: 4 };
    const p = (lastIn.ai_tag && tagPts[lastIn.ai_tag]) || 0;
    if (p) {
      s += p;
      reasons.push(lastIn.ai_tag === "interested" ? "Said they're interested" : lastIn.ai_tag === "question" ? "Asked a question" : "Raised an objection (still talking)");
    }
    const days = (now - Date.parse(lastIn.sent_at)) / 864e5;
    if (days <= 2) {
      s += 15;
      reasons.push("Replied in the last 2 days");
    } else if (days <= 7) {
      s += 7;
      reasons.push("Replied this week");
    } else if (days > 21) {
      s -= 10;
      reasons.push("Gone quiet (3+ weeks)");
    }
  }
  if (awaitingReply(lead, messages)) {
    s += 10;
    reasons.push("Waiting on your reply");
  }
  if (inbound.length >= 2) {
    s += 5;
    reasons.push(`${inbound.length} replies`);
  }
  if (new Set(inbound.map((m) => m.channel)).size > 1) {
    s += 5;
    reasons.push("Engaged on email and SMS");
  }
  const score = Math.max(0, Math.min(99, s));
  return { score, hot: score >= 60, reasons };
}

// ---------- Speed to lead ----------

/**
 * For each reply, how many minutes until I next messaged that lead.
 * Unanswered replies are left out (they show in the reply queue instead).
 */
export function responseMinutes(messages: Message[], range?: { from: string | null; to: string | null }) {
  const byLead = new Map<string, Message[]>();
  for (const m of messages) byLead.set(m.lead_id, [...(byLead.get(m.lead_id) ?? []), m]);
  const out: number[] = [];
  for (const msgs of byLead.values()) {
    const sorted = msgs.sort((a, b) => a.sent_at.localeCompare(b.sent_at));
    sorted.forEach((m, i) => {
      if (m.direction !== "inbound") return;
      if (range?.from && m.sent_at < range.from) return;
      if (range?.to && m.sent_at > range.to) return;
      // Only time the first reply in a burst ("yes" + "how much?" = one wait).
      if (sorted[i - 1]?.direction === "inbound") return;
      const next = sorted.slice(i + 1).find((x) => x.direction === "outbound");
      if (next) out.push((Date.parse(next.sent_at) - Date.parse(m.sent_at)) / 60000);
    });
  }
  return out;
}

export function speedToLead(mins: number[]) {
  if (!mins.length) return { median: null as number | null, within1h: null as number | null, count: 0 };
  const sorted = [...mins].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  const median = sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  return { median, within1h: Math.round((sorted.filter((m) => m <= 60).length / sorted.length) * 100), count: sorted.length };
}

export function formatMinutes(m: number | null) {
  if (m === null) return "—";
  if (m < 60) return `${Math.round(m)}m`;
  if (m < 60 * 48) return `${Math.round(m / 60)}h`;
  return `${Math.round(m / 1440)}d`;
}

// ---------- SMS: quiet hours ----------

/**
 * Don't text tradesmen at 11pm. SMS_SEND_HOURS="09-20" and SMS_SEND_DAYS="1-6"
 * (1 = Monday ... 7 = Sunday), in Irish time. Defaults: 9am-8pm, Mon-Sat.
 */
export function sendWindow(now = new Date()) {
  const [startH, endH] = (process.env.SMS_SEND_HOURS || "09-20").split("-").map(Number);
  const [d1, d2] = (process.env.SMS_SEND_DAYS || "1-6").split("-").map(Number);
  const parts = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Dublin", hour: "numeric", hour12: false, weekday: "short" }).formatToParts(now);
  const hour = Number(parts.find((p) => p.type === "hour")?.value) % 24;
  const wd = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].indexOf(parts.find((p) => p.type === "weekday")?.value ?? "") + 1;
  const dayOk = wd >= d1 && wd <= d2;
  const hourOk = hour >= startH && hour < endH;
  return {
    ok: dayOk && hourOk,
    reason: !dayOk ? `SMS sending is off today (allowed days ${d1}-${d2}, Mon=1)` : !hourOk ? `Quiet hours - SMS sends between ${startH}:00 and ${endH}:00 Irish time` : null,
  };
}

// ---------- SMS: segments & fadas ----------

const GSM7 = "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà";
const GSM7_EXT = "^{}\\[~]|€";

/**
 * How many SMS a text costs. Plain GSM text is 160 chars (153 per part when
 * split). A single non-GSM character - like the fada in "Seán" - switches the
 * whole message to Unicode: 70 chars (67 per part).
 */
export function smsSegments(text: string) {
  let units = 0;
  let unicode = false;
  for (const ch of text) {
    if (GSM7.includes(ch)) units += 1;
    else if (GSM7_EXT.includes(ch)) units += 2;
    else unicode = true;
  }
  const len = unicode ? [...text].length : units;
  const single = unicode ? 70 : 160;
  const multi = unicode ? 67 : 153;
  return { length: len, unicode, segments: len === 0 ? 0 : len <= single ? 1 : Math.ceil(len / multi), limit: single };
}

/** Replace fadas/accents GSM can't carry (á→a, í→i ...) so the text stays at 160 chars. */
export function toGsmFriendly(text: string) {
  return [...text]
    .map((ch) => (GSM7.includes(ch) || GSM7_EXT.includes(ch) ? ch : ch.normalize("NFD").replace(/[̀-ͯ]/g, "")))
    .join("")
    .replace(/[‘’]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/[–—]/g, "-")
    .replace(/…/g, "...");
}
