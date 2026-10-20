import { ChannelBadge } from "@/components/badges";
import { ExportButton } from "@/components/export-button";
import { FilterForm } from "@/components/filter-form";
import { PageHeader } from "@/components/page-header";
import { RangeFields } from "@/components/range-fields";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { NativeSelect } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { campaignStats, parseRange } from "@/lib/stats";
import { getStore } from "@/lib/store";

export const dynamic = "force-dynamic";

type SP = Record<string, string | undefined>;

/** Horizontal bar for a rate, so variants can be compared at a glance. */
function RateBar({ value, best, channel }: { value: number; best: boolean; channel: "email" | "sms" }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 rounded-full bg-muted">
        <div className={`h-2 rounded-full ${channel === "email" ? "bg-email" : "bg-sms"}`} style={{ width: `${Math.min(100, value)}%` }} />
      </div>
      <span className={`text-xs tabular-nums ${best ? "font-semibold" : ""}`}>{value}%</span>
    </div>
  );
}

export default async function CampaignsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const sp = await searchParams;
  const range = parseRange({ ...sp, range: sp.range ?? "all" });
  const store = getStore();
  const [campaigns, messages, leads] = await Promise.all([store.all("campaigns"), store.all("messages"), store.all("leads")]);
  const stats = campaignStats(
    campaigns.filter((c) => !sp.channel || c.channel === sp.channel),
    messages,
    leads,
    range,
  )
    .filter((s) => s.sent > 0 || s.replied > 0)
    .sort((a, b) => b.sent - a.sent);

  return (
    <>
      <PageHeader title="Campaigns" description={`${stats.length} campaigns · ${range.label}`}>
        <FilterForm className="flex flex-wrap gap-2">
          <NativeSelect name="channel" defaultValue={sp.channel ?? ""} aria-label="Channel">
            <option value="">All channels</option>
            <option value="email">Cold email</option>
            <option value="sms">SMS</option>
          </NativeSelect>
          <RangeFields range={sp.range} from={sp.from} to={sp.to} defaultRange="all" />
        </FilterForm>
        <ExportButton view="campaigns" params={sp} />
      </PageHeader>

      <div className="mb-6 rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Campaign</TableHead>
              <TableHead>Channel</TableHead>
              <TableHead className="text-right">Sent</TableHead>
              <TableHead className="text-right">Replied</TableHead>
              <TableHead className="text-right">Positive</TableHead>
              <TableHead className="text-right">Booked</TableHead>
              <TableHead>Reply rate</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {stats.map((s) => (
              <TableRow key={s.campaign.id}>
                <TableCell className="font-medium">{s.campaign.name}<div className="text-xs font-normal text-muted-foreground">{s.campaign.source}</div></TableCell>
                <TableCell><ChannelBadge channel={s.campaign.channel} short /></TableCell>
                <TableCell className="text-right tabular-nums">{s.sent}</TableCell>
                <TableCell className="text-right tabular-nums">{s.replied}</TableCell>
                <TableCell className="text-right tabular-nums">{s.positive}</TableCell>
                <TableCell className="text-right tabular-nums">{s.booked}</TableCell>
                <TableCell><RateBar value={s.replyRate} best={false} channel={s.campaign.channel} /></TableCell>
              </TableRow>
            ))}
            {!stats.length && <TableRow><TableCell colSpan={7} className="py-10 text-center text-muted-foreground">No campaign activity in this period.</TableCell></TableRow>}
          </TableBody>
        </Table>
      </div>

      <h2 className="mb-3 text-sm font-semibold">Message variants</h2>
      <div className="grid gap-4 md:grid-cols-2">
        {stats.filter((s) => s.variants.length > 0).map((s) => {
          const best = Math.max(...s.variants.map((v) => v.replyRate));
          return (
            <Card key={s.campaign.id}>
              <CardHeader>
                <CardTitle className="text-sm">{s.campaign.name}</CardTitle>
                <CardDescription>First-touch messages only. Small numbers swing a lot - wait for 50+ sends per variant before picking a winner.</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Variant</TableHead>
                      <TableHead className="text-right">Contacted</TableHead>
                      <TableHead className="text-right">Replied</TableHead>
                      <TableHead className="text-right">Positive</TableHead>
                      <TableHead>Reply rate</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {s.variants.map((v) => (
                      <TableRow key={v.variant}>
                        <TableCell className="font-medium">{v.variant}{v.replyRate === best && s.variants.length > 1 && best > 0 ? " ★" : ""}</TableCell>
                        <TableCell className="text-right tabular-nums">{v.contacted}</TableCell>
                        <TableCell className="text-right tabular-nums">{v.replied}</TableCell>
                        <TableCell className="text-right tabular-nums">{v.positive}</TableCell>
                        <TableCell><RateBar value={v.replyRate} best={v.replyRate === best} channel={s.campaign.channel} /></TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </>
  );
}
