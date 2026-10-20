import { headers } from "next/headers";
import { CsvImportForm } from "@/components/csv-import-form";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getStore } from "@/lib/store";
import { CHANNEL_LABELS } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function ImportPage() {
  const h = await headers();
  const base = process.env.APP_URL || `${h.get("x-forwarded-proto") ?? "http"}://${h.get("host")}`;
  const secret = process.env.INGEST_SECRET ? "YOUR_INGEST_SECRET" : null;
  const q = secret ? `?secret=${secret}` : "";
  const logs = (await getStore().all("import_logs")).sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 25);

  const hooks = [
    { label: "Cold email: sent + replies", url: `${base}/api/ingest/email${q}`, hint: "Instantly / Smartlead / GHL webhooks. Reply events are detected automatically (event names containing \"reply\")." },
    { label: "SendMode: inbound SMS (replies)", url: `${base}/api/ingest/sms${q}${q ? "&" : "?"}direction=inbound&source=sendmode`, hint: "Set as the inbound SMS forwarding URL. Needs the sender number and message text." },
    { label: "SendMode: sent SMS", url: `${base}/api/ingest/sms${q}${q ? "&" : "?"}direction=outbound&source=sendmode`, hint: "Optional - or import the sent report as CSV after each blast." },
  ];

  return (
    <>
      <PageHeader title="Import & connect" description="Bring sends and replies in by webhook (live) or CSV (any time)." />

      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Webhooks</CardTitle>
            <CardDescription>
              Point your tools at these URLs. {secret ? "Replace YOUR_INGEST_SECRET with the INGEST_SECRET from your env." : "No INGEST_SECRET set - open in demo mode only."}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {hooks.map((hk) => (
              <div key={hk.label} className="space-y-1">
                <div className="text-sm font-medium">{hk.label}</div>
                <code className="block overflow-x-auto rounded bg-muted px-2 py-1.5 text-xs whitespace-nowrap">{hk.url}</code>
                <p className="text-xs text-muted-foreground">{hk.hint}</p>
              </div>
            ))}
            <p className="text-xs text-muted-foreground">Full field list and setup steps per tool are in the README.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>CSV import</CardTitle>
            <CardDescription>
              Column names are matched loosely (email / phone / company / message / campaign / date…). Re-importing the same file won&apos;t create duplicates.
              Samples:{" "}
              {["email-sent", "email-replies", "sms-sent", "sms-replies"].map((s, i) => (
                <span key={s}>{i > 0 && ", "}<a className="underline" href={`/samples/${s}.csv`} download>{s}.csv</a></span>
              ))}
            </CardDescription>
          </CardHeader>
          <CardContent><CsvImportForm /></CardContent>
        </Card>
      </div>

      <Card className="mt-5">
        <CardHeader><CardTitle>Import log</CardTitle><CardDescription>Last 25 webhook calls and imports.</CardDescription></CardHeader>
        <CardContent>
          {logs.length ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>When</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Channel</TableHead>
                  <TableHead>Source / file</TableHead>
                  <TableHead className="text-right">Imported</TableHead>
                  <TableHead>Errors</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((l) => (
                  <TableRow key={l.id}>
                    <TableCell className="text-xs whitespace-nowrap">{formatDateTime(l.created_at)}</TableCell>
                    <TableCell><Badge variant="outline">{l.kind}</Badge></TableCell>
                    <TableCell className="text-xs">{CHANNEL_LABELS[l.channel]}</TableCell>
                    <TableCell className="text-xs">{l.filename ?? l.source ?? "—"}</TableCell>
                    <TableCell className="text-right tabular-nums">{l.rows_imported} / {l.rows_total}</TableCell>
                    <TableCell className="max-w-72 truncate text-xs text-muted-foreground" title={l.errors.join("\n")}>{l.errors[0] ?? ""}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : <p className="text-sm text-muted-foreground">Nothing imported yet.</p>}
        </CardContent>
      </Card>
    </>
  );
}
