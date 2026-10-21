import { ArrowRight, CalendarClock, Flame, Inbox } from "lucide-react";
import Link from "next/link";
import { Avatar } from "@/components/avatar";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { DailyBrief } from "@/components/daily-brief";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { currentUserEmail } from "@/lib/auth";
import { formatMinutes, scoreLead } from "@/lib/crm";
import { followUpQueue, groupBy, replyQueue } from "@/lib/repo";
import { getStore } from "@/lib/store";
import { cn, formatDate } from "@/lib/utils";

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

  const hour = Number(new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Dublin", hour: "numeric", hour12: false }).format(new Date()));
  const hello = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  // Names per login come from APP_USER_NAMES ("login:Name,...") - never guessed from an email.
  const names = Object.fromEntries((process.env.APP_USER_NAMES ?? "").split(",").map((p) => p.split(":").map((x) => x.trim())).filter((p) => p.length === 2).map(([k, v]) => [k.toLowerCase(), v]));
  const name = (email && names[email.toLowerCase()]) || "";
  const who = name ? `, ${name}` : "";

  // Each tile gets its own tint so the three numbers read at a glance
  const tiles = [
    { label: "Waiting on you", value: String(queue.length), icon: Inbox, href: "/queue", tint: "bg-amber-500/15 text-amber-700 dark:text-amber-300" },
    { label: "Follow-ups due", value: String(due.length), icon: CalendarClock, href: "/follow-ups", tint: "bg-sky-500/15 text-sky-700 dark:text-sky-300", note: due.some((d) => d.overdue) ? "some overdue" : "" },
    { label: "Hot leads", value: String(hot.length), icon: Flame, href: "/leads?hot=1&sort=score", tint: "bg-orange-500/15 text-orange-600 dark:text-orange-400" },
  ];

  return (
    <>
      <div className="mb-5">
        <p className="text-xs font-semibold tracking-wider text-brand-ink uppercase">{formatDate(new Date().toISOString())}</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-balance sm:text-3xl">{hello}{who}</h1>
        <p className="mt-1 text-sm text-muted-foreground">Here&apos;s what needs you today.</p>
      </div>

      <DailyBrief />

      <div className="mt-4 grid grid-cols-3 gap-2.5 sm:gap-4">
        {tiles.map((t) => (
          <Link key={t.label} href={t.href} className="rounded-2xl border bg-card p-3 shadow-card transition hover:-translate-y-0.5 hover:border-brand-accent/40 sm:p-4">
            <span className={cn("inline-flex size-8 items-center justify-center rounded-lg sm:size-9", t.tint)}><t.icon className="size-4" /></span>
            <div className="mt-2.5 text-2xl font-semibold tracking-tight tabular-nums sm:text-3xl">{t.value}</div>
            <div className="text-xs leading-tight text-muted-foreground sm:text-sm">{t.label}</div>
            {t.note && <div className="mt-1 text-[11px] font-medium text-destructive">{t.note}</div>}
          </Link>
        ))}
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1.4fr_1fr] [&>*]:min-w-0">
        <Card>
          <CardHeader className="flex-row flex-wrap items-center justify-between gap-2">
            <CardTitle>Waiting on your reply</CardTitle>
            <Button size="sm" asChild><Link href="/queue">Reply now <ArrowRight /></Link></Button>
          </CardHeader>
          <CardContent className="-mt-1 space-y-0.5 px-3">
            {queue.slice(0, 6).map((q) => (
              <Link key={q.reply.id} href="/queue" className="flex items-start gap-3 rounded-xl p-2.5 transition-colors hover:bg-accent/70">
                <Avatar name={q.lead.name ?? q.lead.business} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-baseline gap-2">
                    <span className="truncate font-medium">{q.lead.name ?? q.lead.phone}</span>
                    <span className="ml-auto shrink-0 text-xs text-muted-foreground tabular-nums">{formatMinutes(q.waitingMinutes)} ago</span>
                  </div>
                  <p className="line-clamp-1 text-sm text-muted-foreground">“{q.reply.body}”</p>
                  <div className="mt-1.5 flex flex-wrap gap-1.5">
                    <ChannelBadge channel={q.reply.channel} short />
                    <TagBadge tag={q.reply.ai_tag} />
                  </div>
                </div>
              </Link>
            ))}
            {!queue.length && <p className="py-6 text-center text-sm text-muted-foreground">Nobody waiting. Nice.</p>}
          </CardContent>
        </Card>

        <div className="space-y-5">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-1.5"><Flame className="size-4 text-orange-500" /> Hottest leads</CardTitle></CardHeader>
            <CardContent className="-mt-1 space-y-0.5 px-3">
              {hot.slice(0, 5).map(({ lead, s }) => (
                <Link key={lead.id} href={`/leads/${lead.id}`} className="flex items-center gap-3 rounded-xl p-2 transition-colors hover:bg-accent/70">
                  <Avatar name={lead.name ?? lead.business} className="size-8" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 text-sm font-medium"><span className="truncate">{lead.name ?? lead.business}</span> <StatusBadge status={lead.status} /></div>
                    <div className="truncate text-xs text-muted-foreground">{s.reasons.slice(0, 3).join(" · ")}</div>
                  </div>
                  <span className="shrink-0 rounded-full bg-orange-500/12 px-2 py-0.5 text-xs font-semibold tabular-nums text-orange-700 dark:text-orange-300" title="Lead score out of 100">{s.score}</span>
                </Link>
              ))}
              {!hot.length && <p className="text-sm text-muted-foreground">No hot leads right now.</p>}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Follow-ups due</CardTitle></CardHeader>
            <CardContent className="-mt-1 space-y-0.5 px-3">
              {due.slice(0, 5).map((f) => (
                <Link key={f.followUp!.id} href={`/leads/${f.lead.id}`} className="flex items-center gap-3 rounded-xl p-2 text-sm transition-colors hover:bg-accent/70">
                  <Avatar name={f.lead.name ?? f.lead.business} className="size-8" />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-medium">{f.lead.name ?? f.lead.business}</span>
                    <span className="block truncate text-xs text-muted-foreground">{f.reason}</span>
                  </span>
                  <span className={cn("shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium", f.overdue ? "bg-destructive/12 text-destructive" : "bg-secondary text-muted-foreground")}>{f.overdue ? "overdue" : "today"}</span>
                </Link>
              ))}
              {!due.length && <p className="px-2 text-sm text-muted-foreground">Nothing scheduled for today.</p>}
              <Link href="/follow-ups" className="inline-block px-2 pt-1.5 text-xs font-medium text-brand-ink hover:underline">All follow-ups →</Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
