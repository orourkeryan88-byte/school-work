"use client";

import { Check, Copy, Flame, MessageSquare, RefreshCw, Send, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState, useTransition } from "react";
import { approveReplyAction, dismissReplyAction, draftReplyAction } from "@/app/actions";
import { ChannelBadge, StatusBadge, TagBadge } from "@/components/badges";
import { SmsMeter } from "@/components/sms-meter";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { formatMinutes, type Score } from "@/lib/crm";
import type { Lead, Message } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

const GOALS = [
  { label: "Book a call", goal: "answer briefly, then book a 10 minute call - offer two specific times" },
  { label: "Answer + price", goal: "answer their question directly and mention pricing starts from €99 a month, then suggest a quick call" },
  { label: "Offer free trial", goal: "offer the free 7-day trial with no commitment and ask if they want it set up this week" },
  { label: "Handle objection", goal: "acknowledge their concern honestly, reframe it in one line, and ask a soft question" },
];

export interface ReplyCardProps {
  lead: Lead;
  reply: Message;
  recent: Message[];
  score: Score;
  waitingMinutes: number;
  smsEnabled: boolean;
  windowReason: string | null; // non-null = quiet hours, SMS sending blocked
  autoDraft: boolean;
}

/** One person waiting on me: context, Claude's draft, and one-tap approve. */
export function ReplyCard({ lead, reply, recent, score, waitingMinutes, smsEnabled, windowReason, autoDraft }: ReplyCardProps) {
  const [text, setText] = useState(reply.ai_draft ?? "");
  const [source, setSource] = useState(reply.ai_draft_source ?? null);
  const [done, setDone] = useState<null | "sent" | "logged" | "dismissed">(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [pending, start] = useTransition();

  const draft = (regenerate: boolean, goal?: string) =>
    start(async () => {
      setError(null);
      try {
        const d = await draftReplyAction(reply.id, regenerate, goal);
        setText(d.text);
        setSource(d.source);
      } catch (e) {
        setError((e as Error).message);
      }
    });

  useEffect(() => {
    if (autoDraft && !reply.ai_draft) draft(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (done) {
    return (
      <div className="flex items-center gap-2 rounded-xl border border-dashed px-4 py-3 text-sm text-muted-foreground">
        <Check className="size-4 text-emerald-600" />
        {done === "sent" ? "Sent via SendMode" : done === "logged" ? "Logged as sent" : "Removed from queue"} - {lead.name ?? lead.phone}
      </div>
    );
  }

  const sms = reply.channel === "sms";
  const canSend = sms && smsEnabled && !windowReason;

  return (
    <div className="rounded-xl border bg-card p-4 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Link href={`/leads/${lead.id}`} className="font-medium hover:underline">{lead.name ?? lead.email ?? lead.phone}</Link>
            <StatusBadge status={lead.status} />
            <Badge variant="outline" title={score.reasons.join("\n")} className={score.hot ? "border-orange-500/40 text-orange-700 dark:text-orange-300" : ""}>
              {score.hot && <Flame />} Score {score.score}
            </Badge>
          </div>
          <div className="mt-0.5 text-xs text-muted-foreground">
            {[lead.business, lead.trade, lead.county].filter(Boolean).join(" · ")}
            {lead.phone && !lead.business && (
              <Link href={`/check?number=${encodeURIComponent(lead.phone)}`} className="ml-1 underline">Who is this?</Link>
            )}
          </div>
        </div>
        <div className={`text-xs ${waitingMinutes > 120 ? "font-medium text-amber-700 dark:text-amber-300" : "text-muted-foreground"}`}>
          Waiting {formatMinutes(waitingMinutes)}
        </div>
      </div>

      <div className="mt-3 grid gap-4 lg:grid-cols-[1fr_1.15fr]">
        {/* Conversation */}
        <div className="space-y-2">
          {recent.map((m) => (
            <div key={m.id} className={`rounded-lg px-3 py-2 text-sm ${m.direction === "inbound" ? "bg-emerald-500/10" : "bg-muted text-muted-foreground"}`}>
              <div className="mb-0.5 flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                {m.direction === "inbound" ? "Them" : "You"} · <ChannelBadge channel={m.channel} short /> {m.direction === "inbound" && <TagBadge tag={m.ai_tag} />} · {formatDateTime(m.sent_at)}
              </div>
              <span className="line-clamp-4">{m.body}</span>
            </div>
          ))}
          <p className="text-[11px] text-muted-foreground">Why this score: {score.reasons.join(" · ") || "-"}</p>
        </div>

        {/* Draft */}
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-1.5">
            {GOALS.map((g) => (
              <button key={g.label} type="button" disabled={pending} onClick={() => draft(true, g.goal)} className="rounded-full border px-2.5 py-1 text-xs text-muted-foreground hover:bg-accent disabled:opacity-50">
                {g.label}
              </button>
            ))}
          </div>
          <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={sms ? 4 : 6} placeholder={pending ? "Claude is drafting…" : "Draft your reply…"} disabled={pending && !text} />
          <div className="flex flex-wrap items-center justify-between gap-2">
            {sms ? <SmsMeter text={text} onFix={setText} /> : <span />}
            <span className="text-[11px] text-muted-foreground">{pending ? "Drafting…" : source === "ai" ? "Drafted by Claude" : source === "template" ? "Template" : ""}</span>
          </div>
          {error && <p className="text-xs text-destructive">{error}</p>}
          {sms && smsEnabled && windowReason && <p className="text-xs text-amber-700 dark:text-amber-300">{windowReason}. Copy it, or come back later.</p>}

          <div className="flex flex-wrap gap-1.5">
            {canSend ? (
              <Button
                size="sm"
                disabled={!text.trim() || pending}
                onClick={() =>
                  start(async () => {
                    const r = await approveReplyAction(reply.id, text);
                    if (r.ok) setDone("sent");
                    else setError(r.error ?? "Send failed");
                  })
                }
              >
                <MessageSquare /> Approve & send SMS
              </Button>
            ) : (
              <Button
                size="sm"
                disabled={!text.trim() || pending}
                onClick={() =>
                  start(async () => {
                    const r = await approveReplyAction(reply.id, text);
                    if (r.ok) setDone(r.sent ? "sent" : "logged");
                    else setError(r.error ?? "Failed");
                  })
                }
                title={sms ? "SendMode not connected or quiet hours - log it after sending from your phone" : "Send from your email tool, then log it here"}
              >
                <Send /> Log as sent
              </Button>
            )}
            <Button
              size="sm"
              variant="outline"
              disabled={!text}
              onClick={async () => {
                await navigator.clipboard.writeText(text);
                setCopied(true);
                setTimeout(() => setCopied(false), 1500);
              }}
            >
              {copied ? <Check /> : <Copy />} {copied ? "Copied" : "Copy"}
            </Button>
            <Button size="sm" variant="outline" disabled={pending} onClick={() => draft(true)}>
              <RefreshCw /> Redraft
            </Button>
            <Button size="sm" variant="ghost" disabled={pending} onClick={() => start(async () => { await dismissReplyAction(reply.id); setDone("dismissed"); })} title="Handled elsewhere (rang them, replied from phone)">
              <X /> Done elsewhere
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
