import { CalendarCheck, Inbox, MessageSquare } from "lucide-react";
import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { signInAction } from "@/app/actions";
import { Logo, LogoMark } from "@/components/logo";
import { ThemeToggle } from "@/components/theme";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authMode, currentUserEmail } from "@/lib/auth";

export const metadata: Metadata = { title: "Sign in" };
export const dynamic = "force-dynamic";

const ERRORS: Record<string, string> = {
  bad_login: "That email and password don't match.",
  not_allowed: "That account isn't allowed to use this app.",
};

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const { error } = await searchParams;
  const mode = authMode();
  if (mode === "off" || (await currentUserEmail())) redirect("/"); // no login needed

  return (
    <div className="grid min-h-dvh lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden flex-col justify-between overflow-hidden bg-brand p-10 text-white lg:flex">
        <div className="flex items-center gap-2.5">
          <LogoMark className="size-9" />
          <span className="text-lg font-semibold tracking-tight">Southline Agency</span>
        </div>
        <div className="max-w-md space-y-6">
          <h1 className="text-3xl leading-tight font-semibold tracking-tight">Every message sent. Every reply. What happened next.</h1>
          <ul className="space-y-3 text-sm text-white/80">
            <li className="flex items-center gap-3"><Inbox className="size-4 text-brand-accent" /> Cold email and SMS replies in one inbox</li>
            <li className="flex items-center gap-3"><MessageSquare className="size-4 text-brand-accent" /> AI tags every reply and drafts your answer</li>
            <li className="flex items-center gap-3"><CalendarCheck className="size-4 text-brand-accent" /> Know who to follow up today, and what to say</li>
          </ul>
        </div>
        <p className="text-xs text-white/50">AI receptionists for Irish tradesmen &amp; local services</p>
        {/* decorative wave */}
        <svg className="pointer-events-none absolute -right-24 bottom-24 w-[36rem] text-brand-accent opacity-15" viewBox="0 -40 400 220" aria-hidden>
          <path d="M0 80 C 60 0, 120 0, 180 80 S 300 160, 400 40" fill="none" stroke="currentColor" strokeWidth="10" strokeLinecap="round" />
        </svg>
      </div>

      {/* Form */}
      <div className="relative flex items-center justify-center p-6">
        <div className="absolute top-4 right-4"><ThemeToggle /></div>
        <div className="w-full max-w-sm space-y-8">
          <Logo subtitle="Outreach tracker" className="lg:hidden" />
          <div className="space-y-1.5">
            <h2 className="text-2xl font-semibold tracking-tight">Sign in</h2>
            <p className="text-sm text-muted-foreground">Welcome back. Sign in to see today&apos;s replies.</p>
          </div>

          <form action={signInAction} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">{mode === "password" ? "Email or username" : "Email"}</Label>
              <Input id="email" name="email" type={mode === "password" ? "text" : "email"} autoComplete="username" autoCapitalize="none" required className="h-10" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" name="password" type="password" autoComplete="current-password" required className="h-10" />
            </div>
            {error && <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{ERRORS[error] ?? error}</p>}
            <Button className="h-10 w-full">Sign in</Button>
          </form>

        </div>
      </div>
    </div>
  );
}
