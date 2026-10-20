import { headers } from "next/headers";
import { CsvImportForm } from "@/components/csv-import-form";
import { TestConnection } from "@/components/test-connection";
import { ghlConfigured } from "@/lib/adapters/ghl";
import { sendmodeConfigured } from "@/lib/adapters/sendmode";
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

  const amp = q ? "&" : "?";
  const sendmodeOn = sendmodeConfigured();
  const ghlOn = ghlConfigured();

  const integrations = [
    {
      name: "GoHighLevel",
      on: ghlOn,
      status: ghlOn ? "API key set - contacts are looked up automatically" : "Webhooks work now. Add GHL_API_KEY + GHL_LOCATION_ID to fill in contact details.",
      test: "ghl" as const,
      urls: [
        { label: "Private Integration webhook (InboundMessage + OutboundMessage)", url: `${base}/api/integrations/ghl${q}` },
        { label: "Workflow webhook: email sent", url: `${base}/api/integrations/ghl${q}${amp}channel=email&direction=outbound` },
        { label: "Workflow webhook: customer replied (email)", url: `${base}/api/integrations/ghl${q}${amp}channel=email&direction=inbound` },
        { label: "Workflow webhook: SMS sent / replied", url: `${base}/api/integrations/ghl${q}${amp}channel=sms&direction=outbound  (or inbound)` },
      ],
    },
    {
      name: "SendMode",
      on: sendmodeOn,
      status: sendmodeOn ? "Access key set - you can send SMS from drafts" : "Replies + delivery reports work now. Add SENDMODE_ACCESS_KEY to send SMS from the app.",
      test: "sendmode" as const,
      urls: [
        { label: "Incoming SMS (replies) URL", url: `${base}/api/integrations/sendmode/inbound${q}` },
        { label: "Post Delivery Reports to URL", url: `${base}/api/integrations/sendmode/delivery${q}` },
      ],
    },
  ];

  const hooks = [
    { label: "Instantly / Smartlead / any email tool", url: `${base}/api/ingest/email${q}`, hint: "Add &source=instantly or &source=smartlead. Reply events are detected automatically." },
    { label: "Any SMS tool", url: `${base}/api/ingest/sms${q}${amp}direction=inbound`, hint: "Use direction=outbound for sends." },
  ];

  return (
    <>
      <PageHeader title="Import & connect" description="Bring sends and replies in by webhook (live) or CSV (any time)." />

      <div className="mb-5 grid gap-5 lg:grid-cols-2">
        {integrations.map((it) => (
          <Card key={it.name}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {it.name}
                <Badge variant="outline" className={it.on ? "border-emerald-500/40 text-emerald-700 dark:text-emerald-300" : "text-muted-foreground"}>
                  {it.on ? "Key set" : "Webhooks only"}
                </Badge>
              </CardTitle>
              <CardDescription>{it.status}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {it.urls.map((u) => (
                <div key={u.label} className="space-y-1">
                  <div className="text-xs font-medium">{u.label}</div>
                  <code className="block overflow-x-auto rounded bg-muted px-2 py-1.5 text-xs whitespace-nowrap">{u.url}</code>
                </div>
              ))}
              {it.on && <TestConnection target={it.test} />}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Other webhooks</CardTitle>
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
