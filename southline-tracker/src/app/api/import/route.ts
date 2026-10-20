import { NextResponse } from "next/server";
import { importRows } from "@/lib/importer";
import { parseCsv } from "@/lib/ingest";

// POST /api/import  (multipart form from the Import page; protected by login)
// fields: file, channel=email|sms, direction=outbound|inbound, source, campaign
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const form = await req.formData();
  const file = form.get("file");
  const channel = form.get("channel");
  if (!(file instanceof File)) return NextResponse.json({ error: "no file" }, { status: 400 });
  if (channel !== "email" && channel !== "sms") return NextResponse.json({ error: "channel must be email or sms" }, { status: 400 });

  const rows = parseCsv(await file.text());
  if (!rows.length) return NextResponse.json({ error: "CSV has no rows (is the first line a header?)" }, { status: 400 });

  const direction = form.get("direction");
  const summary = await importRows(rows, {
    channel,
    kind: "csv",
    direction: direction === "inbound" ? "inbound" : "outbound",
    source: (form.get("source") as string) || "csv",
    campaign: (form.get("campaign") as string) || null,
    filename: file.name,
  });
  return NextResponse.json(summary);
}
