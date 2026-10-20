import type { Campaign, Channel, Lead, Message } from "@/lib/types";
import { addDays, isoDay, parseDate, pct } from "@/lib/utils";

// Pure functions that turn rows into dashboard / campaign numbers.
// Kept free of I/O so they're easy to test.

export interface Funnel {
  sent: number; // outbound messages
  contacted: number; // unique leads messaged
  replies: number; // inbound messages
  replied: number; // unique leads who replied
  replyRate: number; // replied / contacted, %
  positive: number; // replies tagged Interested
  booked: number;
  won: number;
}

export type DateRange = { from: string | null; to: string | null; label: string; key: string };

/** Parse ?range=today|7d|30d|all|custom&from=YYYY-MM-DD&to=YYYY-MM-DD */
export function parseRange(sp: { range?: string; from?: string; to?: string }): DateRange {
  const today = isoDay();
  // Day boundaries in Irish time.
  const start = (day: string) => parseDate(`${day}T00:00:00`)!;
  const end = (day: string) => parseDate(`${day}T23:59:59`)!;
  switch (sp.range) {
    case "today":
      return { key: "today", label: "Today", from: start(today), to: null };
    case "7d":
      return { key: "7d", label: "Last 7 days", from: start(addDays(today, -6)), to: null };
    case "all":
      return { key: "all", label: "All time", from: null, to: null };
    case "custom":
      return {
        key: "custom",
        label: `${sp.from ?? "…"} → ${sp.to ?? "…"}`,
        from: sp.from ? start(sp.from) : null,
        to: sp.to ? end(sp.to) : null,
      };
    default:
      return { key: "30d", label: "Last 30 days", from: start(addDays(today, -29)), to: null };
  }
}

export function inRange(iso: string | null, r: Pick<DateRange, "from" | "to">) {
  if (!iso) return false;
  return (!r.from || iso >= r.from) && (!r.to || iso <= r.to);
}

/**
 * Which channel "gets credit" for a lead's booking/win: the channel they
 * first replied on, else the first channel we contacted them on.
 */
export function attributedChannel(leadMessages: Message[]): Channel | null {
  const sorted = [...leadMessages].sort((a, b) => a.sent_at.localeCompare(b.sent_at));
  return (sorted.find((m) => m.direction === "inbound") ?? sorted[0])?.channel ?? null;
}

export function funnel(messages: Message[], leads: Lead[], range: Pick<DateRange, "from" | "to">, channel?: Channel): Funnel {
  const msgs = messages.filter((m) => inRange(m.sent_at, range) && (!channel || m.channel === channel));
  const out = msgs.filter((m) => m.direction === "outbound");
  const inb = msgs.filter((m) => m.direction === "inbound");
  const contacted = new Set(out.map((m) => m.lead_id)).size;
  const replied = new Set(inb.map((m) => m.lead_id)).size;

  // Bookings/wins are counted by when they happened, credited to one channel.
  const byLead = new Map<string, Message[]>();
  for (const m of messages) byLead.set(m.lead_id, [...(byLead.get(m.lead_id) ?? []), m]);
  const credited = (l: Lead) => !channel || attributedChannel(byLead.get(l.id) ?? []) === channel;

  return {
    sent: out.length,
    contacted,
    replies: inb.length,
    replied,
    replyRate: pct(replied, contacted),
    positive: inb.filter((m) => m.ai_tag === "interested").length,
    booked: leads.filter((l) => inRange(l.booked_at, range) && credited(l)).length,
    won: leads.filter((l) => inRange(l.won_at, range) && credited(l)).length,
  };
}

/** Sends and replies per day, for the activity chart. */
export function dailySeries(messages: Message[], days: number, channel?: Channel) {
  const today = isoDay();
  const rows = Array.from({ length: days }, (_, i) => ({ day: addDays(today, i - days + 1), sent: 0, replies: 0 }));
  const idx = new Map(rows.map((r, i) => [r.day, i]));
  for (const m of messages) {
    if (channel && m.channel !== channel) continue;
    const i = idx.get(isoDay(m.sent_at));
    if (i === undefined) continue;
    if (m.direction === "outbound") rows[i].sent++;
    else rows[i].replies++;
  }
  return rows;
}

export interface CampaignStats {
  campaign: Campaign;
  sent: number;
  contacted: number;
  replied: number;
  positive: number;
  booked: number;
  replyRate: number;
  positiveRate: number;
  variants: { variant: string; sent: number; contacted: number; replied: number; positive: number; booked: number; replyRate: number }[];
}

/**
 * Per-campaign and per-variant performance. A lead counts as "replied" for a
 * variant if they replied to a message from that variant.
 */
export function campaignStats(campaigns: Campaign[], messages: Message[], leads: Lead[], range: Pick<DateRange, "from" | "to">): CampaignStats[] {
  const leadById = new Map(leads.map((l) => [l.id, l]));
  return campaigns.map((campaign) => {
    const msgs = messages.filter((m) => m.campaign_id === campaign.id && inRange(m.sent_at, range));
    const calc = (subset: Message[]) => {
      const out = subset.filter((m) => m.direction === "outbound");
      const inb = subset.filter((m) => m.direction === "inbound");
      const contactedIds = new Set(out.map((m) => m.lead_id));
      const repliedIds = new Set(inb.map((m) => m.lead_id));
      const positiveIds = new Set(inb.filter((m) => m.ai_tag === "interested").map((m) => m.lead_id));
      const booked = [...contactedIds].filter((id) => leadById.get(id)?.booked_at).length;
      return {
        sent: out.length,
        contacted: contactedIds.size,
        replied: repliedIds.size,
        positive: positiveIds.size,
        booked,
        replyRate: pct(repliedIds.size, contactedIds.size),
      };
    };
    const all = calc(msgs);
    // Variants are compared on first-touch messages only (follow-ups excluded).
    const variantNames = [...new Set(msgs.map((m) => m.variant).filter((v): v is string => !!v && !/follow/i.test(v)))].sort();
    return {
      campaign,
      ...all,
      positiveRate: pct(all.positive, all.contacted),
      variants: variantNames.map((variant) => ({ variant, ...calc(msgs.filter((m) => m.variant === variant)) })),
    };
  });
}
