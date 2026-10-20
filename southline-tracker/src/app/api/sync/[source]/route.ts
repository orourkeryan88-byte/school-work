import { NextResponse } from "next/server";
import { fetchInstantlyRows } from "@/lib/adapters/instantly";
import { importRows } from "@/lib/importer";
import { checkIngestSecret } from "@/lib/ingest-auth";

// POST /api/sync/instantly?secret=...   - pull recent emails from Instantly's API.
// Call it from a cron (e.g. Vercel Cron or cron-job.org) every 15-60 minutes.
// SendMode: no pull adapter yet - use the inbound SMS webhook + sent CSV export.
export const dynamic = "force-dynamic";

async function handle(req: Request, { params }: { params: Promise<{ source: string }> }) {
  const auth = checkIngestSecret(req);
  if (!auth.ok) return NextResponse.json({ error: auth.error }, { status: auth.status });
  const { source } = await params;

  if (source === "instantly") {
    const key = process.env.INSTANTLY_API_KEY;
    if (!key) return NextResponse.json({ error: "INSTANTLY_API_KEY is not set" }, { status: 400 });
    try {
      const rows = await fetchInstantlyRows(key);
      const summary = await importRows(rows, { channel: "email", kind: "sync", source: "instantly" });
      return NextResponse.json({ ok: true, ...summary });
    } catch (e) {
      return NextResponse.json({ error: (e as Error).message }, { status: 502 });
    }
  }
  return NextResponse.json({ error: `no sync adapter for "${source}" (available: instantly)` }, { status: 404 });
}

export { handle as GET, handle as POST };
