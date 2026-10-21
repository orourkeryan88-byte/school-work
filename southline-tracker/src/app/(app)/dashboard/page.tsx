import { CalendarCheck, Mail, MessageSquare, Percent, Send, Smile, Trophy } from "lucide-react";
import Link from "next/link";
import { DailyChart } from "@/components/daily-chart";
import { ExportButton } from "@/components/export-button";
import { FilterForm } from "@/components/filter-form";
import { PageHeader } from "@/components/page-header";
import { RangeFields } from "@/components/range-fields";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getStore } from "@/lib/store";
import { formatMinutes, responseMinutes, speedToLead } from "@/lib/crm";
import { dailySeries, funnel, parseRange, type Funnel } from "@/lib/stats";

export const dynamic = "force-dynamic";

type SP = Record<string, string | undefined>;

const METRICS: { key: keyof Funnel; label: string; icon: typeof Send; fmt?: (n: number) => string; hint: string }[] = [
  { key: "sent", label: "Sent", icon: Send, hint: "Messages sent" },
  { key: "replies", label: "Replies", icon: MessageSquare, hint: "Replies received" },
  { key: "replyRate", label: "Reply rate", icon: Percent, fmt: (n) => `${n}%`, hint: "Leads who replied ÷ leads contacted" },
  { key: "positive", label: "Positive", icon: Smile, hint: "Replies tagged Interested" },
  { key: "booked", label: "Calls booked", icon: CalendarCheck, hint: "Leads marked Booked in this period" },
  { key: "won", label: "Deals won", icon: Trophy, hint: "Leads marked Won in this period" },
];

export default async function DashboardPage({ searchParams }: { searchParams: Promise<SP> }) {
  const sp = await searchParams;
  const range = parseRange(sp);
  const store = getStore();
  const [messages, leads] = await Promise.all([store.all("messages"), store.all("leads")]);

  const total = funnel(messages, leads, range);
  const speed = speedToLead(responseMinutes(messages, range));
  const email = funnel(messages, leads, range, "email");
  const sms = funnel(messages, leads, range, "sms");

  const days = range.key === "7d" || range.key === "today" ? 7 : 30;
  const sentE = dailySeries(messages, days, "email");
  const sentS = dailySeries(messages, days, "sms");
  const replies = sentE.map((r, i) => ({ day: r.day, email: r.replies, sms: sentS[i].replies }));
  const sends = sentE.map((r, i) => ({ day: r.day, email: r.sent, sms: sentS[i].sent }));

  return (
    <>
      <PageHeader title="Stats" description={range.label}>
        <FilterForm className="flex flex-wrap gap-2">
          <RangeFields range={sp.range} from={sp.from} to={sp.to} />
        </FilterForm>
        <ExportButton view="dashboard" params={sp} />
      </PageHeader>

      {/* Headline numbers */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {METRICS.map(({ key, label, icon: Icon, fmt, hint }) => (
          <Card key={key} className="gap-1 py-4" title={hint}>
            <CardContent className="px-4">
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground"><Icon className="size-3.5" /> {label}</div>
              <div className="mt-1 text-2xl font-semibold tabular-nums">{fmt ? fmt(total[key]) : total[key]}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Cold email vs SMS side by side */}
      <div className="mt-5 grid gap-5 md:grid-cols-2">
        {([["email", "Cold email", Mail, email, "text-email"], ["sms", "SMS (SendMode)", MessageSquare, sms, "text-sms"]] as const).map(([ch, title, Icon, f, color]) => (
          <Card key={ch}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Icon className={`size-4 ${color}`} /> {title}</CardTitle>
              <CardDescription>{f.contacted} leads contacted · {f.replied} replied</CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-3 gap-y-4">
                {METRICS.map(({ key, label, fmt }) => (
                  <div key={key}>
                    <dt className="text-xs text-muted-foreground">{label}</dt>
                    <dd className="text-lg font-semibold tabular-nums">{fmt ? fmt(f[key]) : f[key]}</dd>
                  </div>
                ))}
              </dl>
              <Link href={`/inbox?channel=${ch}`} className="mt-4 inline-block text-xs underline">See {ch === "email" ? "email" : "SMS"} replies →</Link>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Replies per day</CardTitle><CardDescription>Last {days} days</CardDescription></CardHeader>
          <CardContent><DailyChart rows={replies} metric="replies" /></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Sends per day</CardTitle><CardDescription>Last {days} days</CardDescription></CardHeader>
          <CardContent><DailyChart rows={sends} metric="sent" /></CardContent>
        </Card>
      </div>

      {/* Speed to lead: how fast I answer replies in this period */}
      <Card className="mt-5">
        <CardHeader>
          <CardTitle>Speed to lead</CardTitle>
          <CardDescription>How fast you answer replies. Leads answered within the hour book far more often.</CardDescription>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-3 gap-4">
            <div><dt className="text-xs text-muted-foreground">Median reply time</dt><dd className="text-2xl font-semibold tabular-nums">{formatMinutes(speed.median)}</dd></div>
            <div><dt className="text-xs text-muted-foreground">Answered within 1h</dt><dd className="text-2xl font-semibold tabular-nums">{speed.within1h === null ? "—" : `${speed.within1h}%`}</dd></div>
            <div><dt className="text-xs text-muted-foreground">Replies answered</dt><dd className="text-2xl font-semibold tabular-nums">{speed.count}</dd></div>
          </dl>
        </CardContent>
      </Card>

      <p className="mt-4 text-xs text-muted-foreground">
        Bookings and wins are credited to the channel the lead first replied on. Reply rate = unique leads who replied ÷ unique leads contacted in the period.
      </p>
    </>
  );
}
