import type { Campaign, FollowUp, Lead, LeadStatus, Message, Note, ReplyTag } from "@/lib/types";
import type { TableName, Tables } from "./types";

// Deterministic fake data so the UI works before anything is connected.
// Dates are relative to "now" so the 7d / 30d filters always show something.

function rng(seed: number) {
  return () => {
    seed = (seed * 1664525 + 1013904223) % 4294967296;
    return seed / 4294967296;
  };
}

const FIRST = ["Seán", "Ciarán", "Pádraig", "Niamh", "Aoife", "Declan", "Conor", "Siobhán", "Liam", "Darragh", "Eoin", "Mairéad", "Tadhg", "Gráinne", "Brendan", "Fiona", "Kevin", "Orla", "Micheál", "Róisín"];
const LAST = ["Murphy", "Kelly", "O'Brien", "Walsh", "Byrne", "Ryan", "O'Connor", "Doyle", "McCarthy", "Gallagher", "Doherty", "Kennedy", "Lynch", "Quinn", "Moran", "Nolan"];
const TRADES = ["Plumber", "Electrician", "Roofer", "Builder", "Landscaper", "HVAC", "Painter", "Carpenter", "Locksmith", "Plasterer"];
const COUNTIES = ["Dublin", "Cork", "Galway", "Limerick", "Kildare", "Meath", "Wicklow", "Waterford", "Kerry", "Mayo", "Louth", "Wexford"];

const EMAIL_A = "Hi {first}, quick one - how many calls does {business} miss while you're on a job? We set up an AI receptionist that answers 24/7 and books the job in. Worth a 10 min chat?";
const EMAIL_B = "{first}, most {trade}s in {county} lose 3-5 jobs a week to missed calls. Our AI receptionist picks up every one and texts you the details. Open to seeing a demo?";
const SMS_A = "Hi {first}, Ryan from Southline here. Do you miss calls when you're up a ladder? Our AI receptionist answers + books jobs for you. Interested? Reply STOP to opt out";
const SMS_B = "Hi {first}, missed calls = missed jobs. We answer them for {business} 24/7 with AI. Free 7 day trial - want it? Reply STOP to opt out";
const FOLLOW = "Just bumping this up {first} - still happy to show you how it works, takes 10 mins.";

const REPLIES: { tag: ReplyTag; text: string; next?: LeadStatus }[] = [
  { tag: "interested", text: "Yeah go on, send me some info. What does it cost?", next: "interested" },
  { tag: "interested", text: "Sounds good actually. Can you ring me Thursday after 5?", next: "interested" },
  { tag: "interested", text: "Ya I miss loads of calls. Book me in for a demo", next: "booked" },
  { tag: "question", text: "Does it work with my existing mobile number?" },
  { tag: "question", text: "How does it know my prices?" },
  { tag: "objection", text: "Customers won't want to talk to a robot to be honest" },
  { tag: "objection", text: "Too expensive for a one man band I'd say" },
  { tag: "not_interested", text: "Not for me thanks", next: "lost" },
  { tag: "not_interested", text: "No thanks, the wife does the phones", next: "lost" },
  { tag: "out_of_office", text: "I'm away until Monday, will reply when back." },
  { tag: "unsubscribe", text: "STOP", next: "lost" },
];

