// Optional pull-sync from Instantly (API v2). Webhooks are the main way in;
// this backfills anything missed. Field names below follow Instantly's v2
// "List emails" endpoint - check them against developer.instantly.ai if
// Instantly changes its API. Unknown fields are ignored, so a mismatch means
// rows get skipped (and logged), not bad data.

const BASE = "https://api.instantly.ai/api/v2";

type InstantlyEmail = {
  id: string;
  timestamp_email?: string;
  timestamp_created?: string;
  subject?: string;
  from_address_email?: string;
  to_address_email_list?: string;
  body?: { text?: string; html?: string };
  campaign_id?: string;
  lead?: string;
  ue_type?: number; // 1 = sent from campaign, 2 = received (reply), 3 = sent manually
};

function htmlToText(html: string) {
  return html.replace(/<br\s*\/?>/gi, "\n").replace(/<\/p>/gi, "\n").replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").trim();
}

async function get<T>(path: string, key: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { headers: { Authorization: `Bearer ${key}` }, cache: "no-store" });
  if (!res.ok) throw new Error(`Instantly ${path}: ${res.status} ${await res.text()}`);
  return res.json() as Promise<T>;
}

/** Fetch recent emails (sent + replies) as raw rows for importRows(). */
export async function fetchInstantlyRows(key: string, maxPages = 10): Promise<Record<string, unknown>[]> {
  // Campaign names, so messages land under readable campaign names.
  const campaigns = new Map<string, string>();
  try {
    const c = await get<{ items: { id: string; name: string }[] }>("/campaigns?limit=100", key);
    for (const x of c.items ?? []) campaigns.set(x.id, x.name);
  } catch {
    // Not fatal - we'll fall back to the campaign id.
  }

  const rows: Record<string, unknown>[] = [];
  let cursor: string | undefined;
  for (let page = 0; page < maxPages; page++) {
    const qs = new URLSearchParams({ limit: "100" });
    if (cursor) qs.set("starting_after", cursor);
    const data = await get<{ items: InstantlyEmail[]; next_starting_after?: string }>(`/emails?${qs}`, key);
    for (const e of data.items ?? []) {
      const inbound = e.ue_type === 2;
      rows.push({
        external_id: e.id,
        direction: inbound ? "inbound" : "outbound",
        email: e.lead ?? (inbound ? e.from_address_email : e.to_address_email_list?.split(",")[0]),
        subject: e.subject,
        body: e.body?.text || (e.body?.html ? htmlToText(e.body.html) : ""),
        sent_at: e.timestamp_email ?? e.timestamp_created,
        campaign: e.campaign_id ? campaigns.get(e.campaign_id) ?? e.campaign_id : undefined,
      });
    }
    cursor = data.next_starting_after;
    if (!cursor) break;
  }
  return rows;
}
