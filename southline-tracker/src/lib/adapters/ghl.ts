// GoHighLevel (LeadConnector) integration.
//
// Two kinds of payload arrive at /api/integrations/ghl:
//
// 1. App / Private Integration webhooks: InboundMessage and OutboundMessage events.
//    Docs: https://marketplace.gohighlevel.com/docs/webhook/InboundMessage
//    { type: "InboundMessage", locationId, contactId, conversationId, messageId,
//      messageType: "SMS" | "Email" | "CALL" | ..., body, direction, dateAdded,
//      from, to, subject?, emailFrom?, emailTo? }
//    These carry a contactId but usually not the contact's email/name, so with
//    GHL_API_KEY set we look the contact up via the API.
//
// 2. Workflow "Webhook" action payloads: the contact's standard fields at the
//    top level (contact_id, first_name, full_name, email, phone, company_name...),
//    plus whatever you add under Custom Data (e.g. message, direction, campaign).
//
// Both are turned into the generic row shape that importRows() understands.

import { secret } from "@/lib/secrets";
import type { Channel, Direction } from "@/lib/types";

const API = "https://services.leadconnectorhq.com";

export async function ghlConfigured() {
  return Boolean(await secret("GHL_API_KEY"));
}

export interface GhlContact {
  id: string;
  firstName?: string;
  lastName?: string;
  contactName?: string;
  name?: string;
  email?: string;
  phone?: string;
  companyName?: string;
  city?: string;
  state?: string;
}

