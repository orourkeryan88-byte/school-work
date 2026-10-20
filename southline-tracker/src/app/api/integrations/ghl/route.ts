import { NextResponse } from "next/server";
import { fetchGhlContact, ghlConfigured, mergeContact, parseGhlPayload } from "@/lib/adapters/ghl";
import { importRows } from "@/lib/importer";
import { checkIngestSecret } from "@/lib/ingest-auth";
import type { Channel, Direction } from "@/lib/types";

// POST /api/integrations/ghl?secret=INGEST_SECRET
//
// Point either of these at it (setup steps in the README):
//  - a GHL Workflow "Webhook" action  (add &channel=email|sms&direction=outbound|inbound)
//  - a Private Integration / Marketplace app webhook for InboundMessage + OutboundMessage
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const auth = checkIngestSecret(req);
  if (!auth.ok) return NextResponse.json({ error: auth.error }, { status: auth.status });

  const url = new URL(req.url);
  const ch = url.searchParams.get("channel");
  const dir = url.searchParams.get("direction");
  const defaults = {
    channel: ch === "email" || ch === "sms" ? (ch as Channel) : undefined,
    direction: dir === "inbound" || dir === "outbound" ? (dir as Direction) : undefined,
  };

  let payloads: Record<string, unknown>[];
  try {
    const body = await req.json();
    payloads = Array.isArray(body) ? body : [body];
  } catch {
    return NextResponse.json({ error: "expected a JSON body" }, { status: 400 });
  }

  const rows: Record<Channel, Record<string, unknown>[]> = { email: [], sms: [] };
  const ignored: string[] = [];
  const errors: string[] = [];
  for (const p of payloads) {
    const parsed = parseGhlPayload(p, defaults);
    if (parsed.kind === "ignore") {
      ignored.push(parsed.reason);
      continue;
    }
    let row = parsed.row;
    if (parsed.needsLookup && parsed.contactId && ghlConfigured()) {
      try {
        const contact = await fetchGhlContact(parsed.contactId);
        if (contact) row = mergeContact(row, contact);
      } catch (e) {
        errors.push((e as Error).message);
      }
    }
    rows[parsed.channel].push(row);
  }

  const results = [];
  for (const channel of ["email", "sms"] as const) {
    if (rows[channel].length) results.push({ channel, ...(await importRows(rows[channel], { channel, kind: "webhook", source: "ghl" })) });
  }
  const imported = results.reduce((n, r) => n + r.imported + r.duplicates, 0);
  // Ignored events (calls, chats...) are fine - answer 200 so GHL doesn't retry them.
  const ok = imported > 0 || (ignored.length > 0 && results.length === 0);
  return NextResponse.json({ ok, results, ignored, errors }, { status: ok ? 200 : 422 });
}
