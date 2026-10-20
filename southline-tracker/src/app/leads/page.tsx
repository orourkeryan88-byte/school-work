import { Plus } from "lucide-react";
import Link from "next/link";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { ExportButton } from "@/components/export-button";
import { FilterForm } from "@/components/filter-form";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { NativeSelect } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { listLeads, listTrades } from "@/lib/repo";
import { LEAD_STATUSES, STATUS_LABELS, type Channel, type LeadStatus } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

export const dynamic = "force-dynamic";

type SP = Record<string, string | undefined>;

export default async function LeadsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const sp = await searchParams;
  const [leads, trades] = await Promise.all([
    listLeads({ q: sp.q, status: sp.status as LeadStatus, channel: sp.channel as Channel, trade: sp.trade }),
    listTrades(),
  ]);

  // Pipeline counts across the current filter, shown as a strip.
  const counts = LEAD_STATUSES.map((s) => ({ s, n: leads.filter((l) => l.status === s).length }));

  return (
    <>
      <PageHeader title="Leads" description={`${leads.length} leads`}>
        <ExportButton view="leads" params={sp} />
        <Button size="sm" asChild>
          <Link href="/leads/new"><Plus /> Add lead</Link>
        </Button>
      </PageHeader>

      <div className="mb-4 flex flex-wrap gap-1.5 text-xs">
        {counts.map(({ s, n }) => (
          <Link key={s} href={sp.status === s ? "/leads" : `/leads?status=${s}`} className={`rounded-md border px-2.5 py-1 ${sp.status === s ? "bg-accent font-medium" : "text-muted-foreground hover:bg-accent/50"}`}>
            {STATUS_LABELS[s]} <span className="font-semibold text-foreground tabular-nums">{n}</span>
          </Link>
        ))}
      </div>

      <FilterForm className="mb-4 flex flex-wrap gap-2">
        <Input type="search" name="q" defaultValue={sp.q} placeholder="Search name, business, email, phone…" className="w-full sm:w-72" />
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
      </FilterForm>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Lead</TableHead>
              <TableHead className="hidden sm:table-cell">Trade / county</TableHead>
              <TableHead className="hidden md:table-cell">Channels</TableHead>
              <TableHead className="hidden md:table-cell text-right">Sent / replies</TableHead>
              <TableHead className="hidden lg:table-cell">Last reply</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="hidden sm:table-cell">Last activity</TableHead>
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
                <TableCell className="hidden text-xs whitespace-nowrap text-muted-foreground sm:table-cell">{formatDateTime(l.last_activity)}</TableCell>
              </TableRow>
            ))}
            {!leads.length && (
              <TableRow><TableCell colSpan={7} className="py-10 text-center text-muted-foreground">No leads match.</TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </>
  );
}
