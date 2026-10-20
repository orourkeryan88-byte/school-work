import { isSupabaseConfigured } from "@/lib/store";

/**
 * Webhooks/sync are called by other tools, not a logged-in browser, so they
 * use a shared secret instead. Accepted as:
 *   - header  x-ingest-secret: <secret>
 *   - header  Authorization: Bearer <secret>
 *   - query   ?secret=<secret>   (for tools that only let you set a URL)
 * With no INGEST_SECRET set, webhooks are open in demo mode only.
 */
export function checkIngestSecret(req: Request): { ok: true } | { ok: false; status: number; error: string } {
  const secret = process.env.INGEST_SECRET;
  if (!secret) {
    return isSupabaseConfigured() ? { ok: false, status: 500, error: "INGEST_SECRET is not set on the server" } : { ok: true };
  }
  const url = new URL(req.url);
  const given =
    req.headers.get("x-ingest-secret") ??
    req.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ??
    url.searchParams.get("secret");
  return given === secret ? { ok: true } : { ok: false, status: 401, error: "bad or missing secret" };
}
