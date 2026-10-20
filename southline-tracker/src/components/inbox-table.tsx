"use client";

import { ChevronDown, ChevronRight } from "lucide-react";
import Link from "next/link";
import { Fragment, useState } from "react";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { LeadActions } from "@/components/lead-actions";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { InboxRow } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

/** Responses table (desktop) / card list (mobile). Click a row to open quick actions. */
export function InboxTable({ rows, smsEnabled }: { rows: InboxRow[]; smsEnabled?: boolean }) {
  const [open, setOpen] = useState<string | null>(null);
  const toggle = (id: string) => setOpen(open === id ? null : id);

  if (!rows.length) return <p className="py-12 text-center text-sm text-muted-foreground">No replies match these filters.</p>;

  return (
    <>
      {/* Mobile: cards */}
      <div className="space-y-3 md:hidden">
        {rows.map(({ reply, sent, lead }) => (
          <div key={reply.id} className="rounded-lg border p-3">
            <button className="w-full text-left" onClick={() => toggle(reply.id)}>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="font-medium">{lead.name ?? lead.email ?? lead.phone}</div>
                  <div className="text-xs text-muted-foreground">{[lead.business, lead.trade, lead.county].filter(Boolean).join(" · ")}</div>
                </div>
                <div className="text-right text-xs text-muted-foreground">{formatDateTime(reply.sent_at)}</div>
              </div>
              <p className="mt-2 text-sm">“{reply.body}”</p>
              {sent && <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">You: {sent.body}</p>}
              <div className="mt-2 flex flex-wrap gap-1.5">
                <ChannelBadge channel={reply.channel} />
                <TagBadge tag={reply.ai_tag} />
                <StatusBadge status={lead.status} />
              </div>
            </button>
            {open === reply.id && (
              <div className="mt-3 border-t pt-3">
                <LeadActions leadId={lead.id} status={lead.status} channel={reply.channel} messageId={reply.id} tag={reply.ai_tag} smsEnabled={smsEnabled} />
                <Link href={`/leads/${lead.id}`} className="mt-2 inline-block text-xs underline">Open full timeline →</Link>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Desktop: table */}
      <div className="hidden rounded-lg border md:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-6" />
              <TableHead>Contact</TableHead>
              <TableHead>Trade / county</TableHead>
              <TableHead>Channel</TableHead>
              <TableHead className="w-[24%]">Message I sent</TableHead>
              <TableHead className="w-[24%]">Their reply</TableHead>
              <TableHead>Time</TableHead>
              <TableHead>Tag / status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map(({ reply, sent, lead, campaign }) => (
              <Fragment key={reply.id}>
                <TableRow className="cursor-pointer" onClick={() => toggle(reply.id)} data-state={open === reply.id ? "open" : undefined}>
                  <TableCell className="pt-2.5 text-muted-foreground">{open === reply.id ? <ChevronDown className="size-4" /> : <ChevronRight className="size-4" />}</TableCell>
                  <TableCell>
                    <Link href={`/leads/${lead.id}`} onClick={(e) => e.stopPropagation()} className="font-medium hover:underline">
                      {lead.name ?? lead.email ?? lead.phone}
                    </Link>
                    <div className="text-xs text-muted-foreground">{lead.business}</div>
                  </TableCell>
                  <TableCell className="text-xs">
                    <div>{lead.trade ?? "—"}</div>
                    <div className="text-muted-foreground">{lead.county ?? ""}</div>
                  </TableCell>
                  <TableCell>
                    <ChannelBadge channel={reply.channel} short />
                    {campaign && <div className="mt-1 max-w-32 truncate text-xs text-muted-foreground" title={campaign.name}>{campaign.name}</div>}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    <span className="line-clamp-3">{sent?.body ?? "—"}</span>
                  </TableCell>
                  <TableCell className="text-sm">
                    <span className="line-clamp-3">{reply.body}</span>
                  </TableCell>
                  <TableCell className="text-xs whitespace-nowrap text-muted-foreground">{formatDateTime(reply.sent_at)}</TableCell>
                  <TableCell>
                    <div className="flex flex-col items-start gap-1">
                      <TagBadge tag={reply.ai_tag} />
                      <StatusBadge status={lead.status} />
                    </div>
                  </TableCell>
                </TableRow>
                {open === reply.id && (
                  <TableRow className="hover:bg-transparent">
                    <TableCell />
                    <TableCell colSpan={7} className="pb-4">
                      <LeadActions leadId={lead.id} status={lead.status} channel={reply.channel} messageId={reply.id} tag={reply.ai_tag} smsEnabled={smsEnabled} />
                    </TableCell>
                  </TableRow>
                )}
              </Fragment>
            ))}
          </TableBody>
        </Table>
      </div>
    </>
  );
}
