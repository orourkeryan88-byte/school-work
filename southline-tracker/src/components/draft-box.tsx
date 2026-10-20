"use client";

import { Check, Copy, Send, Sparkles } from "lucide-react";
import { useEffect, useState, useTransition } from "react";
import { draftAction, logSentAction } from "@/app/actions";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { Channel } from "@/lib/types";

/**
 * AI draft panel: generate a reply/follow-up in Ryan's tone, edit it,
 * copy it, then "Log as sent" once it's actually been sent.
 */
export function DraftBox({ leadId, channel, initial, goal, autoGenerate }: { leadId: string; channel: Channel; initial?: string; goal?: string; autoGenerate?: boolean }) {
  const [text, setText] = useState(initial ?? "");
  const [source, setSource] = useState<string | null>(initial ? "template" : null);
  const [ch, setCh] = useState<Channel>(channel);
  const [copied, setCopied] = useState(false);
  const [logged, setLogged] = useState(false);
  const [pending, start] = useTransition();

  const generate = () =>
    start(async () => {
      const res = await draftAction(leadId, ch, goal);
      setText(res.text);
      setSource(res.source);
      setLogged(false);
    });

  // Generate once on open if asked to and nothing's there yet.
  useEffect(() => {
    if (autoGenerate && !initial) generate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        <div className="inline-flex rounded-md border p-0.5 text-xs">
          {(["email", "sms"] as const).map((c) => (
            <button key={c} type="button" onClick={() => setCh(c)} className={`rounded px-2 py-1 ${ch === c ? "bg-accent font-medium" : "text-muted-foreground"}`}>
              {c === "email" ? "Email" : "SMS"}
            </button>
          ))}
        </div>
        <Button size="sm" variant="outline" type="button" onClick={generate} disabled={pending}>
          <Sparkles /> {pending ? "Drafting…" : text ? "Redraft" : "Draft with AI"}
        </Button>
        {source && <span className="text-xs text-muted-foreground">{source === "ai" ? "Drafted by Claude" : "Template"}</span>}
      </div>
      <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={ch === "sms" ? 3 : 5} placeholder="Draft appears here…" />
      {ch === "sms" && <div className="text-right text-xs text-muted-foreground">{text.length} chars</div>}
      <div className="flex flex-wrap gap-2">
        <Button
          size="sm"
          variant="secondary"
          type="button"
          disabled={!text}
          onClick={async () => {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
          }}
        >
          {copied ? <Check /> : <Copy />} {copied ? "Copied" : "Copy"}
        </Button>
        <Button
          size="sm"
          type="button"
          disabled={!text || pending || logged}
          onClick={() =>
            start(async () => {
              await logSentAction(leadId, ch, text);
              setLogged(true);
            })
          }
        >
          <Send /> {logged ? "Logged" : "Log as sent"}
        </Button>
      </div>
    </div>
  );
}
