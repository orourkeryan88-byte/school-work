import { cn } from "@/lib/utils";

/** Southline Agency mark: a "south line" wave in a rounded navy tile. */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" aria-hidden className={cn("size-8 shrink-0", className)}>
      <rect width="32" height="32" rx="8" className="fill-brand" />
      <path d="M7 19.5c3-6 6-6 9 0s6 6 9 0" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" className="text-brand-accent" />
      <path d="M7 12.5h18" stroke="white" strokeOpacity=".9" strokeWidth="2.6" strokeLinecap="round" />
    </svg>
  );
}

/** Full logo: mark + "Southline Agency" wordmark. */
export function Logo({ subtitle = "Outreach tracker", className }: { subtitle?: string | null; className?: string }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <LogoMark />
      <div className="leading-tight">
        <div className="text-[15px] font-semibold tracking-tight">Southline Agency</div>
        {subtitle && <div className="text-xs text-muted-foreground">{subtitle}</div>}
      </div>
    </div>
  );
}
