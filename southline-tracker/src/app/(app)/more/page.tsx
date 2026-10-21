import type { Metadata } from "next";
import Link from "next/link";
import { MORE_NAV } from "@/lib/nav-items";
import { RequestChange } from "@/components/request-change";

export const metadata: Metadata = { title: "More" };

// Everything that isn't needed every day, in one place.
export default function MorePage() {
  return (
    <>
      <h1 className="mb-5 text-xl font-semibold tracking-tight sm:text-2xl">More</h1>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {MORE_NAV.map(({ href, label, icon: Icon, hint }) => (
          <Link key={href} href={href} className="flex items-start gap-3 rounded-2xl border bg-card shadow-card p-4 transition hover:-translate-y-0.5 hover:border-brand-accent/40">
            <span className="rounded-xl bg-brand-accent/15 p-2 text-brand-ink"><Icon className="size-5" /></span>
            <span>
              <span className="block font-medium">{label}</span>
              <span className="block text-sm text-muted-foreground">{hint}</span>
            </span>
          </Link>
        ))}
      </div>
      <div className="mt-6 max-w-xs">
        <RequestChange />
      </div>
    </>
  );
}
