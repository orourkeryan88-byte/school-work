import Link from "next/link";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { DraftBox } from "@/components/draft-box";
import { ExportButton } from "@/components/export-button";
import { FollowUpActions } from "@/components/followup-actions";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { sendmodeConfigured } from "@/lib/adapters/sendmode";
import { templateDraft } from "@/lib/ai";
import { followUpQueue } from "@/lib/repo";
import { getStore } from "@/lib/store";
import { addDays, formatDate, formatDateTime, isoDay } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function FollowUpsPage() {
  const today = isoDay();
  const [queue, all, leads] = await Promise.all([followUpQueue(today), getStore().all("follow_ups"), getStore().all("leads")]);
  const upcoming = all
    .filter((f) => !f.done_at && f.due_date > today && f.due_date <= addDays(today, 7))
    .sort((a, b) => a.due_date.localeCompare(b.due_date));
  const smsOn = await sendmodeConfigured();
  const leadName = new Map(leads.map((l) => [l.id, l.name ?? l.business ?? l.email ?? l.phone ?? "Lead"]));

  const card = (item: (typeof queue)[number]) => {
    const { lead, lastMessage: last } = item;
    return (
      <Card key={`${lead.id}-${item.followUp?.id ?? "auto"}`} className="py-4">
        <CardContent className="grid gap-4 px-4 md:grid-cols-[1fr_1.2fr]">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <Link href={`/leads/${lead.id}`} className="font-medium hover:underline">{lead.name ?? lead.email ?? lead.phone}</Link>
              <StatusBadge status={lead.status} />
              {item.overdue && <Badge variant="destructive">Overdue · {formatDate(item.dueDate)}</Badge>}
              {!item.followUp && <Badge variant="outline">Suggested</Badge>}
            </div>
            <div className="text-xs text-muted-foreground">{[lead.business, lead.trade, lead.county].filter(Boolean).join(" · ")}</div>
            <div className="text-sm font-medium">{item.reason}</div>
            {last && (
              <div className="rounded-md bg-muted p-2.5 text-sm">
                <div className="mb-1 flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                  {last.direction === "inbound" ? "They said" : "You said"} · <ChannelBadge channel={last.channel} short /> {last.direction === "inbound" && <TagBadge tag={last.ai_tag} />} · {formatDateTime(last.sent_at)}
                </div>
                <span className="line-clamp-3">{last.body}</span>
              </div>
            )}
            <FollowUpActions leadId={lead.id} followUpId={item.followUp?.id ?? null} reason={item.reason} />
          </div>
          <div>
            <div className="mb-1.5 text-xs font-medium text-muted-foreground">Suggested message</div>
            <DraftBox leadId={lead.id} channel={last?.channel ?? "email"} initial={templateDraft(lead, last)} goal={item.reason} smsEnabled={smsOn} />
          </div>
        </CardContent>
      </Card>
    );
  };

  // People waiting on me first; cold "no reply yet" nudges tucked below.
  const isNudge = (i: (typeof queue)[number]) => !i.followUp && i.lead.status === "contacted";
  const now = queue.filter((i) => !isNudge(i));
  const nudges = queue.filter(isNudge);

  return (
    <>
      <PageHeader title="Follow-ups" description={`${now.length} waiting on you · ${nudges.length} to nudge · ${formatDate(today)}`}>
        <ExportButton view="followups" />
      </PageHeader>

      <div className="space-y-3">
        {now.map(card)}
        {!now.length && <p className="py-12 text-center text-sm text-muted-foreground">Nobody waiting on you today. Nice.</p>}
      </div>

      {nudges.length > 0 && (
        <details className="mt-8">
          <summary className="cursor-pointer text-sm font-semibold">No reply yet - {nudges.length} leads to nudge</summary>
          <div className="mt-3 space-y-3">{nudges.map(card)}</div>
        </details>
      )}

      {upcoming.length > 0 && (
        <div className="mt-8">
          <h2 className="mb-2 text-sm font-semibold">Coming up (next 7 days)</h2>
          <ul className="divide-y rounded-lg border text-sm">
            {upcoming.map((f) => (
              <li key={f.id} className="flex items-center justify-between gap-3 px-3 py-2">
                <Link href={`/leads/${f.lead_id}`} className="hover:underline">{leadName.get(f.lead_id)}</Link>
                <span className="truncate text-xs text-muted-foreground">{f.reason}</span>
                <span className="text-xs whitespace-nowrap tabular-nums">{formatDate(f.due_date)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
