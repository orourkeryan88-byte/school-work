import { ExportButton } from "@/components/export-button";
import { FilterForm } from "@/components/filter-form";
import { InboxTable } from "@/components/inbox-table";
import { PageHeader } from "@/components/page-header";
import { RangeFields } from "@/components/range-fields";
import { Input } from "@/components/ui/input";
import { NativeSelect } from "@/components/ui/select";
import { listInbox, listTrades } from "@/lib/repo";
import { parseRange } from "@/lib/stats";
import { LEAD_STATUSES, REPLY_TAGS, STATUS_LABELS, TAG_LABELS, type Channel, type LeadStatus, type ReplyTag } from "@/lib/types";

export const dynamic = "force-dynamic";

type SP = Record<string, string | undefined>;

export default async function InboxPage({ searchParams }: { searchParams: Promise<SP> }) {
  const sp = await searchParams;
  const range = parseRange({ ...sp, range: sp.range ?? "all" });
  const [rows, trades] = await Promise.all([
    listInbox({
      channel: sp.channel as Channel,
      status: sp.status as LeadStatus,
      tag: sp.tag as ReplyTag,
      trade: sp.trade,
      q: sp.q,
      from: range.from ?? undefined,
      to: range.to ?? undefined,
    }),
    listTrades(),
  ]);
  const interested = rows.filter((r) => r.reply.ai_tag === "interested").length;

  return (
    <>
      <PageHeader title="Responses" description={`${rows.length} replies · ${interested} interested`}>
        <ExportButton view="inbox" params={sp} />
      </PageHeader>

      <FilterForm className="mb-4 flex flex-wrap gap-2">
        <Input type="search" name="q" defaultValue={sp.q} placeholder="Search name, business, reply…" className="w-full sm:w-60" />
        <NativeSelect name="channel" defaultValue={sp.channel ?? ""} aria-label="Channel">
          <option value="">All channels</option>
          <option value="email">Cold email</option>
          <option value="sms">SMS</option>
        </NativeSelect>
        <NativeSelect name="tag" defaultValue={sp.tag ?? ""} aria-label="Reply tag">
          <option value="">All tags</option>
          {REPLY_TAGS.map((t) => <option key={t} value={t}>{TAG_LABELS[t]}</option>)}
        </NativeSelect>
        <NativeSelect name="status" defaultValue={sp.status ?? ""} aria-label="Lead status">
          <option value="">All statuses</option>
          {LEAD_STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
        </NativeSelect>
        <NativeSelect name="trade" defaultValue={sp.trade ?? ""} aria-label="Trade">
          <option value="">All trades</option>
          {trades.map((t) => <option key={t} value={t}>{t}</option>)}
        </NativeSelect>
        <RangeFields range={sp.range} from={sp.from} to={sp.to} defaultRange="all" />
      </FilterForm>

      <InboxTable rows={rows} />
    </>
  );
}