/** GET /contacts/{id} with a Private Integration token (scope: contacts.readonly). */
export async function fetchGhlContact(contactId: string, fetchImpl: typeof fetch = fetch): Promise<GhlContact | null> {
  const key = await secret("GHL_API_KEY");
  if (!key) return null;
  const res = await fetchImpl(`${API}/contacts/${encodeURIComponent(contactId)}`, {
    headers: { Authorization: `Bearer ${key}`, Version: process.env.GHL_API_VERSION || "2021-07-28", Accept: "application/json" },
    cache: "no-store",
    signal: AbortSignal.timeout(15000),
  });
  if (!res.ok) throw new Error(`GHL contact lookup ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const data = (await res.json()) as { contact?: GhlContact };
  return data.contact ?? null;
}

/** Quick connection check for the Import & connect page. */
export async function testGhl(fetchImpl: typeof fetch = fetch): Promise<{ ok: boolean; detail: string }> {
  const key = await secret("GHL_API_KEY");
  const location = await secret("GHL_LOCATION_ID");
  if (!key) return { ok: false, detail: "Add your GHL API key on the API keys page" };
  if (!location) return { ok: false, detail: "Add your GHL location ID on the API keys page" };
  try {
    const res = await fetchImpl(`${API}/contacts/?locationId=${encodeURIComponent(location)}&limit=1`, {
      headers: { Authorization: `Bearer ${key}`, Version: process.env.GHL_API_VERSION || "2021-07-28", Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(15000),
    });
    if (!res.ok) return { ok: false, detail: `GHL ${res.status}: ${(await res.text()).slice(0, 200)}` };
    return { ok: true, detail: "Connected" };
  } catch (e) {
    return { ok: false, detail: (e as Error).message };
  }
}

export type GhlParsed =
  | { kind: "ignore"; reason: string }
  | { kind: "row"; channel: Channel; row: Record<string, unknown>; contactId: string | null; needsLookup: boolean };

const str = (v: unknown) => (v === undefined || v === null || v === "" ? undefined : String(v));

/** messageType from GHL → our channel. Calls, chats etc. are ignored. */
function channelOf(t: unknown): Channel | null {
  const s = String(t ?? "").toLowerCase();
  if (s === "sms" || s === "type_sms") return "sms";
  if (s === "email" || s === "type_email") return "email";
  return null;
}

/** Normalise one GHL payload. `defaults` come from the webhook URL (?channel=&direction=). */
export function parseGhlPayload(p: Record<string, unknown>, defaults: { channel?: Channel; direction?: Direction } = {}): GhlParsed {
  // --- 1. App / Private Integration message events ---
  if (p.type === "InboundMessage" || p.type === "OutboundMessage") {
    const channel = channelOf(p.messageType);
    if (!channel) return { kind: "ignore", reason: `messageType ${String(p.messageType)} not tracked` };
    const inbound = p.type === "InboundMessage" || p.direction === "inbound";
    // For SMS the contact's number is "from" on inbound and "to" on outbound.
    const contactPhone = channel === "sms" ? str(inbound ? p.from : p.to) : undefined;
    const contactEmail = channel === "email" ? str(inbound ? p.emailFrom ?? p.from : firstOf(p.emailTo ?? p.to)) : undefined;
    const body = str(p.body) ?? (typeof p.html === "string" ? stripHtml(p.html) : undefined);
    const contactId = str(p.contactId) ?? null;
    return {
      kind: "row",
      channel,
      contactId,
      needsLookup: Boolean(contactId) && !(channel === "email" ? contactEmail : contactPhone),
      row: {
        direction: inbound ? "inbound" : "outbound",
        body,
        subject: str(p.subject),
        phone: contactPhone,
        email: contactEmail,
        sent_at: str(p.dateAdded),
        external_id: str(p.messageId ?? p.emailMessageId),
        ghl_contact_id: contactId,
      },
    };
  }

  // --- 2. Workflow webhook (contact fields + Custom Data) ---
  const custom = (p.customData && typeof p.customData === "object" ? p.customData : {}) as Record<string, unknown>;
  const msg = (p.message && typeof p.message === "object" ? p.message : {}) as Record<string, unknown>;
  const merged = { ...p, ...custom };
  const channel = channelOf(custom.channel ?? msg.type ?? p.channel) ?? defaults.channel ?? (merged.email && !merged.phone ? "email" : null);
  if (!channel) return { kind: "ignore", reason: "can't tell if this is email or SMS - add ?channel=email or ?channel=sms to the webhook URL" };
  const body = str(custom.message ?? custom.body ?? msg.body ?? p.message_body ?? (typeof p.message === "string" ? p.message : undefined));
  const contactId = str(p.contact_id ?? p.contactId ?? custom.contact_id) ?? null;
  const location = (p.location && typeof p.location === "object" ? p.location : {}) as Record<string, unknown>;
  return {
    kind: "row",
    channel,
    contactId,
    needsLookup: false,
    row: {
      direction: str(custom.direction) ?? defaults.direction ?? (msg.direction as string | undefined) ?? "outbound",
      body,
      subject: str(custom.subject ?? msg.subject),
      email: str(merged.email),
      phone: str(merged.phone),
      name: str(merged.full_name ?? merged.name) ?? [str(merged.first_name), str(merged.last_name)].filter(Boolean).join(" "),
      business: str(merged.company_name ?? merged.business),
      trade: str(custom.trade ?? merged.trade),
      county: str(custom.county ?? merged.county ?? merged.city ?? location.city),
      campaign: str(custom.campaign ?? (p.workflow && typeof p.workflow === "object" ? (p.workflow as Record<string, unknown>).name : undefined)),
      variant: str(custom.variant),
      sent_at: str(custom.sent_at ?? msg.dateAdded ?? p.date_created),
      external_id: str(custom.message_id ?? msg.id),
      ghl_contact_id: contactId,
    },
  };
}

/** Fill in contact details from the GHL API when the event didn't include them. */
export function mergeContact(row: Record<string, unknown>, c: GhlContact) {
  return {
    ...row,
    email: row.email ?? c.email,
    phone: row.phone ?? c.phone,
    name: row.name ?? (c.contactName || c.name || [c.firstName, c.lastName].filter(Boolean).join(" ") || undefined),
    business: row.business ?? c.companyName,
    county: row.county ?? c.city,
  };
}

function firstOf(v: unknown) {
  if (Array.isArray(v)) return str(v[0]);
  return str(v)?.split(",")[0].trim();
}

function stripHtml(html: string) {
  return html.replace(/<br\s*\/?>/gi, "\n").replace(/<\/p>/gi, "\n").replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").trim();
}