export function buildMockData(): { [K in TableName]: Tables[K][] } {
  const r = rng(42);
  const pick = <T,>(a: T[]) => a[Math.floor(r() * a.length)];
  const now = Date.now();
  const daysAgo = (d: number, h = 10) => new Date(now - d * 864e5 + (h - 10) * 36e5).toISOString();
  let n = 0;
  const id = (p: string) => `${p}_${String(++n).padStart(4, "0")}`;

  const campaigns: Campaign[] = [
    { id: "cmp_email_dublin", name: "Dublin trades - Oct", channel: "email", source: "instantly", created_at: daysAgo(35) },
    { id: "cmp_email_munster", name: "Munster plumbers", channel: "email", source: "smartlead", created_at: daysAgo(28) },
    { id: "cmp_sms_trial", name: "SMS free trial push", channel: "sms", source: "sendmode", created_at: daysAgo(25) },
    { id: "cmp_sms_missed", name: "SMS missed calls", channel: "sms", source: "sendmode", created_at: daysAgo(12) },
  ];

  const leads: Lead[] = [];
  const messages: Message[] = [];
  const notes: Note[] = [];
  const follow_ups: FollowUp[] = [];

  for (let i = 0; i < 70; i++) {
    const first = pick(FIRST);
    const last = pick(LAST);
    const trade = pick(TRADES);
    const county = pick(COUNTIES);
    const business = `${last.replace("'", "")} ${trade === "HVAC" ? "Heating & Cooling" : trade + "s"}`;
    const created = 3 + Math.floor(r() * 30);
    // Some leads get both channels - the matcher joins them into one timeline.
    const useEmail = r() < 0.7;
    const useSms = !useEmail || r() < 0.35;
    const lead: Lead = {
      id: id("lead"),
      name: `${first} ${last}`,
      business,
      email: useEmail ? `${first.toLowerCase().normalize("NFD").replace(/[^a-z]/g, "")}@${business.toLowerCase().replace(/[^a-z]/g, "")}.ie` : null,
      phone: `+3538${5 + Math.floor(r() * 5)}${String(Math.floor(r() * 1e7)).padStart(7, "0")}`,
      trade,
      county,
      status: "contacted",
      unsubscribed: false,
      booked_at: null,
      won_at: null,
      created_at: daysAgo(created + 1),
      updated_at: daysAgo(created),
    };
    leads.push(lead);
    const fill = (t: string) =>
      t.replace("{first}", first).replace("{business}", business).replace("{trade}", trade.toLowerCase()).replace("{county}", county);

    const channels: ("email" | "sms")[] = [];
    if (useEmail) channels.push("email");
    if (useSms) channels.push("sms");

    for (const channel of channels) {
      const variant = r() < 0.5 ? "A" : "B";
      const campaign =
        channel === "email"
          ? r() < 0.6 ? "cmp_email_dublin" : "cmp_email_munster"
          : created > 12 ? "cmp_sms_trial" : "cmp_sms_missed";
      const body = fill(channel === "email" ? (variant === "A" ? EMAIL_A : EMAIL_B) : variant === "A" ? SMS_A : SMS_B);
      const sentDay = created - (channel === "sms" ? 1 : 0);
      const sent: Message = {
        id: id("msg"), lead_id: lead.id, campaign_id: campaign, channel, direction: "outbound", body,
        subject: channel === "email" ? "Missed calls" : null, variant, sent_at: daysAgo(sentDay, 9),
        reply_to_id: null, ai_tag: null, ai_tag_source: null, source: channel === "email" ? "instantly" : "sendmode",
        external_id: null, created_at: daysAgo(sentDay, 9),
      };
      messages.push(sent);
      let last = sent;

      // Variant B and SMS reply a bit more often, so the comparisons show a difference.
      const replyChance = (channel === "sms" ? 0.42 : 0.3) + (variant === "B" ? 0.1 : 0);
      if (r() < replyChance) {
        const rep = pick(REPLIES);
        const replyDay = Math.max(0, sentDay - Math.floor(r() * 3));
        const reply: Message = {
          id: id("msg"), lead_id: lead.id, campaign_id: campaign, channel, direction: "inbound", body: rep.text,
          subject: null, variant, sent_at: daysAgo(replyDay, 11 + Math.floor(r() * 8)), reply_to_id: sent.id,
          ai_tag: rep.tag, ai_tag_source: "rules", source: sent.source, external_id: null, created_at: daysAgo(replyDay, 12),
        };
        messages.push(reply);
        lead.status = rep.next ?? (lead.status === "interested" ? "interested" : "replied");
        if (rep.tag === "unsubscribe") lead.unsubscribed = true;
        if (lead.status === "booked") lead.booked_at = reply.sent_at;
        if (lead.status !== "replied") {
          notes.push({ id: id("note"), lead_id: lead.id, kind: "status", body: `Status → ${lead.status}`, created_at: reply.sent_at });
        }
      } else if (sentDay > 4 && r() < 0.6) {
        // Follow-up nudge with no reply yet.
        last = {
          ...sent, id: id("msg"), body: fill(FOLLOW), variant: "follow-up 1", sent_at: daysAgo(sentDay - 3, 9), created_at: daysAgo(sentDay - 3, 9),
        };
        messages.push(last);
      }
    }

    // A few booked calls turn into wins, plus some manual notes and follow-ups.
    if (lead.status === "booked" && r() < 0.5) {
      lead.status = "won";
      lead.won_at = daysAgo(Math.max(0, created - 3));
      notes.push({ id: id("note"), lead_id: lead.id, kind: "status", body: "Status → won", created_at: lead.won_at });
    }
    if (lead.status === "interested" || lead.status === "replied") {
      if (r() < 0.6) {
        follow_ups.push({
          id: id("fu"), lead_id: lead.id, due_date: new Date(now + Math.floor(r() * 5 - 2) * 864e5).toISOString().slice(0, 10),
          reason: lead.status === "interested" ? "Send pricing + book demo" : "Answer their question", done_at: null, created_at: daysAgo(1),
        });
      }
      if (r() < 0.3) {
        notes.push({ id: id("note"), lead_id: lead.id, kind: "note", body: "Spoke briefly on the phone - busy season, call back next week.", created_at: daysAgo(1, 15) });
      }
    }
  }

  return { leads, campaigns, messages, notes, follow_ups, import_logs: [] };
}
