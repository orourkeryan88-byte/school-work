import Anthropic from "@anthropic-ai/sdk";
import type { Lead, Message, ReplyTag } from "@/lib/types";
import { CHANNEL_LABELS, REPLY_TAGS, STATUS_LABELS, TAG_LABELS } from "@/lib/types";
import { formatDate } from "@/lib/utils";

// AI assist. Uses Claude when ANTHROPIC_API_KEY is set; otherwise falls back
// to simple keyword rules / templates so the app still works without a key.

const MODEL = process.env.ANTHROPIC_MODEL || "claude-opus-5-5";

export function aiEnabled() {
  return Boolean(process.env.ANTHROPIC_API_KEY);
}

let client: Anthropic | null = null;
function claude() {
  if (!client) client = new Anthropic();
  return client;
}

const TONE = `You write for Ryan at Southline Agency in Ireland. Southline sells AI receptionists
to tradesmen and local service businesses (plumbers, electricians, roofers...): it answers
every call 24/7, books jobs and texts the owner the details.
Tone: short, direct, friendly, plain Irish English. No hype, no exclamation marks, no emojis,
no "I hope this finds you well". Sign off "Ryan" on email only. SMS must be under 300 characters.`;

/** One Claude call that returns plain text. Returns null on refusal. */
async function ask(system: string, prompt: string, opts: { maxTokens?: number; format?: Record<string, unknown> } = {}) {
  const res = await claude().beta.messages.create({
    model: MODEL,
    max_tokens: opts.maxTokens ?? 2000,
    // Server-side fallback: if the model declines for policy reasons, the API
    // retries on Anthropic's recommended fallback model in the same call.
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    // These are short, simple tasks - low effort keeps them fast and cheap.
    output_config: {
      effort: "low",
      ...(opts.format ? { format: { type: "json_schema" as const, schema: opts.format } } : {}),
    },
    system,
    messages: [{ role: "user", content: prompt }],
  });
  if (res.stop_reason === "refusal") return null;
  return res.content
    .map((b) => (b.type === "text" ? b.text : ""))
    .join("")
    .trim();
}

// ---------- Classify replies ----------

