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
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0b1f3a] to-[#17406f] p-5 text-white shadow-card dark:from-[#102a4d] dark:to-[#0c1c34]">
      {/* the gold swoosh from the logo, faint across the bottom */}
      <svg aria-hidden viewBox="0 0 100 20" preserveAspectRatio="none" className="pointer-events-none absolute inset-x-0 bottom-0 h-10 w-full text-brand-accent opacity-30">
        <path d="M0 19C30 6 62 2 100 6C62 4 32 8 0 19Z" fill="currentColor" />
      </svg>
      <div className="relative mb-2.5 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Sparkles className="size-4 text-brand-accent" /> Today&apos;s brief
          <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-medium text-white/70">{brief ? (brief.source === "ai" ? "by Claude" : "summary") : "…"}</span>
        </div>
        <Button variant="ghost" size="icon-sm" aria-label="Refresh brief" disabled={pending} onClick={() => load(true)} className="text-white/80 hover:bg-white/10 hover:text-white dark:hover:bg-white/10">
          <RefreshCw className={pending ? "animate-spin" : ""} />
        </Button>
      </div>
      {brief ? (
        <div className="relative space-y-1 text-[15px] leading-relaxed whitespace-pre-line text-white/90">{brief.text}</div>
      ) : (
        <div className="relative space-y-2">
          <div className="h-3 w-3/4 animate-pulse rounded bg-white/15" />
          <div className="h-3 w-2/3 animate-pulse rounded bg-white/15" />
          <div className="h-3 w-1/2 animate-pulse rounded bg-white/15" />
        </div>
      )}
    </div>
  );
}
