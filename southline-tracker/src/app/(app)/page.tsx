import { ArrowRight, CalendarClock, Clock, Flame, Inbox, TrendingUp } from "lucide-react";
import Link from "next/link";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { DailyBrief } from "@/components/daily-brief";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { currentUserEmail } from "@/lib/auth";
import { euro, formatMinutes, pipelineTotals, responseMinutes, scoreLead, speedToLead } from "@/lib/crm";
import { followUpQueue, groupBy, replyQueue } from "@/lib/repo";
import { getStore } from "@/lib/store";
import { formatDate } from "@/lib/utils";

// Today: the one screen to open first thing - who's waiting, who's hot, what's due.
export default async function TodayPage() {
  const store = getStore();
  const [queue, followUps, leads, messages, email] = await Promise.all([replyQueue(), followUpQueue(), store.all("leads"), store.all("messages"), currentUserEmail()]);
  const byLead = groupBy(messages, (m) => m.lead_id);
  const hot = leads
    .map((l) => ({ lead: l, s: scoreLead(l, byLead.get(l.id) ?? []) }))
    .filter((x) => x.s.hot)
    .sort((a, b) => b.s.score - a.s.score);
  const due = followUps.filter((f) => f.followUp);
  const speed = speedToLead(responseMinutes(messages, { from: new Date(Date.now() - 30 * 864e5).toISOString(), to: null }));
  const totals = pipelineTotals(leads);

  const hour = Number(new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Dublin", hour: "numeric", hour12: false }).format(new Date()));
  const hello = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  // Names per login come from APP_USER_NAMES ("login:Name,...") - never guessed from an email.
  const names = Object.fromEntries((process.env.APP_USER_NAMES ?? "").split(",").map((p) => p.split(":").map((x) => x.trim())).filter((p) => p.length === 2).map(([k, v]) => [k.toLowerCase(), v]));
  const name = (email && names[email.toLowerCase()]) || "";
  const who = name ? `, ${name}` : "";

  const tiles = [
    { label: "Waiting on you", value: String(queue.length), icon: Inbox, href: "/queue", warn: queue.length > 0 },
    { label: "Follow-ups due", value: String(due.length), icon: CalendarClock, href: "/follow-ups", warn: due.some((d) => d.overdue) },
    { label: "Hot leads", value: String(hot.length), icon: Flame, href: "/pipeline" },
    { label: "Median reply time (30d)", value: formatMinutes(speed.median), icon: Clock, href: "/dashboard", hint: speed.within1h !== null ? `${speed.within1h}% within 1h` : undefined },
    { label: "Weighted pipeline", value: `${euro(totals.weighted)}/mo`, icon: TrendingUp, href: "/pipeline" },
  ];

  return (
    <>
      <div className="mb-5">
        <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">{hello}{who}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{formatDate(new Date().toISOString())} · here&apos;s what needs you today.</p>
      </div>

      <DailyBrief />

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {tiles.map((t) => (
          <Link key={t.label} href={t.href} className="rounded-xl border bg-card p-4 transition-colors hover:bg-accent/50">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground"><t.icon className="size-3.5" /> {t.label}</div>
            <div className={`mt-1 text-2xl font-semibold tabular-nums ${t.warn ? "text-amber-700 dark:text-amber-300" : ""}`}>{t.value}</div>
            {t.hint && <div className="text-[11px] text-muted-foreground">{t.hint}</div>}
          </Link>
        ))}
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1.4fr_1fr]">
        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Waiting on your reply</CardTitle>
            <Button size="sm" asChild><Link href="/queue">Open reply queue <ArrowRight /></Link></Button>
          </CardHeader>
          <CardContent className="space-y-2">
            {queue.slice(0, 6).map((q) => (
              <Link key={q.reply.id} href="/queue" className="block rounded-lg border p-3 hover:bg-accent/40">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium">{q.lead.name ?? q.lead.phone}</span>
                  <ChannelBadge channel={q.reply.channel} short />
                  <TagBadge tag={q.reply.ai_tag} />
                  <span className="ml-auto text-xs text-muted-foreground">{formatMinutes(q.waitingMinutes)} ago</span>
                </div>
                <p className="mt-1 line-clamp-1 text-sm text-muted-foreground">“{q.reply.body}”</p>
              </Link>
            ))}
            {!queue.length && <p className="py-6 text-center text-sm text-muted-foreground">Nobody waiting. Nice.</p>}
          </CardContent>
        </Card>

        <div className="space-y-5">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-1.5"><Flame className="size-4 text-orange-500" /> Hottest leads</CardTitle></CardHeader>
            <CardContent className="space-y-2.5">
              {hot.slice(0, 5).map(({ lead, s }) => (
                <Link key={lead.id} href={`/leads/${lead.id}`} className="flex items-start justify-between gap-3 hover:opacity-80">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 text-sm font-medium">{lead.name ?? lead.business} <StatusBadge status={lead.status} /></div>
                    <div className="truncate text-xs text-muted-foreground">{s.reasons.slice(0, 3).join(" · ")}</div>
                  </div>
                  <span className="text-sm font-semibold tabular-nums text-orange-600 dark:text-orange-400">{s.score}</span>
                </Link>
              ))}
              {!hot.length && <p className="text-sm text-muted-foreground">No hot leads right now.</p>}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Follow-ups due</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {due.slice(0, 5).map((f) => (
                <Link key={f.followUp!.id} href={`/leads/${f.lead.id}`} className="flex items-center justify-between gap-3 text-sm hover:opacity-80">
                  <span className="truncate">{f.lead.name ?? f.lead.business} <span className="text-muted-foreground">- {f.reason}</span></span>
                  <span className={`shrink-0 text-xs ${f.overdue ? "text-destructive" : "text-muted-foreground"}`}>{f.overdue ? "overdue" : "today"}</span>
                </Link>
              ))}
              {!due.length && <p className="text-sm text-muted-foreground">Nothing scheduled for today.</p>}
              <Link href="/follow-ups" className="inline-block pt-1 text-xs underline">All follow-ups →</Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
