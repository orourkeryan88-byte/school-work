"use client";

import { PlugZap } from "lucide-react";
import { useState, useTransition } from "react";
import { testGhlAction, testSendmodeAction } from "@/app/actions";
import { Button } from "@/components/ui/button";

/** "Test connection" button for an integration. */
export function TestConnection({ target }: { target: "ghl" | "sendmode" }) {
  const [result, setResult] = useState<{ ok: boolean; detail: string } | null>(null);
  const [pending, start] = useTransition();
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Button size="sm" variant="outline" disabled={pending} onClick={() => start(async () => setResult(await (target === "ghl" ? testGhlAction() : testSendmodeAction())))}>
        <PlugZap /> {pending ? "Testing…" : "Test connection"}
      </Button>
      {result && <span className={`text-xs ${result.ok ? "text-emerald-600 dark:text-emerald-400" : "text-destructive"}`}>{result.detail}</span>}
    </div>
  );
}
