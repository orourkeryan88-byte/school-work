"use client";

import { Bug, Check, Copy, ExternalLink, Lightbulb, Wand2, X } from "lucide-react";
import { usePathname } from "next/navigation";
import { useState, useTransition } from "react";
import { requestChangeAction } from "@/app/actions";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type Result = Awaited<ReturnType<typeof requestChangeAction>>;

/** "Request a change": describe a feature or bug; it goes to Claude as a GitHub issue. */
export function RequestChange({ variant = "sidebar" }: { variant?: "sidebar" | "icon" }) {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  const [kind, setKind] = useState<"feature" | "bug">("feature");
  const [text, setText] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [copied, setCopied] = useState(false);
  const [pending, start] = useTransition();

  const close = () => {
    setOpen(false);
    setResult(null);
    setText("");
  };

  return (
    <>
      {variant === "sidebar" ? (
        <button onClick={() => setOpen(true)} className="flex w-full items-center gap-2.5 rounded-md border border-dashed px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground">
          <Wand2 className="size-4 text-brand-accent" /> Request a change
        </button>
      ) : (
        <Button variant="ghost" size="icon-sm" aria-label="Request a change" title="Request a change" onClick={() => setOpen(true)}>
          <Wand2 />
        </Button>
      )}

      {open && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-0 sm:items-center sm:p-4" onClick={close}>
          <div className="w-full max-w-lg rounded-t-2xl border bg-popover p-5 shadow-2xl sm:rounded-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="mb-3 flex items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Request a change</h2>
                <p className="text-sm text-muted-foreground">Tell Claude what to build or fix. It writes the code and opens a pull request for you to approve.</p>
              </div>
              <Button variant="ghost" size="icon-sm" aria-label="Close" onClick={close}><X /></Button>
            </div>

            {result?.ok ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 p-3 text-sm"><Check className="size-4 text-emerald-600" /> Sent to Claude as issue #{result.number}.</div>
                <p className="text-sm text-muted-foreground">Claude will reply on the issue and open a pull request, usually within a few minutes. Merge it and the app updates on the next deploy.</p>
                <div className="flex gap-2">
                  <Button size="sm" asChild><a href={result.url} target="_blank" rel="noreferrer"><ExternalLink /> Watch progress</a></Button>
                  <Button size="sm" variant="outline" onClick={close}>Done</Button>
                </div>
              </div>
            ) : result && !result.ok && "saved" in result ? (
              <div className="space-y-3">
                <div className="rounded-lg bg-amber-500/10 p-3 text-sm">Saved, but not sent: {result.error}.</div>
                <p className="text-sm text-muted-foreground">Until GitHub is connected, copy this and paste it to Claude Code (claude.ai/code) with this repo:</p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={async () => {
                    await navigator.clipboard.writeText(result.issueText ?? "");
                    setCopied(true);
                  }}
                >
                  {copied ? <Check /> : <Copy />} {copied ? "Copied" : "Copy request"}
                </Button>
              </div>
            ) : (
              <form
                className="space-y-3"
                onSubmit={(e) => {
                  e.preventDefault();
                  start(async () => setResult(await requestChangeAction(kind, text, path)));
                }}
              >
                <div className="inline-flex rounded-lg border p-0.5 text-sm">
                  {([["feature", "New feature", Lightbulb], ["bug", "Something's broken", Bug]] as const).map(([k, label, Icon]) => (
                    <button key={k} type="button" onClick={() => setKind(k)} className={cn("flex items-center gap-1.5 rounded-md px-3 py-1.5", kind === k ? "bg-accent font-medium" : "text-muted-foreground")}>
                      <Icon className="size-4" /> {label}
                    </button>
                  ))}
                </div>
                <Textarea
                  autoFocus
                  rows={5}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={kind === "bug" ? "What happened, and what did you expect? e.g. 'The pipeline shows the wrong total when…'" : "What should the app do? e.g. 'Add a button on each lead to send the price list by SMS'"}
                />
                <p className="text-xs text-muted-foreground">Page: <code>{path}</code> is included automatically. Plain English is fine.</p>
                {result && !result.ok && !("saved" in result) && <p className="text-sm text-destructive">{result.error}</p>}
                <Button disabled={!text.trim() || pending} className="w-full">{pending ? "Sending…" : "Send to Claude"}</Button>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
