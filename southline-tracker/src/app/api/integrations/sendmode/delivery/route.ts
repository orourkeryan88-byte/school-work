import { applyDeliveryReport } from "@/lib/repo";
import { parseDeliveryReport } from "@/lib/adapters/sendmode";
import { checkIngestSecret } from "@/lib/ingest-auth";

// SendMode delivery reports.
// In SendMode: Settings → API Settings → "Post Delivery Reports to URL":
//   https://YOUR_APP/api/integrations/sendmode/delivery?secret=INGEST_SECRET
// SendMode sends EventID, Phonenumber, DataType, Status, CustomerID and
// expects the body "True" back.
export const dynamic = "force-dynamic";

async function handle(req: Request) {
  const auth = checkIngestSecret(req);
  if (!auth.ok) return new Response(auth.error, { status: auth.status });

  const fields: Record<string, unknown> = Object.fromEntries(new URL(req.url).searchParams);
  if (req.method === "POST") {
    const type = req.headers.get("content-type") ?? "";
    try {
      if (type.includes("json")) Object.assign(fields, await req.json());
      else if (type.includes("form")) Object.assign(fields, Object.fromEntries((await req.formData()).entries()));
    } catch {
      // fall back to query params only
    }
  }
  const report = parseDeliveryReport(fields);
  await applyDeliveryReport(report.customerId, report.status);
  // Always "True" so SendMode doesn't keep retrying reports for messages we don't know.
  return new Response("True", { headers: { "content-type": "text/html" } });
}

export { handle as GET, handle as POST };
