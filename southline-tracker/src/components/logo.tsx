import { MARK } from "@/lib/brand-mark";
import { cn } from "@/lib/utils";

/** Southline Agency mark: the navy "SA" monogram with the gold swoosh, on a white tile. */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 100" aria-hidden className={cn("size-8 shrink-0 rounded-[22%] ring-1 ring-black/5", className)}>
      <rect width="100" height="100" rx="22" fill="#fff" />
      <path d={MARK.s} fill={MARK.navy} />
      <path d={MARK.a} fill={MARK.navy} />
      <path d={MARK.swoosh} fill={MARK.gold} />
    </svg>
  );
}

/** Full logo: mark + "Southline Agency" wordmark. onDark = on the navy sidebar. */
export function Logo({ subtitle = "Outreach tracker", className, onDark }: { subtitle?: string | null; className?: string; onDark?: boolean }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <LogoMark className="size-9" />
      <div className="leading-tight">
        <div className="text-[15px] font-semibold tracking-tight">Southline Agency</div>
        {subtitle && <div className={cn("text-xs", onDark ? "text-sidebar-muted" : "text-muted-foreground")}>{subtitle}</div>}
      </div>
    </div>
  );
}
