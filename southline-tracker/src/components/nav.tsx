"use client";

import { LayoutGrid } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MAIN_NAV, MORE_NAV } from "@/lib/nav-items";
import { cn } from "@/lib/utils";

// The pipeline board is part of Leads, so it doesn't light up "More".
const MORE_PATHS = ["/more", ...MORE_NAV.map((n) => n.href).filter((h) => h !== "/pipeline")];

function isActive(path: string, href: string) {
  if (href === "/") return path === "/";
  if (href === "/more") return MORE_PATHS.some((p) => path.startsWith(p));
  // The pipeline board is part of Leads.
  if (href === "/leads") return path.startsWith("/leads") || path.startsWith("/pipeline");
  return path.startsWith(href);
}

/** Desktop sidebar: the four main items + More. */
export function SideNav() {
  const path = usePathname();
  const items = [...MAIN_NAV, { href: "/more", label: "More", icon: LayoutGrid }];
  return (
    <nav className="flex flex-col gap-1">
      {items.map(({ href, label, icon: Icon }) => (
        <Link
          key={href}
          href={href}
          className={cn(
            "relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-[15px] font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-brand-accent",
            isActive(path, href) ? "bg-sidebar-active text-white" : "text-sidebar-muted hover:bg-sidebar-active hover:text-white",
          )}
        >
          {/* gold marker on the current page */}
          {isActive(path, href) && <span aria-hidden className="absolute inset-y-2 left-0 w-1 rounded-full bg-brand-accent" />}
          <Icon className={cn("size-[18px]", isActive(path, href) && "text-brand-accent")} />
          {label}
        </Link>
      ))}
    </nav>
  );
}

/** Phone: tab bar along the bottom with the same five items. */
export function TabBar() {
  const path = usePathname();
  const items = [
    ...MAIN_NAV.map((n) => (n.href === "/check" ? { ...n, label: "Check" } : n)),
    { href: "/more", label: "More", icon: LayoutGrid },
  ];
  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t bg-background/95 pb-[env(safe-area-inset-bottom,0px)] backdrop-blur md:hidden"
    >
      {items.map(({ href, label, icon: Icon }) => {
        const active = isActive(path, href);
        return (
          <Link key={href} href={href} className={cn("flex flex-col items-center gap-0.5 py-1.5 text-[11px]", active ? "font-semibold text-foreground" : "text-muted-foreground")}>
            <span className={cn("rounded-full px-4 py-1 transition-colors", active && "bg-brand-accent/15 text-brand-ink")}>
              <Icon className="size-5" />
            </span>
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

/** Leads ⇄ Pipeline board switch, shown at the top of both pages. */
export function LeadsViewSwitch() {
  const path = usePathname();
  const board = path.startsWith("/pipeline");
  return (
    <div className="inline-flex rounded-lg border p-0.5 text-sm">
      <Link href="/leads" className={cn("rounded-md px-3 py-1.5", !board ? "bg-accent font-medium" : "text-muted-foreground")}>List</Link>
      <Link href="/pipeline" className={cn("rounded-md px-3 py-1.5", board ? "bg-accent font-medium" : "text-muted-foreground")}>Board</Link>
    </div>
  );
}
