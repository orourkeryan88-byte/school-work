"use client";

import { Upload } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/select";

type Result = { total: number; imported: number; duplicates: number; skipped: number; errors: string[] } | { error: string };

/** Upload a CSV of sends or replies for one channel. Posts to /api/import. */
export function CsvImportForm() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<Result | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setResult(null);
    try {
      const res = await fetch("/api/import", { method: "POST", body: new FormData(e.currentTarget) });
      setResult(await res.json());
      router.refresh();
    } catch (err) {
      setResult({ error: (err as Error).message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="channel">Channel</Label>
          <NativeSelect id="channel" name="channel" defaultValue="email" className="w-full">
            <option value="email">Cold email</option>
            <option value="sms">SMS (SendMode)</option>
          </NativeSelect>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="direction">Rows are</Label>
          <NativeSelect id="direction" name="direction" defaultValue="outbound" className="w-full">
            <option value="outbound">Messages I sent</option>
            <option value="inbound">Replies I received</option>
          </NativeSelect>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="source">Exported from</Label>
          <NativeSelect id="source" name="source" defaultValue="" className="w-full">
            <option value="">Other / CSV</option>
            <option value="instantly">Instantly</option>
            <option value="smartlead">Smartlead</option>
            <option value="ghl">GoHighLevel</option>
            <option value="sendmode">SendMode</option>
          </NativeSelect>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="campaign">Campaign (if not in the file)</Label>
          <Input id="campaign" name="campaign" placeholder="e.g. Dublin trades - Nov" />
        </div>
      </div>
      <Input type="file" name="file" accept=".csv,text/csv" required />
      <Button disabled={busy}><Upload /> {busy ? "Importing…" : "Import CSV"}</Button>

      {result && (
        <div className="rounded-md border p-3 text-sm">
          {"error" in result ? (
            <span className="text-destructive">{result.error}</span>
          ) : (
            <>
              <div>
                <b>{result.imported}</b> imported · {result.duplicates} duplicates · {result.skipped} skipped (of {result.total})
              </div>
              {result.errors.length > 0 && (
                <ul className="mt-2 max-h-40 list-disc overflow-auto pl-5 text-xs text-muted-foreground">
                  {result.errors.slice(0, 20).map((e) => <li key={e}>{e}</li>)}
                </ul>
              )}
            </>
          )}
        </div>
      )}
    </form>
  );
}
