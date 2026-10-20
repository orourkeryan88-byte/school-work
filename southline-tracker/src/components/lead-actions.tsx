"use client";

import { CalendarPlus, CalendarCheck, Sparkles, StickyNote, ThumbsUp, Wand2 } from "lucide-react";
import { useState, useTransition } from "react";
import { addFollowUpAction, addNoteAction, reclassifyAction, retagAction, setStatusAction } from "@/app/actions";
import { DraftBox } from "@/components/draft-box";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { NativeSelect } from "@/components/ui/select";
import type { Channel, LeadStatus, ReplyTag } from "@/lib/types";
import { LEAD_STATUSES, REPLY_TAGS, STATUS_LABELS, TAG_LABELS } from "@/lib/types";
import { addDays, isoDay } from "@/lib/utils";

type Panel = null | "note" | "followup" | "draft";

/**
 * Quick actions for a lead (and optionally the reply being looked at):
 * mark interested, mark booked, add note, set follow-up date, AI draft, retag.
 */
export function LeadActions({
  leadId,
  status,
  channel,
  messageId,
  tag,
  compact,
  smsEnabled,
}: {
  leadId: string;
  status: LeadStatus;
  channel: Channel;
  messageId?: string;
  tag?: ReplyTag | null;
  compact?: boolean;
  smsEnabled?: boolean;
}) {
  const [panel, setPanel] = useState<Panel>(null);
  const [note, setNote] = useState("");
  const [due, setDue] = useState(addDays(isoDay(), 2));
  const [reason, setReason] = useState("");
  const [flash, setFlash] = useState<string | null>(null);
  const [pending, start] = useTransition();

  const run = (fn: () => Promise<unknown>, msg: string) =>
    start(async () => {
      await fn();
      setFlash(msg);
      setTimeout(() => setFlash(null), 1800);
    });
  const toggle = (p: Panel) => setPanel(panel === p ? null : p);
  const size = compact ? "icon-sm" : "sm";

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-1.5">
        <Button size={size} variant="outline" title="Mark interested" disabled={pending || status === "interested"} onClick={() => run(() => setStatusAction(leadId, "interested"), "Marked interested")}>
          <ThumbsUp /> {!compact && "Interested"}
        </Button>
        <Button size={size} variant="outline" title="Mark booked" disabled={pending || status === "booked"} onClick={() => run(() => setStatusAction(leadId, "booked"), "Marked booked")}>
          <CalendarCheck /> {!compact && "Booked"}
        </Button>
        <Button size={size} variant={panel === "note" ? "secondary" : "outline"} title="Add note" onClick={() => toggle("note")}>
          <StickyNote /> {!compact && "Note"}
        </Button>
        <Button size={size} variant={panel === "followup" ? "secondary" : "outline"} title="Set follow-up date" onClick={() => toggle("followup")}>
          <CalendarPlus /> {!compact && "Follow-up"}
        </Button>
        <Button size={size} variant={panel === "draft" ? "secondary" : "outline"} title="Draft a reply with AI" onClick={() => toggle("draft")}>
          <Sparkles /> {!compact && "Draft reply"}
        </Button>
        {flash && <span className="text-xs text-emerald-600 dark:text-emerald-400">{flash}</span>}
      </div>

      {!compact && (
        <div className="flex flex-wrap items-center gap-2">
          <NativeSelect aria-label="Lead status" value={status} disabled={pending} onChange={(e) => run(() => setStatusAction(leadId, e.target.value as LeadStatus), "Status updated")}>
            {LEAD_STATUSES.map((s) => (
              <option key={s} value={s}>Status: {STATUS_LABELS[s]}</option>
            ))}
          </NativeSelect>
          {messageId && (
            <>
              <NativeSelect aria-label="Reply tag" value={tag ?? ""} disabled={pending} onChange={(e) => run(() => retagAction(messageId, e.target.value as ReplyTag), "Retagged")}>
                <option value="" disabled>Tag…</option>
                {REPLY_TAGS.map((t) => (
                  <option key={t} value={t}>Tag: {TAG_LABELS[t]}</option>
                ))}
              </NativeSelect>
              <Button size="sm" variant="ghost" title="Re-run AI tagging" disabled={pending} onClick={() => run(() => reclassifyAction(messageId), "Re-tagged")}>
                <Wand2 /> Re-tag
              </Button>
            </>
          )}
        </div>
      )}

      {panel === "note" && (
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            run(() => addNoteAction(leadId, note), "Note added");
            setNote("");
            setPanel(null);
          }}
        >
          <Input autoFocus value={note} onChange={(e) => setNote(e.target.value)} placeholder="e.g. Rang him, call back Friday" />
          <Button size="sm" disabled={!note.trim()}>Save</Button>
        </form>
      )}

      {panel === "followup" && (
        <form
          className="flex flex-wrap gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            run(() => addFollowUpAction(leadId, due, reason), `Follow-up set for ${due}`);
            setReason("");
            setPanel(null);
          }}
        >
          <Input type="date" value={due} onChange={(e) => setDue(e.target.value)} className="w-40" required />
          <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Reason (optional)" className="min-w-40 flex-1" />
          <Button size="sm">Set</Button>
        </form>
      )}

      {panel === "draft" && <DraftBox leadId={leadId} channel={channel} autoGenerate smsEnabled={smsEnabled} />}
    </div>
  );
}
