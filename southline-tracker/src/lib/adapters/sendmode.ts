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

const BASE = "https://rest.sendmode.com/v2";

export function sendmodeConfigured() {
  return Boolean(process.env.SENDMODE_ACCESS_KEY);
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
  const key = process.env.SENDMODE_ACCESS_KEY;
  if (!key) return { ok: false, error: "SENDMODE_ACCESS_KEY is not set", raw: null };

  const message: Record<string, unknown> = {
    messagetext: opts.text,
    recipients: [toSendmodeNumber(opts.to)],
    customerid: opts.customerId,
  };
  const senderId = opts.senderId ?? process.env.SENDMODE_SENDER_ID;
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

/** Check the key works and how many credits are left. */
export async function getCredits(fetchImpl: typeof fetch = fetch): Promise<{ ok: boolean; credits?: string; error?: string }> {
  const key = process.env.SENDMODE_ACCESS_KEY;
  if (!key) return { ok: false, error: "SENDMODE_ACCESS_KEY is not set" };
  try {
    const res = await fetchImpl(`${BASE}/credits?access_key=${encodeURIComponent(key)}`, { headers: { Authorization: key }, cache: "no-store", signal: AbortSignal.timeout(15000) });
    const text = await res.text();
    if (!res.ok) return { ok: false, error: `SendMode ${res.status}: ${text.slice(0, 200)}` };
    let credits = text;
    try {
      const j = JSON.parse(text);
      credits = String(j.credits ?? j.balance ?? j.remainingCredits ?? JSON.stringify(j));
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
