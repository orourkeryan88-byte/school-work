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
            "flex items-center gap-3 rounded-lg px-3 py-2.5 text-[15px] font-medium transition-colors",
            isActive(path, href) ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
          )}
        >
          <Icon className="size-[18px]" />
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
          <Link key={href} href={href} className={cn("flex flex-col items-center gap-0.5 py-2 text-[11px]", active ? "font-medium text-foreground" : "text-muted-foreground")}>
            <Icon className={cn("size-5", active && "text-brand-accent")} />
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
