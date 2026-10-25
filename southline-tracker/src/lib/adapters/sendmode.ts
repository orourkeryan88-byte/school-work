// SendMode (sendmode.com) SMS gateway, REST API v2.
// Docs: https://developers.sendmode.com/restdocs/send
//   - Auth: the API access key goes in the Authorization header
//     (create one in the SendMode portal: Settings → API Settings).
//   - Send: POST https://rest.sendmode.com/v2/send with a form field `message`
//     holding JSON: { messagetext, recipients: [..], senderid?, customerid?, scheduledate? }
//   - Credits: GET https://rest.sendmode.com/v2/credits?access_key=...
//   - Delivery reports: SendMode posts EventID, Phonenumber, DataType, Status,
//     CustomerID to the URL set in "Post Delivery Reports to URL" and expects
//     the response body "True".

import { secret } from "@/lib/secrets";

const BASE = "https://rest.sendmode.com/v2";

export async function sendmodeConfigured() {
  return Boolean(await secret("SENDMODE_ACCESS_KEY"));
}

/** SendMode wants Irish numbers without the "+": 353871234567. */
export function toSendmodeNumber(e164: string) {
  return e164.replace(/^\+/, "");
}

export interface SendResult {
  ok: boolean;
  error?: string;
  raw: unknown;
}

/**
 * Send one SMS. `customerId` is echoed back on delivery reports, so we pass
 * our own message id to match the report to the message later.
 */
export async function sendSms(opts: { to: string; text: string; customerId: string; senderId?: string }, fetchImpl: typeof fetch = fetch): Promise<SendResult> {
  const key = await secret("SENDMODE_ACCESS_KEY");
  if (!key) return { ok: false, error: "Add your SendMode access key on the API keys page", raw: null };

  const message: Record<string, unknown> = {
    messagetext: opts.text,
    recipients: [toSendmodeNumber(opts.to)],
    customerid: opts.customerId,
  };
  const senderId = opts.senderId ?? (await secret("SENDMODE_SENDER_ID"));
  if (senderId) message.senderid = senderId;

  let res: Response;
  let text: string;
  try {
    res = await fetchImpl(`${BASE}/send`, {
      method: "POST",
      headers: { Authorization: key, "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ message: JSON.stringify(message) }).toString(),
      signal: AbortSignal.timeout(20000),
    });
    text = await res.text();
  } catch (e) {
    const cause = (e as { cause?: { code?: string } }).cause?.code;
    return { ok: false, error: `Couldn't reach SendMode${cause ? ` (${cause})` : ""}: ${(e as Error).message}`, raw: null };
  }
  let raw: unknown = text;
  try {
    raw = JSON.parse(text);
  } catch {
    // keep the plain text
  }
  // Success looks like { status: "OK", statusCode: 0, ... }. Errors come back
  // as JSON with an error code/description (e.g. 14 = INVALID_ACCESS_KEY).
  const body = (raw && typeof raw === "object" ? raw : {}) as Record<string, unknown>;
  const accepted = res.ok && (String(body.status ?? "").toUpperCase() === "OK" || body.statusCode === 0 || body.statusCode === "0");
  if (accepted) return { ok: true, raw };
  const why = body.description ?? body.message ?? body.error ?? (typeof raw === "string" ? raw : JSON.stringify(raw));
  return { ok: false, error: `SendMode ${res.status}: ${String(why).slice(0, 300)}`, raw };
}

/** Plain-English version of a SendMode error reply. */
export function sendmodeError(j: Record<string, unknown>) {
  const code = String(j.status ?? "");
  if (code === "INVALID_ACCESS_KEY" || Number(j.statusCode) === 14)
    return "SendMode says this access key isn't valid. In the SendMode portal (Settings → API Settings) copy the access key again, or create a new one, and paste it here.";
  return `SendMode: ${String(j.error ?? j.description ?? j.message ?? code ?? "unknown error").slice(0, 200)}`;
}

/** Check the key works and how many credits are left. */
export async function getCredits(fetchImpl: typeof fetch = fetch): Promise<{ ok: boolean; credits?: string; error?: string }> {
  const key = await secret("SENDMODE_ACCESS_KEY");
  if (!key) return { ok: false, error: "Add your SendMode access key on the API keys page" };
  try {
    const res = await fetchImpl(`${BASE}/credits?access_key=${encodeURIComponent(key)}`, { headers: { Authorization: key }, cache: "no-store", signal: AbortSignal.timeout(15000) });
    const text = await res.text();
    if (!res.ok) return { ok: false, error: `SendMode ${res.status}: ${text.slice(0, 200)}` };
    let credits = text;
    try {
      const j = JSON.parse(text) as Record<string, unknown>;
      // SendMode answers 200 even for a bad key, e.g. { status: "INVALID_ACCESS_KEY", statusCode: 14, error: "..." }
      const failed = j.error || /INVALID|ERROR|DENIED/i.test(String(j.status ?? "")) || (j.statusCode != null && Number(j.statusCode) !== 0);
      if (failed) return { ok: false, error: sendmodeError(j) };
      credits = String(j.credits ?? j.balance ?? j.remainingCredits ?? j.Credits ?? JSON.stringify(j));
    } catch {
      // plain-text balance
    }
    return { ok: true, credits };
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

/** Read a delivery report (query string or form fields, any casing). */
export function parseDeliveryReport(fields: Record<string, unknown>) {
  const get = (k: string) => {
    const hit = Object.entries(fields).find(([key]) => key.toLowerCase() === k);
    return hit ? String(hit[1]) : null;
  };
  return {
    eventId: get("eventid"),
    phone: get("phonenumber"),
    status: get("status"),
    customerId: get("customerid"),
  };
}