const RULES: [ReplyTag, RegExp][] = [
  ["unsubscribe", /^\s*(stop|unsubscribe|remove me|opt ?out)\b|take me off|don'?t (text|email|contact) me/i],
  ["out_of_office", /out of (the )?office|away until|on (annual )?leave|auto.?reply|back on/i],
  ["not_interested", /not interested|no thanks|no thank you|not for (me|us)|we'?re (all )?(good|sorted)|not at the moment/i],
  ["objection", /too (expensive|dear)|robot|can'?t afford|already (have|use)|won'?t work|don'?t trust/i],
  ["interested", /\b(yes|yeah|ya|go on|sounds good|interested|book|demo|call me|ring me|send (me )?(some )?info|how much|cost|price)\b/i],
  ["question", /\?/],
];

/** Keyword fallback classifier. Order matters: STOP beats everything. */
export function classifyByRules(text: string): ReplyTag {
  for (const [tag, re] of RULES) if (re.test(text)) return tag;
  return "question";
}

export async function classifyReply(text: string): Promise<{ tag: ReplyTag; source: "ai" | "rules" }> {
  if (!aiEnabled()) return { tag: classifyByRules(text), source: "rules" };
  try {
    const out = await ask(
      `Classify a reply to a cold outreach message (email or SMS) from an AI receptionist agency to an Irish tradesman.
Labels:
- interested: wants info, price, a call, a demo, or says yes
- not_interested: declines politely or flatly
- question: asks something without showing clear interest or rejection
- objection: pushes back with a reason (price, robots, already have something)
- out_of_office: auto-reply / away message
- unsubscribe: asks to stop, be removed, or says STOP`,
      `Reply:\n"""${text}"""`,
      {
        maxTokens: 1000,
        format: {
          type: "object",
          properties: { tag: { type: "string", enum: [...REPLY_TAGS] } },
          required: ["tag"],
          additionalProperties: false,
        },
      },
    );
    const tag = out ? (JSON.parse(out).tag as ReplyTag) : null;
    if (tag && REPLY_TAGS.includes(tag)) return { tag, source: "ai" };
  } catch (e) {
    console.error("classifyReply failed, using rules:", e);
  }
  return { tag: classifyByRules(text), source: "rules" };
}

// ---------- Draft responses / follow-ups ----------

function transcript(messages: Message[]) {
  return messages
    .slice(-10)
    .map((m) => `[${CHANNEL_LABELS[m.channel]} ${m.direction === "outbound" ? "ME" : "THEM"} ${formatDate(m.sent_at)}] ${m.body}`)
    .join("\n");
}

function leadLine(lead: Lead) {
  return `${lead.name ?? "Unknown"}${lead.business ? `, ${lead.business}` : ""}${lead.trade ? ` (${lead.trade}` : ""}${lead.county ? `, ${lead.county})` : lead.trade ? ")" : ""}. Status: ${STATUS_LABELS[lead.status]}.`;
}

function firstName(lead: Lead) {
  return lead.name?.split(" ")[0] ?? "there";
}

/** Template drafts used when there's no API key. */
export function templateDraft(lead: Lead, last: Message | null): string {
  const first = firstName(lead);
  const tag = last?.direction === "inbound" ? last.ai_tag : null;
  switch (tag) {
    case "interested":
      return `Great stuff ${first}. Easiest thing is a quick 10 min call so I can show you it working on a real call. Would tomorrow or Thursday suit?`;
    case "question":
      return `Good question ${first} - short answer is yes, it's set up around your business. Easier to show than explain: have you 10 mins this week for a quick call?`;
    case "objection":
      return `Fair point ${first}. Most lads felt the same until they heard it - it sounds natural and only takes the details, you still do the talking. Free 7 day trial if you want to test it with no risk?`;
    case "out_of_office":
      return `No bother ${first}, I'll check back next week.`;
    case "not_interested":
    case "unsubscribe":
      return `No problem ${first}, I won't contact you again. Best of luck with the business.`;
    default:
      return `Hi ${first}, just following up on my last message - still happy to show you how the AI receptionist would work for ${lead.business ?? "you"}. 10 mins this week?`;
  }
}

export async function draftMessage(lead: Lead, messages: Message[], channel: "email" | "sms", goal?: string): Promise<{ text: string; source: "ai" | "template" }> {
  const last = messages[messages.length - 1] ?? null;
  if (!aiEnabled()) return { text: templateDraft(lead, last), source: "template" };
  try {
    const out = await ask(
      TONE,
      `Lead: ${leadLine(lead)}
Conversation so far (oldest first):
${transcript(messages) || "(nothing yet)"}

Write the next ${channel === "sms" ? "SMS" : "email (body only, no subject line)"} from me.
Goal: ${goal || "move them one step closer to a booked 10 minute demo call, or respond properly to what they said"}.
If they asked to stop or said no, write a one-line polite sign-off and nothing else.
Return only the message text.`,
    );
    if (out) return { text: out, source: "ai" };
  } catch (e) {
    console.error("draftMessage failed, using template:", e);
  }
  return { text: templateDraft(lead, last), source: "template" };
}

// ---------- Summarise a lead ----------

export async function summariseLead(lead: Lead, messages: Message[], notes: string[]): Promise<{ text: string; source: "ai" | "template" }> {
  const lastIn = [...messages].reverse().find((m) => m.direction === "inbound");
  const fallback = [
    leadLine(lead),
    `${messages.filter((m) => m.direction === "outbound").length} sent, ${messages.filter((m) => m.direction === "inbound").length} replies${lastIn?.ai_tag ? ` - last reply: ${TAG_LABELS[lastIn.ai_tag]}` : ""}.`,
    lastIn ? `They said: "${lastIn.body.slice(0, 120)}"` : "No reply yet.",
  ].join("\n");
  if (!aiEnabled()) return { text: fallback, source: "template" };
  try {
    const out = await ask(
      "You summarise sales leads for a busy solo founder. Exactly 3 short lines, no bullets or headings: who they are, where the conversation is, and the next best action.",
      `Lead: ${leadLine(lead)}\nNotes: ${notes.join(" | ") || "none"}\nConversation:\n${transcript(messages) || "(nothing yet)"}`,
    );
    if (out) return { text: out, source: "ai" };
  } catch (e) {
    console.error("summariseLead failed:", e);
  }
  return { text: fallback, source: "template" };
}
