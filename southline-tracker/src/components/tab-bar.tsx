"use client";

import { Columns3, Menu, Sparkles, Sun, Users } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const TABS = [
  { href: "/", label: "Today", icon: Sun },
  { href: "/queue", label: "Replies", icon: Sparkles },
  { href: "/leads", label: "Leads", icon: Users },
  { href: "/pipeline", label: "Pipeline", icon: Columns3 },
];

/** iPhone-style tab bar along the bottom on phones; "More" opens the full menu. */
export function TabBar() {
  const path = usePathname();
  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t bg-background/95 pb-[env(safe-area-inset-bottom,0px)] backdrop-blur md:hidden"
    >
      {TABS.map(({ href, label, icon: Icon }) => {
        const active = href === "/" ? path === "/" : path.startsWith(href);
        return (
          <Link key={href} href={href} className={cn("flex flex-col items-center gap-0.5 py-2 text-[11px]", active ? "font-medium text-foreground" : "text-muted-foreground")}>
            <Icon className={cn("size-5", active && "text-brand-accent")} />
            {label}
          </Link>
        );
      })}
      <button type="button" onClick={() => window.dispatchEvent(new Event("southline:menu"))} aria-label="More" className="flex flex-col items-center gap-0.5 py-2 text-[11px] text-muted-foreground">
        <Menu className="size-5" />
        More
      </button>
    </nav>
  );
}
