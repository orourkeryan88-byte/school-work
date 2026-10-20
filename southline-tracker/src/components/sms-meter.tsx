"use client";

import { smsSegments, toGsmFriendly } from "@/lib/crm";

/** Live SMS length/cost meter, with a one-click fix when fadas push it into Unicode. */
export function SmsMeter({ text, onFix }: { text: string; onFix?: (fixed: string) => void }) {
  const s = smsSegments(text);
  if (!text) return null;
  const fixed = s.unicode ? toGsmFriendly(text) : text;
  const fixedSegs = s.unicode ? smsSegments(fixed).segments : s.segments;
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
      <span className={s.segments > 1 ? "font-medium text-amber-700 dark:text-amber-300" : ""}>
        {s.segments} SMS · {s.length} chars{s.segments === 1 ? ` of ${s.limit}` : ""}
      </span>
      {s.unicode && (
        <span>
          Contains fadas/special characters, so each SMS is only 70 chars.
          {onFix && fixedSegs < s.segments && (
            <button type="button" className="ml-1 underline" onClick={() => onFix(fixed)}>
              Remove them ({fixedSegs} SMS)
            </button>
          )}
        </span>
      )}
    </div>
  );
}
