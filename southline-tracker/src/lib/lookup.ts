// "Check number": who is behind a phone number?
//  1. Your CRM: is this number already a lead?
//  2. Claude + web search: public *business* listings for the number
//     (Google Business profiles, Golden Pages, company websites, Facebook pages).
// Claude only reports what a business has published. A number that looks like
// a private personal mobile with no business listing is reported as such.

import Anthropic from "@anthropic-ai/sdk";
import { aiEnabled } from "@/lib/ai";
import { normalizePhone } from "@/lib/utils";

const MODEL = process.env.ANTHROPIC_MODEL || "claude-opus-5-5";

export interface WebLookup {
  found: boolean;
  name: string | null; // person's name, only if a business listing shows it
  business: string | null;
  trade: string | null;
  location: string | null;
  website: string | null;
  summary: string; // 1-3 lines in plain English
  confidence: "high" | "medium" | "low" | "none";
  sources: { title: string; url: string }[]; // only URLs the search actually returned
  error?: string;
}

/** The ways a number is usually written on Irish websites, for searching. */
export function phoneVariants(raw: string): string[] {
  const e164 = normalizePhone(raw);
  if (!e164) return [];
  if (!e164.startsWith("+353")) return [e164];
  const rest = e164.slice(4); // 871234567
  const local = `0${rest}`; // 0871234567
  const pre = local.slice(0, 3); // 087 (mobiles) - landlines vary, this is still a common format
  const tail = local.slice(3);
  return [...new Set([`${pre} ${tail.slice(0, 3)} ${tail.slice(3)}`, local, `+353 ${rest.slice(0, 2)} ${rest.slice(2, 5)} ${rest.slice(5)}`, `(${pre}) ${tail}`, e164])];
}

const SYSTEM = `You identify Irish businesses from a phone number, for a B2B sales team that sells to tradesmen and local service businesses.
Search the web for the number in its different written formats. Useful places: Google business listings, goldenpages.ie, company websites, Facebook/Instagram business pages, Checkatrade-style directories, LinkedIn company pages.
Rules:
- Only report details a business has published publicly alongside this number. Never guess.
- If the number only appears linked to a private individual (no business), or not at all, say so: found=false, and do not dig for personal details.
- Prefer exact matches of the number. A similar number is not a match.
- confidence: "high" = the exact number on the business's own site or listing; "medium" = exact number in one directory; "low" = indirect or partial evidence; "none" = nothing found.
End your answer with the result as JSON inside <result></result> tags, exactly these keys:
{"found": boolean, "name": string|null, "business": string|null, "trade": string|null, "location": string|null, "website": string|null, "summary": string, "confidence": "high"|"medium"|"low"|"none", "source_urls": string[]}`;

// Results are cached for a day so checking the same number twice is free.
const cache = globalThis as unknown as { __lookups?: Map<string, { at: number; result: WebLookup }> };
const DAY = 864e5;

export async function webLookup(raw: string, opts: { fresh?: boolean; client?: Pick<Anthropic, "beta"> } = {}): Promise<WebLookup> {
  const e164 = normalizePhone(raw);
  const empty: WebLookup = { found: false, name: null, business: null, trade: null, location: null, website: null, summary: "", confidence: "none", sources: [] };
  if (!e164) return { ...empty, error: "That doesn't look like a phone number." };
  if (!aiEnabled()) return { ...empty, error: "Add ANTHROPIC_API_KEY so Claude can search the web for this number." };

  cache.__lookups ??= new Map();
  const hit = cache.__lookups.get(e164);
  if (hit && !opts.fresh && Date.now() - hit.at < DAY) return hit.result;

  const client = opts.client ?? new Anthropic();
  const tools = [
    {
      type: "web_search_20260209" as const,
      name: "web_search" as const,
      max_uses: 6,
      user_location: { type: "approximate" as const, country: "IE", timezone: "Europe/Dublin" },
    },
  ];
  const messages: Anthropic.Beta.BetaMessageParam[] = [
    { role: "user", content: `Who is behind this phone number? ${phoneVariants(e164).map((v) => `"${v}"`).join(" or ")}` },
  ];

  try {
    let res: Anthropic.Beta.BetaMessage | null = null;
    // Web search runs a server-side loop that can pause; resume it a few times.
    for (let i = 0; i < 4; i++) {
      res = await client.beta.messages.create({
        model: MODEL,
        max_tokens: 8000,
        betas: ["server-side-fallback-2026-07-01"],
        fallbacks: "default",
        output_config: { effort: "medium" },
        system: SYSTEM,
        tools,
        messages,
      });
      if (res.stop_reason !== "pause_turn") break;
      messages.push({ role: "assistant", content: res.content });
    }
    if (!res || res.stop_reason === "refusal") return { ...empty, error: "Claude couldn't check this number." };
    const result = parseLookup(res.content);
    cache.__lookups.set(e164, { at: Date.now(), result });
    return result;
  } catch (e) {
    console.error("webLookup failed:", e);
    return { ...empty, error: `Web check failed: ${(e as Error).message}` };
  }
}

/** Turn Claude's answer into a WebLookup. Sources are limited to URLs the search really returned. */
export function parseLookup(content: Anthropic.Beta.BetaContentBlock[]): WebLookup {
  // Every URL the search actually returned - sources must come from here.
  const seen = new Map<string, string>();
  for (const b of content) {
    if (b.type === "web_search_tool_result" && Array.isArray(b.content)) {
      for (const r of b.content) if (r.type === "web_search_result") seen.set(r.url, r.title);
    }
  }
  const text = content.map((b) => (b.type === "text" ? b.text : "")).join("");
  const json = text.match(/<result>([\s\S]*?)<\/result>/)?.[1] ?? text.match(/\{[\s\S]*\}\s*$/)?.[0];
  let parsed: Record<string, unknown> = {};
  try {
    parsed = json ? JSON.parse(json) : {};
  } catch {
    // fall through with an empty result
  }
  const str = (v: unknown) => (typeof v === "string" && v.trim() ? v.trim() : null);
  const conf = ["high", "medium", "low", "none"].includes(String(parsed.confidence)) ? (parsed.confidence as WebLookup["confidence"]) : "none";
  const urls = Array.isArray(parsed.source_urls) ? (parsed.source_urls as unknown[]).map(String) : [];
  const sources = urls.filter((u) => seen.has(u)).map((u) => ({ url: u, title: seen.get(u) || u }));
  const result: WebLookup = {
    found: parsed.found === true && conf !== "none",
    name: str(parsed.name),
    business: str(parsed.business),
    trade: str(parsed.trade),
    location: str(parsed.location),
    website: str(parsed.website),
    summary: str(parsed.summary) ?? (json ? "" : text.slice(0, 400)),
    confidence: sources.length ? conf : conf === "high" ? "medium" : conf, // no verifiable source = can't be "high"
    sources,
  };
  return result;
}
