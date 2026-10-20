import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { LogOut } from "lucide-react";
import { MobileNav, SideNav } from "@/components/nav";
import { ThemeProvider, ThemeToggle } from "@/components/theme";
import { Button } from "@/components/ui/button";
import { aiEnabled } from "@/lib/ai";
import { isSupabaseConfigured } from "@/lib/store";
import { signOutAction } from "./actions";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Southline Outreach",
  description: "Every cold email and SMS sent, every reply, and what happened next.",
  // iPhone: run full-screen when opened from the home screen.
  appleWebApp: { capable: true, title: "Southline", statusBarStyle: "default" },
};
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const live = isSupabaseConfigured();
  return (
    <html lang="en-IE" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} font-sans`}>
        <ThemeProvider>
          <div className="flex min-h-dvh">
            {/* Sidebar (desktop) */}
            <aside className="sticky top-0 hidden h-dvh w-56 shrink-0 flex-col border-r p-3 md:flex">
              <div className="mb-4 px-3 pt-2">
                <div className="text-sm font-semibold">Southline</div>
                <div className="text-xs text-muted-foreground">Outreach tracker</div>
              </div>
              <SideNav />
              <div className="mt-auto space-y-1 px-3 text-xs text-muted-foreground">
                <div>Data: {live ? "Supabase" : "Mock (demo)"}</div>
                <div>AI: {aiEnabled() ? "Claude" : "Rules (no API key)"}</div>
              </div>
            </aside>

            <div className="flex min-w-0 flex-1 flex-col">
              <header className="sticky top-0 z-40 flex h-14 items-center gap-2 border-b bg-background/90 px-4 backdrop-blur">
                <MobileNav />
                <span className="font-semibold md:hidden">Southline</span>
                <div className="ml-auto flex items-center gap-1">
                  <ThemeToggle />
                  {live && (
                    <form action={signOutAction}>
                      <Button variant="ghost" size="icon-sm" aria-label="Sign out">
                        <LogOut />
                      </Button>
                    </form>
                  )}
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
        </ThemeProvider>
      </body>
    </html>
  );
}
