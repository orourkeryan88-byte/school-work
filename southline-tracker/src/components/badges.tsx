import { Mail, MessageSquare } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Channel, LeadStatus, ReplyTag } from "@/lib/types";
import { CHANNEL_LABELS, STATUS_LABELS, TAG_LABELS } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ChannelBadge({ channel, short }: { channel: Channel; short?: boolean }) {
  const Icon = channel === "email" ? Mail : MessageSquare;
  return (
    <Badge variant="outline" className="gap-1.5">
      <Icon className={channel === "email" ? "text-email" : "text-sms"} />
      {short ? (channel === "email" ? "Email" : "SMS") : CHANNEL_LABELS[channel]}
    </Badge>
  );
}

// Colour is a hint only - the label always carries the meaning.
const STATUS_STYLE: Record<LeadStatus, string> = {
  new: "bg-secondary text-secondary-foreground",
  contacted: "bg-secondary text-secondary-foreground",
  replied: "bg-sky-500/15 text-sky-700 dark:text-sky-300",
  interested: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  booked: "bg-violet-500/15 text-violet-700 dark:text-violet-300",
  won: "bg-emerald-600 text-white",
  lost: "bg-muted text-muted-foreground line-through decoration-1",
};

export function StatusBadge({ status }: { status: LeadStatus }) {
  return <Badge className={cn("border-transparent", STATUS_STYLE[status])}>{STATUS_LABELS[status]}</Badge>;
}

const TAG_STYLE: Record<ReplyTag, string> = {
  interested: "border-emerald-500/40 text-emerald-700 dark:text-emerald-300",
  not_interested: "border-border text-muted-foreground",
  question: "border-sky-500/40 text-sky-700 dark:text-sky-300",
  objection: "border-amber-500/40 text-amber-700 dark:text-amber-300",
  out_of_office: "border-border text-muted-foreground",
  unsubscribe: "border-red-500/40 text-red-700 dark:text-red-300",
};

export function TagBadge({ tag }: { tag: ReplyTag | null }) {
  if (!tag) return <Badge variant="outline" className="text-muted-foreground">Untagged</Badge>;
  return <Badge variant="outline" className={TAG_STYLE[tag]}>{TAG_LABELS[tag]}</Badge>;
}
