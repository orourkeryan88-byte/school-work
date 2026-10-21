"use client";

import { ExternalLink, Globe, Loader2, Phone, RefreshCw, Search, UserPlus } from "lucide-react";
import Link from "next/link";
import { useEffect, useState, useTransition } from "react";
import { crmLookupAction, saveLookupAction, webLookupAction } from "@/app/actions";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { WebLookup } from "@/lib/lookup";
import { formatDateTime } from "@/lib/utils";

type Crm = Awaited<ReturnType<typeof crmLookupAction>>;

const CONFIDENCE: Record<WebLookup["confidence"], string> = {
  high: "border-emerald-500/40 text-emerald-700 dark:text-emerald-300",
  medium: "border-sky-500/40 text-sky-700 dark:text-sky-300",
  low: "border-amber-500/40 text-amber-700 dark:text-amber-300",
  none: "text-muted-foreground",
};

/** Paste a number → what the CRM knows + what Claude finds in public business listings. */
export function CheckNumber({ initial, aiOn }: { initial?: string; aiOn: boolean }) {
  const [number, setNumber] = useState(initial ?? "");
  const [checked, setChecked] = useState<string | null>(null);
  const [crm, setCrm] = useState<Crm | undefined>(undefined);
  const [web, setWeb] = useState<WebLookup | null>(null);
  const [savedId, setSavedId] = useState<string | null>(null);
  const [crmPending, startCrm] = useTransition();
  const [webPending, startWeb] = useTransition();
  const [savePending, startSave] = useTransition();

  const check = (n: string, fresh = false) => {
    if (!n.trim()) return;
    setChecked(n);
    setSavedId(null);
    if (!fresh) setCrm(undefined);
    setWeb(null);
    history.replaceState(null, "", `/check?number=${encodeURIComponent(n)}`);
    if (!fresh) startCrm(async () => setCrm(await crmLookupAction(n)));
    startWeb(async () => setWeb(await webLookupAction(n, fresh)));
  };

  useEffect(() => {
    if (initial) check(initial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const lead = crm?.lead ?? null;

  return (
    <div className="space-y-5">
      <form
        className="flex max-w-xl gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          check(number);
        }}
      >
        <div className="relative flex-1">
          <Phone className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            autoFocus
            type="tel"
            inputMode="tel"
            value={number}
            onChange={(e) => setNumber(e.target.value)}
            placeholder="087 123 4567"
            className="h-11 pl-9 text-base"
            aria-label="Phone number"
          />
        </div>
        <Button className="h-11" disabled={!number.trim() || webPending}>
          <Search /> Check
        </Button>
      </form>

      {checked && crm === null && <p className="text-sm text-destructive">That doesn&apos;t look like a phone number.</p>}

      {checked && crm !== null && (
        <div className="grid gap-5 lg:grid-cols-2">
          {/* In your CRM */}
          <div className="rounded-2xl border bg-card shadow-card p-4">
            <div className="mb-3 text-sm font-semibold">In your CRM</div>
            {crmPending || crm === undefined ? (
              <Loader2 className="size-4 animate-spin text-muted-foreground" />
            ) : lead ? (
              <div className="space-y-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Link href={`/leads/${lead.id}`} className="text-lg font-semibold hover:underline">{lead.name ?? lead.business ?? crm?.phone}</Link>
                    <StatusBadge status={lead.status} />
                    {crm?.score && <Badge variant="outline">Score {crm.score.score}</Badge>}
                  </div>
                  <div className="text-sm text-muted-foreground">{[lead.business, lead.trade, lead.county].filter(Boolean).join(" · ") || "No details yet"}</div>
                  {crm?.campaigns.length ? <div className="mt-1 text-xs text-muted-foreground">Campaigns: {crm.campaigns.join(", ")}</div> : null}
                </div>
                {crm?.messages.map((m) => (
                  <div key={m.id} className={`rounded-lg px-3 py-2 text-sm ${m.direction === "inbound" ? "bg-emerald-500/10" : "bg-muted text-muted-foreground"}`}>
                    <div className="mb-0.5 flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                      {m.direction === "inbound" ? "Them" : "You"} · <ChannelBadge channel={m.channel} short /> {m.direction === "inbound" && <TagBadge tag={m.ai_tag} />} · {formatDateTime(m.sent_at)}
                    </div>
                    <span className="line-clamp-3">{m.body}</span>
                  </div>
                ))}
                <Button size="sm" variant="outline" asChild><Link href={`/leads/${lead.id}`}>Open lead</Link></Button>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Not in your CRM yet. {crm?.phone}</p>
            )}
          </div>

          {/* Claude web check */}
          <div className="rounded-2xl border bg-card shadow-card p-4">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-semibold"><Globe className="size-4 text-brand-accent" /> Claude web check</div>
              {web && !web.error && (
                <Button size="icon-sm" variant="ghost" aria-label="Search again" title="Search again (ignores the 24h cache)" disabled={webPending} onClick={() => check(checked, true)}>
                  <RefreshCw />
                </Button>
              )}
            </div>
            {webPending || (!web && aiOn) ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" /> Searching business listings, websites and directories… (usually 10-30s)
              </div>
            ) : web?.error ? (
              <p className="text-sm text-muted-foreground">{web.error}</p>
            ) : web ? (
              <div className="space-y-3">
                {web.found ? (
                  <dl className="grid grid-cols-[6rem_1fr] gap-x-3 gap-y-1.5 text-sm">
                    {web.business && (<><dt className="text-muted-foreground">Company</dt><dd className="font-semibold">{web.business}</dd></>)}
                    {web.name && (<><dt className="text-muted-foreground">Name</dt><dd>{web.name}</dd></>)}
                    {web.trade && (<><dt className="text-muted-foreground">Works as</dt><dd>{web.trade}</dd></>)}
                    {web.location && (<><dt className="text-muted-foreground">Area</dt><dd>{web.location}</dd></>)}
                    {web.website && (<><dt className="text-muted-foreground">Website</dt><dd><a href={web.website.startsWith("http") ? web.website : `https://${web.website}`} target="_blank" rel="noreferrer" className="underline">{web.website}</a></dd></>)}
                  </dl>
                ) : (
                  <p className="text-sm font-medium">No business listing found for this number.</p>
                )}
                {web.summary && <p className="text-sm text-muted-foreground">{web.summary}</p>}
                <Badge variant="outline" className={CONFIDENCE[web.confidence]}>Confidence: {web.confidence}</Badge>
                {web.sources.length > 0 && (
                  <ul className="space-y-1 text-xs">
                    {web.sources.map((s) => (
                      <li key={s.url}>
                        <a href={s.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-muted-foreground underline hover:text-foreground">
                          <ExternalLink className="size-3" /> {s.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                )}
                {web.found && (
                  savedId ? (
                    <Button size="sm" variant="outline" asChild><Link href={`/leads/${savedId}`}>Saved - open lead</Link></Button>
                  ) : (
                    <Button
                      size="sm"
                      disabled={savePending}
                      onClick={() =>
                        startSave(async () => {
                          const r = await saveLookupAction(checked, web, `Number check: ${web.summary}${web.sources[0] ? ` (source: ${web.sources[0].url})` : ""}`);
                          setSavedId(r.id);
                        })
                      }
                    >
                      <UserPlus /> {lead ? "Add missing details to lead" : "Save as lead"}
                    </Button>
                  )
                )}
              </div>
            ) : null}
          </div>
        </div>
      )}

      <p className="max-w-xl text-xs text-muted-foreground">
        Claude only reports details a business has published with this number (listings, websites, business pages), with links so you can check.
        Private numbers with no business listing are left alone. Results are cached for 24 hours.
      </p>
    </div>
  );
}
