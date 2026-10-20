import { importRows } from "@/lib/importer";
import { checkIngestSecret } from "@/lib/ingest-auth";

// SendMode inbound SMS (replies).
// Point SendMode's incoming SMS forwarding URL at:
//   https://YOUR_APP/api/integrations/sendmode/inbound?secret=INGEST_SECRET
// Same as /api/ingest/sms?direction=inbound&source=sendmode, but answers
// "True" like SendMode's other callbacks expect. Accepts GET, form or JSON.
export const dynamic = "force-dynamic";

async function handle(req: Request) {
  const auth = checkIngestSecret(req);
  if (!auth.ok) return new Response(auth.error, { status: auth.status });

  const fields: Record<string, unknown> = Object.fromEntries([...new URL(req.url).searchParams].filter(([k]) => k !== "secret"));
  if (req.method === "POST") {
    const type = req.headers.get("content-type") ?? "";
    try {
      if (type.includes("json")) Object.assign(fields, await req.json());
      else Object.assign(fields, Object.fromEntries((await req.formData()).entries()));
    } catch {
      // query params only
    }
  }
  const summary = await importRows([fields], { channel: "sms", kind: "webhook", direction: "inbound", source: "sendmode" });
  // Non-200 makes failures visible in SendMode; details are in the Import log.
  return new Response(summary.imported + summary.duplicates > 0 ? "True" : `False: ${summary.errors[0] ?? "not imported"}`, {
    status: summary.imported + summary.duplicates > 0 ? 200 : 422,
    headers: { "content-type": "text/html" },
  });
}

export { handle as GET, handle as POST };
