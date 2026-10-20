import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { PipelineBoard, type BoardCard } from "@/components/pipeline-board";
import { Card, CardContent } from "@/components/ui/card";
import { dealValue, defaultDealValue, euro, pipelineTotals, scoreLead, STAGE_PROBABILITY } from "@/lib/crm";
import { groupBy } from "@/lib/repo";
import { getStore } from "@/lib/store";
import { pct } from "@/lib/utils";

export const metadata: Metadata = { title: "Pipeline" };

export default async function PipelinePage() {
  const store = getStore();
  const [leads, messages] = await Promise.all([store.all("leads"), store.all("messages")]);
  const byLead = groupBy(messages, (m) => m.lead_id);
  const now = Date.now();

  const cards: BoardCard[] = leads
    .filter((l) => l.status !== "new")
    .map((l) => {
      const msgs = byLead.get(l.id) ?? [];
      const s = scoreLead(l, msgs, now);
      const last = msgs.reduce((acc, m) => (m.sent_at > acc ? m.sent_at : acc), l.updated_at);
      return { id: l.id, name: l.name ?? l.business ?? l.email ?? l.phone ?? "Lead", business: l.name ? l.business : null, status: l.status, value: dealValue(l), score: s.score, hot: s.hot, lastActivity: last };
    });

  const t = pipelineTotals(leads);
  const won = leads.filter((l) => l.status === "won").length;
  const lost = leads.filter((l) => l.status === "lost").length;
  const tiles = [
    { label: "Open pipeline", value: `${euro(t.openValue)}/mo`, hint: `${t.openCount} open deals` },
    { label: "Weighted forecast", value: `${euro(t.weighted)}/mo`, hint: "Each deal × its stage's win chance" },
    { label: "Won (MRR)", value: `${euro(t.wonMrr)}/mo`, hint: `${won} customers` },
    { label: "Win rate", value: `${pct(won, won + lost)}%`, hint: "Won ÷ (won + lost)" },
  ];

  return (
    <>
      <PageHeader title="Pipeline" description={`Drag deals between stages. Deals without a value count as ${euro(defaultDealValue())}/mo - set it on the lead.`} />
      <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {tiles.map((x) => (
          <Card key={x.label} className="gap-1 py-4" title={x.hint}>
            <CardContent className="px-4">
              <div className="text-xs text-muted-foreground">{x.label}</div>
              <div className="mt-1 text-xl font-semibold tabular-nums">{x.value}</div>
              <div className="text-[11px] text-muted-foreground">{x.hint}</div>
            </CardContent>
          </Card>
        ))}
      </div>
      <PipelineBoard cards={cards} />
      <p className="mt-2 text-xs text-muted-foreground">
        Win chance used for the forecast: {Object.entries(STAGE_PROBABILITY).filter(([k]) => !["new", "won", "lost"].includes(k)).map(([k, v]) => `${k} ${Math.round(v * 100)}%`).join(" · ")}
      </p>
    </>
  );
}
