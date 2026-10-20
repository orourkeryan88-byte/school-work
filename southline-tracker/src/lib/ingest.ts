import Papa from "papaparse";
import type { Channel, Direction } from "@/lib/types";
import type { MessageEvent } from "@/lib/repo";

// Adapters: turn whatever a sending tool gives us (webhook JSON or CSV row)
// into one MessageEvent. Field names differ between GHL, Instantly,
// Smartlead and SendMode, so we look for a list of common aliases.
// Keys are compared lower-cased with spaces/dashes/dots turned into "_".

const ALIASES = {
  // The lead's address. For "from"/"to" style payloads the right side depends
  // on direction, see the *_in / *_out lists.
  email: ["email", "lead_email", "contact_email", "sl_lead_email", "contact.email"],
  email_in: ["from_email", "from", "sender"],
  email_out: ["to_email", "to", "recipient"],
  phone: ["phone", "mobile", "msisdn", "phone_number", "mobile_number", "number", "contact.phone"],
  phone_in: ["from_number", "from", "sender", "originator"],
  phone_out: ["to_number", "to", "recipient", "destination"],
  name: ["name", "full_name", "contact_name", "lead_name", "first_name", "firstname", "contact.name"],
  last_name: ["last_name", "lastname", "surname"],
  business: ["business", "company", "company_name", "business_name", "organisation", "organization", "companyname", "contact.company_name"],
  trade: ["trade", "industry", "category", "niche"],
  county: ["county", "location", "city", "region", "area"],
  body: ["body", "message", "text", "content", "reply_text", "reply_message", "reply", "email_body", "sms", "message_body", "msg", "body_text"],
  subject: ["subject", "email_subject"],
  campaign: ["campaign", "campaign_name", "campaignname", "sequence", "workflow", "list"],
  variant: ["variant", "step", "sequence_step", "template", "ab_variant", "version"],
  sent_at: ["sent_at", "timestamp", "date", "time", "datetime", "created_at", "received_at", "replied_at", "event_timestamp", "senttime", "received"],
  direction: ["direction", "type", "event", "event_type", "status"],
  external_id: ["external_id", "id", "message_id", "messageid", "email_id", "sms_id", "uuid"],
  source: ["source", "provider", "platform"],
  ghl_contact_id: ["ghl_contact_id"],
};

type Field = keyof typeof ALIASES;

function normKey(k: string) {
  return k.trim().toLowerCase().replace(/[\s\-]+/g, "_");
}

/** Flatten nested JSON one level deep ({contact:{email}} -> "contact.email") and normalise keys. */
function flatten(obj: Record<string, unknown>, prefix = "", out: Record<string, unknown> = {}) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${normKey(k)}` : normKey(k);
    if (v && typeof v === "object" && !Array.isArray(v) && !prefix) flatten(v as Record<string, unknown>, key, out);
    else out[key] = v;
  }
  // Also expose nested values under their bare key, without overwriting top-level ones.
  for (const [k, v] of Object.entries(out)) {
    const bare = k.split(".").pop()!;
    if (!(bare in out)) out[bare] = v;
  }
  return out;
}

function pick(row: Record<string, unknown>, field: Field): string | null {
  for (const alias of ALIASES[field]) {
    const v = row[alias];
    if (v !== undefined && v !== null && String(v).trim() !== "") {
      // Smartlead sends reply_message: { text, html }
      if (typeof v === "object") {
        const o = v as Record<string, unknown>;
        if (typeof o.text === "string") return o.text;
        continue;
      }
      return String(v).trim();
    }
  }
  return null;
}

/** Decide sent vs reply from explicit fields, else the default for this source. */
export function detectDirection(raw: string | null, fallback: Direction): Direction {
  if (!raw) return fallback;
  const s = raw.toLowerCase();
  if (/(reply|replied|inbound|incoming|received|mo\b|response)/.test(s)) return "inbound";
  if (/(sent|outbound|outgoing|delivered|mt\b|send)/.test(s)) return "outbound";
  return fallback;
}

function stripQuoted(text: string) {
  // Drop the quoted original from email replies ("On Mon, X wrote:" / "> ...").
  return text
    .split(/\n\s*On .{5,120}wrote:\s*\n|\n-{2,}\s*Original Message/i)[0]
    .split("\n")
    .filter((l) => !l.startsWith(">"))
    .join("\n")
    .trim();
}

export type NormalizeResult = { ok: true; event: MessageEvent } | { ok: false; error: string };

export function normalizeEvent(input: Record<string, unknown>, channel: Channel, defaults: { direction?: Direction; source?: string | null; campaign?: string | null } = {}): NormalizeResult {
  const row = flatten(input);
  const body = pick(row, "body");
  if (!body) return { ok: false, error: "missing message body" };

  const direction = detectDirection(pick(row, "direction"), defaults.direction ?? "outbound");
  const side = direction === "inbound" ? "_in" : "_out";
  const looksLikeEmail = (v: string | null) => (v && v.includes("@") ? v : null);
  const looksLikePhone = (v: string | null) => (v && /^[\d\s+()\-]{7,}$/.test(v) ? v : null);
  const email = looksLikeEmail(pick(row, "email")) ?? looksLikeEmail(pick(row, `email${side}` as Field));
  const phone = looksLikePhone(pick(row, "phone")) ?? looksLikePhone(pick(row, `phone${side}` as Field));
  // A GHL contact id is enough to find the lead, even without email/phone.
  const ghlContactId = pick(row, "ghl_contact_id");
  if (channel === "email" && !email && !ghlContactId) return { ok: false, error: "missing email address" };
  if (channel === "sms" && !phone && !ghlContactId) return { ok: false, error: "missing phone number" };

  const first = pick(row, "name");
  const last = pick(row, "last_name");
  const name = [first, last && !first?.includes(last) ? last : null].filter(Boolean).join(" ") || null;

  return {
    ok: true,
    event: {
      channel,
      direction,
      body: channel === "email" && direction === "inbound" ? stripQuoted(body) || body : body,
      subject: pick(row, "subject"),
      email,
      phone,
      name,
      business: pick(row, "business"),
      trade: pick(row, "trade"),
      county: pick(row, "county"),
      campaign: pick(row, "campaign") ?? defaults.campaign ?? null,
      variant: pick(row, "variant"),
      sent_at: pick(row, "sent_at"),
      external_id: pick(row, "external_id"),
      ghl_contact_id: ghlContactId,
      source: (defaults.source || pick(row, "source") || (channel === "sms" ? "sendmode" : "email"))?.toLowerCase() ?? null,
    },
  };
}

export function parseCsv(text: string): Record<string, string>[] {
  const res = Papa.parse<Record<string, string>>(text.replace(/^﻿/, ""), { header: true, skipEmptyLines: true });
  return res.data;
}

/** Turn rows into CSV text (for exports). */
export function toCsv(rows: Record<string, unknown>[]): string {
  return Papa.unparse(rows.map((r) => Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v ?? ""]))));
}
