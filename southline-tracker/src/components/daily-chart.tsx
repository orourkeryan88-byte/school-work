"use client";

import { useState } from "react";
import { formatDate } from "@/lib/utils";

type Row = { day: string; email: number; sms: number };

/**
 * Replies per day, email vs SMS, as paired bars. Hovering (or tapping) a day
 * shows its exact numbers in the readout line. Both series share one axis.
 */
export function DailyChart({ rows, metric }: { rows: Row[]; metric: string }) {
  const [hover, setHover] = useState<number | null>(null);
  const max = Math.max(1, ...rows.map((r) => Math.max(r.email, r.sms)));
  const total = rows.reduce((a, r) => ({ email: a.email + r.email, sms: a.sms + r.sms }), { email: 0, sms: 0 });
  const shown = hover !== null ? rows[hover] : null;

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex gap-4">
          <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-sm bg-email" /> Cold email</span>
          <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-sm bg-sms" /> SMS</span>
        </div>
        <div className="text-muted-foreground tabular-nums" aria-live="polite">
          {shown
            ? `${formatDate(shown.day)}: ${shown.email} email, ${shown.sms} SMS ${metric}`
            : `Total: ${total.email} email, ${total.sms} SMS ${metric}`}
        </div>
      </div>
      <div className="relative">
        {/* recessive gridlines at 0 / 50% / 100% */}
        <div className="pointer-events-none absolute inset-0 flex flex-col justify-between">
          {[max, Math.round(max / 2), 0].map((v, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="w-5 text-right text-[10px] text-muted-foreground tabular-nums">{v}</span>
              <div className="h-px flex-1 bg-border" />
            </div>
          ))}
        </div>
        <div className="ml-7 flex h-36 items-end gap-[2px]" role="img" aria-label={`${metric} per day by channel`}>
          {rows.map((r, i) => (
            <div
              key={r.day}
              className={`flex h-full flex-1 cursor-default items-end justify-center gap-[2px] rounded-sm ${hover === i ? "bg-accent/70" : ""}`}
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
              onClick={() => setHover(hover === i ? null : i)}
            >
              <div className="w-full max-w-2.5 rounded-t bg-email" style={{ height: `${(r.email / max) * 100}%` }} />
              <div className="w-full max-w-2.5 rounded-t bg-sms" style={{ height: `${(r.sms / max) * 100}%` }} />
            </div>
          ))}
        </div>
        <div className="mt-1 ml-7 flex justify-between text-[10px] text-muted-foreground">
          <span>{formatDate(rows[0].day)}</span>
          <span>{formatDate(rows[rows.length - 1].day)}</span>
        </div>
      </div>
    </div>
  );
}
