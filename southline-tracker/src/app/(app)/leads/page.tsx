import { Flame, MessageSquare, Phone, Plus } from "lucide-react";
import Link from "next/link";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { ExportButton } from "@/components/export-button";
import { FilterForm } from "@/components/filter-form";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { NativeSelect } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { LeadsViewSwitch } from "@/components/nav";
import { listLeads, listTrades } from "@/lib/repo";
import { LEAD_STATUSES, STATUS_LABELS, type Channel, type LeadStatus } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

export const dynamic = "force-dynamic";

type SP = Record<string, string | undefined>;

/** Search params without empty values, for building links. */
const clean = (sp: SP) => Object.fromEntries(Object.entries(sp).filter((e): e is [string, string] => Boolean(e[1])));

export default async function LeadsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const sp = await searchParams;
  const [leads, trades] = await Promise.all([
    listLeads({ q: sp.q, status: sp.status as LeadStatus, channel: sp.channel as Channel, trade: sp.trade, sort: (sp.sort as "recent" | "score" | "name") || "recent", hot: sp.hot === "1" }),
    listTrades(),
  ]);

  const showFilters = Boolean(sp.filters || sp.channel || sp.trade || sp.status || (sp.sort && sp.sort !== "recent"));

  // Pipeline counts across the current filter, shown as a strip.
  const counts = LEAD_STATUSES.map((s) => ({ s, n: leads.filter((l) => l.status === s).length }));

  return (
    <>
      <PageHeader title="Leads" description={`${leads.length} leads`}>
        <LeadsViewSwitch />
        <span className="hidden sm:inline-flex"><ExportButton view="leads" params={sp} /></span>
        <Button size="sm" asChild>
          <Link href="/leads/new"><Plus /> Add lead</Link>
        </Button>
      </PageHeader>

      <div className="mb-4 flex flex-wrap gap-1.5 text-xs">
        <Link href={sp.hot === "1" ? "/leads" : "/leads?hot=1&sort=score"} className={`flex items-center gap-1 rounded-md border px-2.5 py-1 ${sp.hot === "1" ? "border-orange-500/40 bg-orange-500/10 font-medium text-orange-700 dark:text-orange-300" : "text-muted-foreground hover:bg-accent/50"}`}>
          <Flame className="size-3" /> Hot
        </Link>
        {counts.map(({ s, n }) => (
          <Link key={s} href={sp.status === s ? "/leads" : `/leads?status=${s}`} className={`rounded-md border px-2.5 py-1 ${sp.status === s ? "bg-accent font-medium" : "text-muted-foreground hover:bg-accent/50"}`}>
            {STATUS_LABELS[s]} <span className="font-semibold text-foreground tabular-nums">{n}</span>
          </Link>
        ))}
      </div>

      <FilterForm className="mb-4 flex flex-wrap gap-2">
        <Input type="search" name="q" defaultValue={sp.q} placeholder="Search name, business, phone…" className="w-full sm:w-72" />
        {/* Phones show just search + chips; the rest opens with "More filters" */}
        {!showFilters && (
          <Link href={`/leads?${new URLSearchParams({ ...clean(sp), filters: "1" })}`} className="py-1.5 text-sm text-muted-foreground underline sm:hidden">More filters</Link>
        )}
        <div className={`${showFilters ? "flex" : "hidden"} w-full flex-wrap gap-2 sm:flex sm:w-auto`}>
          {showFilters && <input type="hidden" name="filters" value="1" />}
        <NativeSelect name="status" defaultValue={sp.status ?? ""} aria-label="Status">
          <option value="">All statuses</option>
          {LEAD_STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
        </NativeSelect>
        <NativeSelect name="channel" defaultValue={sp.channel ?? ""} aria-label="Channel">
          <option value="">All channels</option>
          <option value="email">Cold email</option>
          <option value="sms">SMS</option>
        </NativeSelect>
        <NativeSelect name="trade" defaultValue={sp.trade ?? ""} aria-label="Trade">
          <option value="">All trades</option>
          {trades.map((t) => <option key={t} value={t}>{t}</option>)}
        </NativeSelect>
        <NativeSelect name="sort" defaultValue={sp.sort ?? "recent"} aria-label="Sort">
          <option value="recent">Sort: most recent</option>
          <option value="score">Sort: hottest first</option>
          <option value="name">Sort: name A-Z</option>
        </NativeSelect>
        </div>
        {sp.hot === "1" && <input type="hidden" name="hot" value="1" />}
      </FilterForm>

      {/* Phone: one card per lead */}
      <div className="space-y-2.5 md:hidden">
        {leads.map((l) => (
          <div key={l.id} className="rounded-xl border bg-card p-3.5">
            <Link href={`/leads/${l.id}`} className="block">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="truncate font-medium">{l.name ?? l.business ?? l.email ?? l.phone ?? "Unknown"}</div>
                  <div className="truncate text-xs text-muted-foreground">{[l.name ? l.business : null, l.trade, l.county].filter(Boolean).join(" · ") || "No details yet"}</div>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1">
                  <StatusBadge status={l.status} />
                  <span className={`flex items-center gap-0.5 text-[11px] tabular-nums ${l.score.hot ? "font-semibold text-orange-600 dark:text-orange-400" : "text-muted-foreground"}`}>
                    {l.score.hot && <Flame className="size-3" />}Score {l.score.score}
                  </span>
                </div>
              </div>
              {l.last_reply && (
                <div className="mt-2 flex items-start gap-1.5 text-sm">
                  <TagBadge tag={l.last_reply.ai_tag} />
                  <span className="line-clamp-1 text-muted-foreground">“{l.last_reply.body}”</span>
                </div>
              )}
              <div className="mt-2 flex items-center gap-2 text-[11px] text-muted-foreground">
                {l.channels.map((c) => <ChannelBadge key={c} channel={c} short />)}
                <span className="tabular-nums">{l.sent} sent · {l.replies} {l.replies === 1 ? "reply" : "replies"}</span>
                <span className="ml-auto">{formatDateTime(l.last_activity)}</span>
              </div>
            </Link>
            {l.phone && !l.unsubscribed && (
              <div className="mt-2.5 flex gap-2 border-t pt-2.5">
                <Button size="sm" variant="outline" className="flex-1" asChild><a href={`tel:${l.phone}`}><Phone /> Call</a></Button>
                <Button size="sm" variant="outline" className="flex-1" asChild><a href={`sms:${l.phone}`}><MessageSquare /> Text</a></Button>
              </div>
            )}
          </div>
        ))}
        {!leads.length && <p className="py-10 text-center text-sm text-muted-foreground">No leads match.</p>}
      </div>

      <div className="hidden rounded-lg border md:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Lead</TableHead>
              <TableHead className="hidden md:table-cell">Trade / county</TableHead>
              <TableHead className="hidden md:table-cell">Channels</TableHead>
              <TableHead className="hidden md:table-cell text-right">Sent / replies</TableHead>
              <TableHead className="hidden lg:table-cell">Last reply</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Score</TableHead>
              <TableHead className="hidden md:table-cell">Last activity</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {leads.map((l) => (
              <TableRow key={l.id}>
                <TableCell>
                  <Link href={`/leads/${l.id}`} className="font-medium hover:underline">{l.name ?? l.email ?? l.phone ?? "Unknown"}</Link>
                  <div className="text-xs text-muted-foreground">{l.business}</div>
                </TableCell>
                <TableCell className="hidden text-xs sm:table-cell">
                  {l.trade ?? "—"}
                  <div className="text-muted-foreground">{l.county}</div>
                </TableCell>
                <TableCell className="hidden md:table-cell">
                  <div className="flex gap-1">{l.channels.map((c) => <ChannelBadge key={c} channel={c} short />)}</div>
                </TableCell>
                <TableCell className="hidden text-right tabular-nums md:table-cell">{l.sent} / {l.replies}</TableCell>
                <TableCell className="hidden max-w-64 lg:table-cell">
                  {l.last_reply ? (
                    <div className="space-y-1">
                      <TagBadge tag={l.last_reply.ai_tag} />
                      <div className="line-clamp-1 text-xs text-muted-foreground">{l.last_reply.body}</div>
                    </div>
                  ) : <span className="text-xs text-muted-foreground">—</span>}
                </TableCell>
                <TableCell><StatusBadge status={l.status} /></TableCell>
                <TableCell className={`text-right tabular-nums ${l.score.hot ? "font-semibold text-orange-600 dark:text-orange-400" : "text-muted-foreground"}`} title={l.score.reasons.join(" · ")}>{l.score.score}</TableCell>
                <TableCell className="hidden text-xs whitespace-nowrap text-muted-foreground sm:table-cell">{formatDateTime(l.last_activity)}</TableCell>
              </TableRow>
            ))}
            {!leads.length && (
              <TableRow><TableCell colSpan={8} className="py-10 text-center text-muted-foreground">No leads match.</TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </>
  );
}
