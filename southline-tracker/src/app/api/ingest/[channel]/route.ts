import { NextResponse } from "next/server";
import { importRows } from "@/lib/importer";
import { checkIngestSecret } from "@/lib/ingest-auth";
import type { Channel, Direction } from "@/lib/types";

// POST /api/ingest/email and POST /api/ingest/sms
//
// Accepts JSON (one event, an array, or { events: [...] }), form-encoded
// bodies, or plain query params (GET is accepted too, for SMS gateways that
// forward inbound texts as a GET request).
//
// Optional query params set defaults for events that don't say:
//   ?direction=inbound|outbound   (default: outbound, or inbound if the payload looks like a reply)
//   ?source=instantly|smartlead|ghl|sendmode
//   ?campaign=Campaign+name
export const dynamic = "force-dynamic";

const CONTROL = new Set(["secret", "direction", "source", "campaign"]);

async function handle(req: Request, { params }: { params: Promise<{ channel: string }> }) {
  const { channel } = await params;
  if (channel !== "email" && channel !== "sms") return NextResponse.json({ error: "use /api/ingest/email or /api/ingest/sms" }, { status: 404 });

  const auth = checkIngestSecret(req);
  if (!auth.ok) return NextResponse.json({ error: auth.error }, { status: auth.status });

  const url = new URL(req.url);
  const query = Object.fromEntries([...url.searchParams].filter(([k]) => !CONTROL.has(k)));
  let events: Record<string, unknown>[] = [];
  try {
    const type = req.headers.get("content-type") ?? "";
    if (req.method === "GET") {
      events = [query];
    } else if (type.includes("application/json")) {
      const body = await req.json();
      events = Array.isArray(body) ? body : Array.isArray(body?.events) ? body.events : [body];
    } else if (type.includes("form")) {
      events = [{ ...query, ...Object.fromEntries((await req.formData()).entries()) }];
    } else {
      // Unknown content type - try JSON, fall back to query params.
      const text = await req.text();
      events = [text ? JSON.parse(text) : query];
    }
  } catch {
    return NextResponse.json({ error: "could not parse body (send JSON or form data)" }, { status: 400 });
  }

  const direction = url.searchParams.get("direction");
  const summary = await importRows(events, {
    channel: channel as Channel,
    kind: "webhook",
    direction: direction === "inbound" || direction === "outbound" ? (direction as Direction) : undefined,
    source: url.searchParams.get("source"),
    campaign: url.searchParams.get("campaign"),
  });

  const status = summary.imported + summary.duplicates > 0 ? 200 : 422;
  return NextResponse.json({ ok: status === 200, ...summary }, { status });
}

export { handle as GET, handle as POST };
