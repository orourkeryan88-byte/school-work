import { ArrowDownLeft, ArrowUpRight, CalendarClock, Flame, History, Mail, MessageSquare, Phone, StickyNote } from "lucide-react";
import { Button } from "@/components/ui/button";
import { dealValue, euro, scoreLead, type Score } from "@/lib/crm";
import Link from "next/link";
import { notFound } from "next/navigation";
import { updateLeadAction } from "@/app/actions";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { ExportButton } from "@/components/export-button";
import { FollowUpDoneButton } from "@/components/followup-done";
import { LeadActions } from "@/components/lead-actions";
import { LeadForm } from "@/components/lead-form";
import { LeadSummary } from "@/components/lead-summary";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { sendmodeConfigured } from "@/lib/adapters/sendmode";
import { getLeadDetail, type TimelineItem } from "@/lib/repo";
import { formatDate, formatDateTime } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function LeadPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const detail = await getLeadDetail(id);
  if (!detail) notFound();
  const { lead, messages, followUps, timeline } = detail;
  const last = messages.at(-1);
  const score = scoreLead(lead, messages);
  const openFollowUps = followUps.filter((f) => !f.done_at).sort((a, b) => a.due_date.localeCompare(b.due_date));

  return (
    <>
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link href="/leads" className="text-xs text-muted-foreground hover:underline">← Leads</Link>
          <h1 className="mt-1 text-xl font-semibold sm:text-2xl">{lead.name ?? lead.email ?? lead.phone}</h1>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            {[lead.business, lead.trade, lead.county].filter(Boolean).join(" · ")}
            <StatusBadge status={lead.status} />
            {lead.unsubscribed && <Badge variant="destructive">Unsubscribed</Badge>}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {lead.phone && (
            <>
              <Button size="sm" variant="outline" asChild><a href={`tel:${lead.phone}`}><Phone /> Call</a></Button>
              <Button size="sm" variant="outline" asChild><a href={`sms:${lead.phone}`}><MessageSquare /> Text</a></Button>
              <Button size="sm" variant="outline" asChild><a href={`https://wa.me/${lead.phone.replace(/\D/g, "")}`} target="_blank" rel="noreferrer">WhatsApp</a></Button>
            </>
          )}
          {lead.email && <Button size="sm" variant="outline" asChild><a href={`mailto:${lead.email}`}><Mail /> Email</a></Button>}
          <ExportButton view="timeline" params={{ lead: lead.id }} />
        </div>
      </div>
      <ScoreStrip score={score} value={dealValue(lead)} />

      <div className="grid gap-5 lg:grid-cols-[1fr_22rem]">
        <div className="space-y-5">
          <Card>
            <CardHeader><CardTitle>Quick actions</CardTitle></CardHeader>
            <CardContent>
              <LeadActions
                leadId={lead.id}
                status={lead.status}
                channel={last?.channel ?? (lead.phone && !lead.email ? "sms" : "email")}
                messageId={last?.direction === "inbound" ? last.id : undefined}
                tag={last?.direction === "inbound" ? last.ai_tag : undefined}
                smsEnabled={sendmodeConfigured()}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Timeline</CardTitle></CardHeader>
            <CardContent>
              {timeline.length ? (
                <ol className="relative space-y-4 border-l pl-5">
                  {timeline.map((t) => <TimelineEntry key={`${t.type}-${itemId(t)}`} item={t} />)}
                </ol>
              ) : (
                <p className="text-sm text-muted-foreground">Nothing yet.</p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-5">
          <Card>
            <CardHeader><CardTitle>AI summary</CardTitle></CardHeader>
            <CardContent><LeadSummary leadId={lead.id} /></CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Follow-ups</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {openFollowUps.length ? openFollowUps.map((f) => (
                <div key={f.id} className="flex items-center justify-between gap-2 text-sm">
                  <div>
                    <div className="font-medium">{formatDate(f.due_date)}</div>
                    <div className="text-xs text-muted-foreground">{f.reason ?? "Follow up"}</div>
                  </div>
                  <FollowUpDoneButton id={f.id} />
                </div>
              )) : <p className="text-sm text-muted-foreground">None scheduled.</p>}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Details</CardTitle></CardHeader>
            <CardContent>
              <LeadForm lead={lead} action={updateLeadAction.bind(null, lead.id)} submit="Save details" />
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}

function itemId(t: TimelineItem) {
  return t.type === "message" ? t.message.id : t.type === "note" ? t.note.id : t.followUp.id;
}

/** One entry on the lead timeline: a send, a reply, a note, a status change or a follow-up. */
function TimelineEntry({ item }: { item: TimelineItem }) {
  const dot = "absolute -left-[29px] mt-0.5 flex size-4 items-center justify-center rounded-full border bg-background [&_svg]:size-2.5";
  if (item.type === "message") {
    const m = item.message;
    const inbound = m.direction === "inbound";
    return (
      <li className="relative">
        <span className={dot}>{inbound ? <ArrowDownLeft className="text-emerald-600" /> : <ArrowUpRight className="text-muted-foreground" />}</span>
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          <span className="font-medium text-foreground">{inbound ? "They replied" : "You sent"}</span>
          <ChannelBadge channel={m.channel} short />
          {inbound && <TagBadge tag={m.ai_tag} />}
          {item.campaign && <span>{item.campaign.name}{m.variant ? ` · ${m.variant}` : ""}</span>}
          <span>{formatDateTime(m.sent_at)}</span>
          {m.delivery_status && <span title="SendMode delivery report">· {m.delivery_status}</span>}
        </div>
        {m.subject && !inbound && <div className="mt-1 text-xs font-medium">{m.subject}</div>}
        <p className={`mt-1 rounded-md p-2.5 text-sm whitespace-pre-line ${inbound ? "bg-emerald-500/10" : "bg-muted"}`}>{m.body}</p>
      </li>
    );
  }
  if (item.type === "note") {
    const n = item.note;
    return (
      <li className="relative">
        <span className={dot}>{n.kind === "status" ? <History /> : <StickyNote />}</span>
        <div className="text-xs text-muted-foreground">
          {n.kind === "status" ? "Status change" : "Note"} · {formatDateTime(n.created_at)}
        </div>
        <p className={`mt-0.5 text-sm ${n.kind === "status" ? "text-muted-foreground" : ""}`}>{n.body}</p>
      </li>
    );
  }
  const f = item.followUp;
  return (
    <li className="relative">
      <span className={dot}><CalendarClock /></span>
      <div className="text-xs text-muted-foreground">Follow-up set · {formatDateTime(f.created_at)}</div>
      <p className="mt-0.5 text-sm">
        Due {formatDate(f.due_date)}{f.reason ? ` - ${f.reason}` : ""} {f.done_at && <span className="text-muted-foreground">(done)</span>}
      </p>
    </li>
  );
}

/** Score + value strip under the lead header: why they're hot, what they're worth. */
function ScoreStrip({ score, value }: { score: Score; value: number }) {
  return (
    <div className="-mt-2 mb-5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
      <span className={`flex items-center gap-1 font-semibold ${score.hot ? "text-orange-600 dark:text-orange-400" : "text-foreground"}`}>
        {score.hot && <Flame className="size-3.5" />} Score {score.score}
      </span>
      <span>{score.reasons.join(" · ")}</span>
      <span className="tabular-nums">Deal: {euro(value)}/mo</span>
    </div>
  );
}
