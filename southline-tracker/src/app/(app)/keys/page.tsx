import { LockKeyhole, ShieldAlert } from "lucide-react";
import type { Metadata } from "next";
import { KeyRow } from "@/components/key-row";
import { PageHeader } from "@/components/page-header";
import { TestConnection } from "@/components/test-connection";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { authMode } from "@/lib/auth";
import { keyStatuses } from "@/lib/secrets";
import { isSupabaseConfigured } from "@/lib/store";

export const metadata: Metadata = { title: "API keys" };

// Paste API keys here instead of in the host's settings. Saved encrypted; only the last 4 are ever shown.
export default async function KeysPage() {
  const keys = await keyStatuses();
  const groups = [...new Set(keys.map((k) => k.group))];
  const loginOff = authMode() === "off";

  return (
    <>
      <PageHeader title="API keys" description="Connect SendMode, GoHighLevel and Claude by pasting your keys. They're saved encrypted and only the last 4 characters are ever shown." />

      {loginOff && (
        <div className="mb-4 flex gap-3 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-900 dark:text-amber-100">
          <ShieldAlert className="mt-0.5 size-4 shrink-0" />
          <p>The login is off, so anyone with the app&apos;s link can replace these keys (they still can&apos;t see them). Turn the login back on before you share the link.</p>
        </div>
      )}
      {!isSupabaseConfigured() && (
        <div className="mb-4 flex gap-3 rounded-2xl border bg-card p-4 text-sm text-muted-foreground shadow-card">
          <LockKeyhole className="mt-0.5 size-4 shrink-0" />
          <p>The app is on sample data, so keys saved here only last on this computer. Once your database is connected they&apos;re stored there for good.</p>
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-2 [&>*]:min-w-0">
        {groups.map((g) => (
          <Card key={g}>
            <CardHeader><CardTitle>{g}</CardTitle></CardHeader>
            <CardContent className="space-y-5">
              {keys.filter((k) => k.group === g).map((k) => <KeyRow key={k.name} k={k} />)}
              {g.startsWith("SendMode") && <TestConnection target="sendmode" />}
              {g.startsWith("GoHighLevel") && <TestConnection target="ghl" />}
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="mt-6 max-w-2xl text-xs text-muted-foreground">
        Your database keys (Supabase) and AUTH_SECRET can&apos;t live here, because the app needs them to open the database in the first place. Those go in your host&apos;s settings. Anything set there always takes priority over this page.
      </p>
    </>
  );
}
