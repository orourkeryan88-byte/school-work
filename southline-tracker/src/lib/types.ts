// Domain types shared by the UI, the data store and the API routes.
// Field names mirror the Postgres columns in supabase/migrations (snake_case).

export const CHANNELS = ["email", "sms"] as const;
export type Channel = (typeof CHANNELS)[number];

export const DIRECTIONS = ["outbound", "inbound"] as const;
export type Direction = (typeof DIRECTIONS)[number];

// Pipeline order matters: it's used to stop a lead moving "backwards"
// automatically (e.g. a new send shouldn't drag Booked back to Contacted).
export const LEAD_STATUSES = [
  "new",
  "contacted",
  "replied",
  "interested",
  "booked",
  "won",
  "lost",
] as const;
export type LeadStatus = (typeof LEAD_STATUSES)[number];

export const REPLY_TAGS = [
  "interested",
  "not_interested",
  "question",
  "objection",
  "out_of_office",
  "unsubscribe",
] as const;
export type ReplyTag = (typeof REPLY_TAGS)[number];

export interface Lead {
  id: string;
  name: string | null;
  business: string | null;
  email: string | null;
  phone: string | null; // E.164, e.g. +353871234567
  trade: string | null; // plumber, electrician, ...
  county: string | null;
  status: LeadStatus;
  unsubscribed: boolean;
  booked_at: string | null;
  won_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Campaign {
  id: string;
  name: string;
  channel: Channel;
  source: string | null; // instantly, smartlead, ghl, sendmode, csv...
  created_at: string;
}

export interface Message {
  id: string;
  lead_id: string;
  campaign_id: string | null;
  channel: Channel;
  direction: Direction;
  body: string;
  subject: string | null;
  variant: string | null; // A/B variant or sequence step label
  sent_at: string; // when it was sent/received
  reply_to_id: string | null; // inbound only: the outbound message it answers
  ai_tag: ReplyTag | null; // inbound only
  ai_tag_source: "ai" | "rules" | "manual" | null;
  source: string | null;
  external_id: string | null; // id from the sending tool, used to dedupe
  created_at: string;
}

export type NoteKind = "note" | "status" | "system";

export interface Note {
  id: string;
  lead_id: string;
  kind: NoteKind; // "status" notes record pipeline changes for the timeline
  body: string;
  created_at: string;
}

export interface FollowUp {
  id: string;
  lead_id: string;
  due_date: string; // YYYY-MM-DD
  reason: string | null;
  done_at: string | null;
  created_at: string;
}

export interface ImportLog {
  id: string;
  channel: Channel;
  kind: "csv" | "webhook" | "sync";
  source: string | null;
  filename: string | null;
  rows_total: number;
  rows_imported: number;
  rows_skipped: number;
  errors: string[];
  created_at: string;
}

// A row in the responses inbox: an inbound reply joined to its lead and
// the message it was replying to.
export interface InboxRow {
  reply: Message;
  sent: Message | null;
  lead: Lead;
  campaign: Campaign | null;
}

export const STATUS_LABELS: Record<LeadStatus, string> = {
  new: "New",
  contacted: "Contacted",
  replied: "Replied",
  interested: "Interested",
  booked: "Booked",
  won: "Won",
  lost: "Lost",
};

export const TAG_LABELS: Record<ReplyTag, string> = {
  interested: "Interested",
  not_interested: "Not interested",
  question: "Question",
  objection: "Objection",
  out_of_office: "Out of office",
  unsubscribe: "Unsubscribe",
};

export const CHANNEL_LABELS: Record<Channel, string> = {
  email: "Cold email",
  sms: "SMS",
};
