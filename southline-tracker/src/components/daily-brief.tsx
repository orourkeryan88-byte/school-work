"use client";

import { RefreshCw, Sparkles } from "lucide-react";
import { useEffect, useState, useTransition } from "react";
import { briefAction } from "@/app/actions";
import { Button } from "@/components/ui/button";

/** Claude's "what to do today" brief at the top of Today. */
export function DailyBrief() {
  const [brief, setBrief] = useState<{ text: string; source: string } | null>(null);
  const [pending, start] = useTransition();
  const load = (force: boolean) => start(async () => setBrief(await briefAction(force)));
  useEffect(() => load(false), []);
  return (
    <div className="rounded-xl border bg-gradient-to-br from-brand/[0.06] to-transparent p-4">
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Sparkles className="size-4 text-brand-accent" /> Today&apos;s brief
          <span className="text-xs font-normal text-muted-foreground">{brief ? (brief.source === "ai" ? "by Claude" : "summary") : ""}</span>
        </div>
        <Button variant="ghost" size="icon-sm" aria-label="Refresh brief" disabled={pending} onClick={() => load(true)}>
          <RefreshCw className={pending ? "animate-spin" : ""} />
        </Button>
      </div>
      {brief ? (
        <div className="space-y-1 text-sm whitespace-pre-line">{brief.text}</div>
      ) : (
        <div className="space-y-2">
          <div className="h-3 w-3/4 animate-pulse rounded bg-muted" />
          <div className="h-3 w-2/3 animate-pulse rounded bg-muted" />
          <div className="h-3 w-1/2 animate-pulse rounded bg-muted" />
        </div>
      )}
    </div>
  );
}
