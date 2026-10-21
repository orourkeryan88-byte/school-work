import { LogOut } from "lucide-react";
import Link from "next/link";
import { CommandPalette } from "@/components/command-palette";
import { Logo, LogoMark } from "@/components/logo";
import { SideNav, TabBar } from "@/components/nav";
import { ThemeToggle } from "@/components/theme";
import { Button } from "@/components/ui/button";
import { authMode, currentUserEmail } from "@/lib/auth";
import { isSupabaseConfigured } from "@/lib/store";
import { signOutAction } from "../actions";

// Everything behind the login: sidebar, header and page content.
export const dynamic = "force-dynamic";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const live = isSupabaseConfigured();
  const email = await currentUserEmail();
  return (
    <div className="flex min-h-dvh">
      {/* Sidebar (desktop) */}
      <aside className="sticky top-0 hidden h-dvh w-60 shrink-0 flex-col bg-sidebar p-3 text-sidebar-foreground md:flex">
        <Link href="/" className="mb-6 rounded-lg px-2 pt-2 outline-none focus-visible:ring-2 focus-visible:ring-brand-accent">
          <Logo onDark />
        </Link>
        <SideNav />
        {email && <div className="mt-auto truncate px-3 text-xs text-sidebar-muted" title={email}>{email}</div>}
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-40 flex h-14 items-center gap-2 border-b bg-background/85 px-4 backdrop-blur-md">
          <Link href="/" className="flex min-w-0 items-center gap-2 md:hidden">
            <LogoMark className="size-7" />
            <span className="truncate text-[15px] font-semibold tracking-tight whitespace-nowrap">Southline Agency</span>
          </Link>
          <div className="ml-auto flex shrink-0 items-center gap-0.5 sm:gap-1.5">
            <CommandPalette />
            <ThemeToggle />
            {authMode() !== "off" && (
              <form action={signOutAction}>
                <Button variant="ghost" size="icon-sm" aria-label="Sign out" title="Sign out">
                  <LogOut />
                </Button>
              </form>
            )}
          </div>
        </header>
        {!live && <div className="border-b bg-amber-500/10 px-4 py-1.5 text-xs text-amber-800 dark:text-amber-200">Sample data - connect your database to use real leads.</div>}
        <main className="mx-auto w-full max-w-7xl flex-1 p-4 pb-24 sm:p-6 sm:pb-24 md:pb-6">{children}</main>
        <TabBar />
      </div>
    </div>
  );
}
