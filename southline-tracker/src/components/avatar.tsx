import { cn, initials } from "@/lib/utils";

// Soft tints from the brand palette. Picked from the name, so a person always keeps the same colour.
const TINTS = [
  "bg-sky-500/15 text-sky-700 dark:text-sky-300",
  "bg-teal-500/15 text-teal-700 dark:text-teal-300",
  "bg-indigo-500/15 text-indigo-700 dark:text-indigo-300",
  "bg-amber-500/15 text-amber-800 dark:text-amber-300",
  "bg-rose-500/15 text-rose-700 dark:text-rose-300",
  "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
];

export function Avatar({ name, className }: { name: string | null | undefined; className?: string }) {
  let h = 0;
  for (const c of name ?? "") h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return (
    <span aria-hidden className={cn("inline-flex size-9 shrink-0 items-center justify-center rounded-full text-xs font-semibold", TINTS[h % TINTS.length], className)}>
      {initials(name)}
    </span>
  );
}
