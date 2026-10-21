"use client";

import { Check, Trash2 } from "lucide-react";
import { useState, useTransition } from "react";
import { saveKeyAction } from "@/app/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { KeyStatus } from "@/lib/secrets";
import { cn } from "@/lib/utils";

/** One API key: what's saved (last 4 only), and a box to paste a new one. */
export function KeyRow({ k }: { k: KeyStatus }) {
  const [value, setValue] = useState("");
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [pending, start] = useTransition();
  const id = `key-${k.name}`;
  const save = (v: string) =>
    start(async () => {
      const res = await saveKeyAction(k.name, v);
      setMsg(res.ok ? { ok: true, text: v ? "Saved" : "Removed" } : { ok: false, text: res.error });
      if (res.ok) setValue("");
    });

  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap items-center gap-2">
        <label htmlFor={id} className="text-sm font-medium">{k.label}</label>
        <span
          className={cn(
            "rounded-full px-2 py-0.5 text-[11px] font-medium",
            k.source === "host" ? "bg-sky-500/15 text-sky-700 dark:text-sky-300" : k.source === "app" ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300" : "bg-secondary text-muted-foreground",
          )}
        >
          {k.source === "host" ? "Set on the host" : k.source === "app" ? "Saved" : "Not set"}
        </span>
        {k.preview && <span className="font-mono text-xs text-muted-foreground">{k.preview}</span>}
      </div>
      {k.source === "host" ? (
        <p className="text-xs text-muted-foreground">Set in your host&apos;s settings, so it&apos;s changed there.</p>
      ) : (
        <form
          className="flex flex-wrap gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (value.trim()) save(value);
          }}
        >
          <Input
            id={id}
            type={k.secret ? "password" : "text"}
            autoComplete="off"
            spellCheck={false}
            placeholder={k.source === "app" ? "Paste a new one to replace it" : "Paste it here"}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className="min-w-48 flex-1 font-mono placeholder:font-sans"
          />
          <Button type="submit" size="sm" className="h-9" disabled={pending || !value.trim()}>
            <Check /> {pending ? "Saving…" : "Save"}
          </Button>
          {k.source === "app" && (
            <Button type="button" size="sm" variant="ghost" className="h-9 text-muted-foreground" disabled={pending} onClick={() => save("")} aria-label={`Remove ${k.label}`}>
              <Trash2 /> Remove
            </Button>
          )}
        </form>
      )}
      <p className="text-xs text-muted-foreground">{k.help}</p>
      {msg && <p role="status" className={cn("text-xs font-medium", msg.ok ? "text-emerald-600 dark:text-emerald-400" : "text-destructive")}>{msg.text}</p>}
    </div>
  );
}
