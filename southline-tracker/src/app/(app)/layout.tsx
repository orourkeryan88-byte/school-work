import { LogOut } from "lucide-react";
import Link from "next/link";
import { CommandPalette } from "@/components/command-palette";
import { Logo, LogoMark } from "@/components/logo";
import { MobileNav, SideNav } from "@/components/nav";
import { ThemeToggle } from "@/components/theme";
import { Button } from "@/components/ui/button";
import { aiEnabled } from "@/lib/ai";
import { currentUserEmail } from "@/lib/auth";
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
      <aside className="sticky top-0 hidden h-dvh w-60 shrink-0 flex-col border-r p-3 md:flex">
        <Link href="/" className="mb-5 px-2 pt-2">
          <Logo />
        </Link>
        <SideNav />
        <div className="mt-auto space-y-1 px-3 text-xs text-muted-foreground">
          {email && <div className="truncate" title={email}>{email}</div>}
          <div>Data: {live ? "Supabase" : "Mock (demo)"}</div>
          <div>AI: {aiEnabled() ? "Claude" : "Rules (no API key)"}</div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-40 flex h-14 items-center gap-2 border-b bg-background/90 px-4 backdrop-blur">
          <MobileNav />
          <Link href="/" className="flex items-center gap-2 md:hidden">
            <LogoMark className="size-7" />
            <span className="font-semibold tracking-tight">Southline Agency</span>
          </Link>
          <div className="ml-auto flex items-center gap-1.5">
            <CommandPalette />
            <ThemeToggle />
            <form action={signOutAction}>
              <Button variant="ghost" size="icon-sm" aria-label="Sign out" title="Sign out">
                <LogOut />
              </Button>
            </form>
          </div>
        </header>
        {!live && (
          <div className="border-b bg-amber-500/10 px-4 py-2 text-xs text-amber-800 dark:text-amber-200">
            Demo mode: showing mock data. Add Supabase keys to <code>.env.local</code> to use your real data (see README).
          </div>
        )}
        <main className="mx-auto w-full max-w-7xl flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
