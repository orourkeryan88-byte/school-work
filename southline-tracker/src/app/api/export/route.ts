import { NextResponse } from "next/server";
import { toCsv } from "@/lib/ingest";
import { followUpQueue, getLeadDetail, listInbox, listLeads } from "@/lib/repo";
import { campaignStats, funnel, parseRange } from "@/lib/stats";
import { getStore } from "@/lib/store";
import type { Channel, LeadStatus, ReplyTag } from "@/lib/types";
import { CHANNEL_LABELS, STATUS_LABELS, TAG_LABELS } from "@/lib/types";
import { isoDay } from "@/lib/utils";

// GET /api/export?view=inbox|leads|campaigns|followups|dashboard|timeline|messages&<same filters as the page>
// Returns a CSV download of exactly what that page shows.
export const dynamic = "force-dynamic";

async function rowsFor(view: string, sp: Record<string, string>): Promise<Record<string, unknown>[] | null> {
  const store = getStore();
  switch (view) {
    case "inbox": {
      const range = parseRange({ ...sp, range: sp.range ?? "all" });
      const rows = await listInbox({ channel: sp.channel as Channel, status: sp.status as LeadStatus, tag: sp.tag as ReplyTag, trade: sp.trade, q: sp.q, from: range.from ?? undefined, to: range.to ?? undefined });
      return rows.map(({ reply, sent, lead, campaign }) => ({
        replied_at: reply.sent_at, name: lead.name, business: lead.business, email: lead.email, phone: lead.phone, trade: lead.trade, county: lead.county,
        channel: CHANNEL_LABELS[reply.channel], campaign: campaign?.name, variant: reply.variant, message_sent: sent?.body, reply: reply.body,
        tag: reply.ai_tag ? TAG_LABELS[reply.ai_tag] : "", status: STATUS_LABELS[lead.status],
      }));
    }
    case "leads": {
      const rows = await listLeads({ q: sp.q, status: sp.status as LeadStatus, channel: sp.channel as Channel, trade: sp.trade });
      return rows.map((l) => ({
        name: l.name, business: l.business, email: l.email, phone: l.phone, trade: l.trade, county: l.county, status: STATUS_LABELS[l.status],
        channels: l.channels.join(" + "), sent: l.sent, replies: l.replies, last_reply: l.last_reply?.body, last_reply_tag: l.last_reply?.ai_tag ? TAG_LABELS[l.last_reply.ai_tag] : "",
        last_activity: l.last_activity, booked_at: l.booked_at, won_at: l.won_at, unsubscribed: l.unsubscribed ? "yes" : "",
      }));
    }
    case "campaigns": {
      const range = parseRange({ ...sp, range: sp.range ?? "all" });
      const [campaigns, messages, leads] = await Promise.all([store.all("campaigns"), store.all("messages"), store.all("leads")]);
      const stats = campaignStats(campaigns.filter((c) => !sp.channel || c.channel === sp.channel), messages, leads, range);
      // One row per campaign plus one per variant.
      return stats.flatMap((s) => [
        { campaign: s.campaign.name, channel: CHANNEL_LABELS[s.campaign.channel], variant: "(all)", sent: s.sent, contacted: s.contacted, replied: s.replied, positive: s.positive, booked: s.booked, reply_rate_pct: s.replyRate },
        ...s.variants.map((v) => ({ campaign: s.campaign.name, channel: CHANNEL_LABELS[s.campaign.channel], variant: v.variant, sent: v.sent, contacted: v.contacted, replied: v.replied, positive: v.positive, booked: v.booked, reply_rate_pct: v.replyRate })),
      ]);
    }
    case "followups": {
      const q = await followUpQueue();
      return q.map((i) => ({
        due: i.dueDate, overdue: i.overdue ? "yes" : "", scheduled: i.followUp ? "yes" : "suggested", reason: i.reason, name: i.lead.name, business: i.lead.business,
        email: i.lead.email, phone: i.lead.phone, status: STATUS_LABELS[i.lead.status], last_message: i.lastMessage?.body, last_message_at: i.lastMessage?.sent_at,
      }));
    }
    case "dashboard": {
      const range = parseRange(sp);
      const [messages, leads] = await Promise.all([store.all("messages"), store.all("leads")]);
      return [["All", undefined], ["Cold email", "email"], ["SMS", "sms"]].map(([label, ch]) => ({
        range: range.label, channel: label, ...funnel(messages, leads, range, ch as Channel | undefined),
      }));
    }
    case "timeline": {
      const d = sp.lead ? await getLeadDetail(sp.lead) : null;
      if (!d) return [];
      return d.timeline.map((t) =>
        t.type === "message"
          ? { at: t.at, type: t.message.direction === "inbound" ? "reply" : "sent", channel: CHANNEL_LABELS[t.message.channel], campaign: t.campaign?.name, text: t.message.body, tag: t.message.ai_tag ?? "" }
          : t.type === "note"
            ? { at: t.at, type: t.note.kind === "status" ? "status" : "note", channel: "", campaign: "", text: t.note.body, tag: "" }
            : { at: t.at, type: "follow-up", channel: "", campaign: "", text: `Due ${t.followUp.due_date} ${t.followUp.reason ?? ""}`.trim(), tag: "" },
      );
    }
    case "messages": {
      const [messages, leads] = await Promise.all([store.all("messages"), store.all("leads")]);
      const byId = new Map(leads.map((l) => [l.id, l]));
      return messages.map((m) => ({ at: m.sent_at, direction: m.direction, channel: m.channel, email: byId.get(m.lead_id)?.email, phone: byId.get(m.lead_id)?.phone, business: byId.get(m.lead_id)?.business, body: m.body, tag: m.ai_tag ?? "", variant: m.variant, source: m.source }));
    }
  }
  return null;
}

export async function GET(req: Request) {
  const sp = Object.fromEntries(new URL(req.url).searchParams);
  const view = sp.view ?? "";
  const rows = await rowsFor(view, sp);
  if (!rows) return NextResponse.json({ error: "unknown view" }, { status: 400 });
  return new NextResponse(toCsv(rows), {
    headers: {
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": `attachment; filename="southline-${view}-${isoDay()}.csv"`,
    },
  });
}
