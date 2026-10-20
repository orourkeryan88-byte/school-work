"use client";

import { BarChart3, CalendarClock, Columns3, Inbox, Megaphone, Menu, Sparkles, Sun, Upload, Users, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";

export const NAV = [
  { href: "/", label: "Today", icon: Sun },
  { href: "/queue", label: "Reply queue", icon: Sparkles },
  { href: "/inbox", label: "Responses", icon: Inbox },
  { href: "/pipeline", label: "Pipeline", icon: Columns3 },
  { href: "/leads", label: "Leads", icon: Users },
  { href: "/follow-ups", label: "Follow-ups", icon: CalendarClock },
  { href: "/campaigns", label: "Campaigns", icon: Megaphone },
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/import", label: "Import & connect", icon: Upload },
];

function Links({ onClick }: { onClick?: () => void }) {
  const path = usePathname();
  return (
    <nav className="flex flex-col gap-1">
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = href === "/" ? path === "/" : path.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onClick}
            className={cn(
              "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              active ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
            )}
          >
            <Icon className="size-4" />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

export function SideNav() {
  return <Links />;
}

/** Hamburger menu for phones. */
export function MobileNav() {
  const [open, setOpen] = useState(false);
  return (
    <div className="md:hidden">
      <button aria-label="Menu" className="rounded-md p-2 hover:bg-accent" onClick={() => setOpen(!open)}>
        {open ? <X className="size-5" /> : <Menu className="size-5" />}
      </button>
      {open && (
        <div className="absolute inset-x-0 top-14 z-50 border-b bg-background p-3 shadow-lg">
          <Links onClick={() => setOpen(false)} />
        </div>
      )}
    </div>
  );
}
