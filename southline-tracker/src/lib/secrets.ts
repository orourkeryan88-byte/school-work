// API keys set from the app's "API keys" page.
//
// - Stored encrypted (AES-256-GCM) in the app_secrets table. The encryption key
//   is derived from SECRETS_KEY, or AUTH_SECRET if that isn't set, so the
//   database alone is never enough to read them.
// - Keys set in the host's environment variables always win; the page shows
//   those as "Set on the host" and they can't be changed from the app.
// - Values are never sent back to the browser: the page only shows the last 4.
import crypto from "node:crypto";
import { getStore, isSupabaseConfigured } from "@/lib/store";

export const KEY_FIELDS = [
  { name: "SENDMODE_ACCESS_KEY", group: "SendMode (texting)", label: "Access key", secret: true, help: "SendMode portal → Settings → API Settings" },
  { name: "SENDMODE_SENDER_ID", group: "SendMode (texting)", label: "Sender ID", secret: false, help: "Who texts come from, e.g. Southline (up to 11 letters) or your number" },
  { name: "GHL_API_KEY", group: "GoHighLevel", label: "API key", secret: true, help: "GHL → Settings → Private Integrations → create a token" },
  { name: "GHL_LOCATION_ID", group: "GoHighLevel", label: "Location ID", secret: false, help: "GHL → Settings → Business Profile → Location ID" },
  { name: "ANTHROPIC_API_KEY", group: "Claude (AI drafts + brief)", label: "API key", secret: true, help: "console.anthropic.com → API Keys" },
  { name: "INSTANTLY_API_KEY", group: "Instantly (cold email)", label: "API key", secret: true, help: "Instantly → Settings → Integrations → API" },
  { name: "GITHUB_TOKEN", group: "GitHub (Request a change)", label: "Token", secret: true, help: "github.com → Settings → Developer settings → fine-grained token with Issues: read & write" },
  { name: "GITHUB_REPO", group: "GitHub (Request a change)", label: "Repository", secret: false, help: "owner/repo, e.g. orourkeryan88-byte/school-work" },
] as const;
export type KeyName = (typeof KEY_FIELDS)[number]["name"];
const NAMES = new Set<string>(KEY_FIELDS.map((f) => f.name));
export const isKeyName = (n: string): n is KeyName => NAMES.has(n);

/** 32-byte encryption key, or null if no server secret is set (only allowed on mock data). */
export function cipherKey(): Buffer | null {
  const base = process.env.SECRETS_KEY || process.env.AUTH_SECRET || (isSupabaseConfigured() ? "" : "local-mock-data-only");
  return base ? crypto.createHash("sha256").update(`southline-api-keys:${base}`).digest() : null;
}

export function encrypt(plain: string, key: Buffer) {
  const iv = crypto.randomBytes(12);
  const c = crypto.createCipheriv("aes-256-gcm", key, iv);
  const enc = Buffer.concat([c.update(plain, "utf8"), c.final()]);
  return Buffer.concat([iv, c.getAuthTag(), enc]).toString("base64");
}

/** Returns null if the value was encrypted with a different key or was tampered with. */
export function decrypt(b64: string, key: Buffer): string | null {
  try {
    const buf = Buffer.from(b64, "base64");
    const d = crypto.createDecipheriv("aes-256-gcm", key, buf.subarray(0, 12));
    d.setAuthTag(buf.subarray(12, 28));
    return Buffer.concat([d.update(buf.subarray(28)), d.final()]).toString("utf8");
  } catch {
    return null;
  }
}

// Decrypted values, re-read from the database at most every 30 seconds.
let cache: { at: number; values: Map<string, string> } | null = null;
async function stored(): Promise<Map<string, string>> {
  if (cache && Date.now() - cache.at < 30_000) return cache.values;
  const values = new Map<string, string>();
  const key = cipherKey();
  if (key) {
    try {
      for (const row of await getStore().all("app_secrets")) {
        const v = decrypt(row.value_enc, key);
        if (v) values.set(row.id, v);
      }
    } catch (e) {
      // Table missing (migration 0005 not run yet) - behave as if nothing is saved.
      console.warn("Couldn't read saved API keys:", (e as Error).message);
    }
  }
  cache = { at: Date.now(), values };
  return values;
}

/** The value to use: the host's env var if set, otherwise the one saved in the app. */
export async function secret(name: KeyName): Promise<string | undefined> {
  return process.env[name] || (await stored()).get(name) || undefined;
}

export interface KeyStatus {
  name: KeyName;
  group: string;
  label: string;
  help: string;
  secret: boolean;
  source: "host" | "app" | null; // where the value comes from, null = not set
  preview: string | null; // "•••• 4bfe" for secrets, the full value otherwise
  updatedAt: string | null;
}

const mask = (v: string, isSecret: boolean) => (isSecret ? `•••• ${v.slice(-4)}` : v);

/** Everything the API keys page shows. Never includes a full secret. */
export async function keyStatuses(): Promise<KeyStatus[]> {
  cache = null;
  const saved = await stored();
  const rows = await getStore().all("app_secrets").catch(() => []);
  return KEY_FIELDS.map((f) => {
    const host = process.env[f.name];
    const app = saved.get(f.name);
    const v = host || app;
    return {
      ...f,
      source: host ? "host" : app ? "app" : null,
      preview: v ? mask(v, f.secret) : null,
      updatedAt: host ? null : (rows.find((r) => r.id === f.name)?.updated_at ?? null),
    };
  });
}

/** Save (or with an empty value, remove) one key. */
export async function saveKey(name: string, value: string, by: string | null): Promise<{ ok: true } | { ok: false; error: string }> {
  if (!isKeyName(name)) return { ok: false, error: "Unknown key" };
  if (process.env[name]) return { ok: false, error: "This one is set in your host's settings, so change it there." };
  const v = value.trim();
  const store = getStore();
  const existing = await store.get("app_secrets", name);
  if (!v) {
    if (existing) await store.remove("app_secrets", name);
    cache = null;
    return { ok: true };
  }
  if (v.length > 500 || (/\s/.test(v) && KEY_FIELDS.find((f) => f.name === name)!.secret)) return { ok: false, error: "That doesn't look like a key - check there are no spaces." };
  const key = cipherKey();
  if (!key) return { ok: false, error: "Set AUTH_SECRET in your host's settings first - it's used to lock the saved keys." };
  const row = { id: name, value_enc: encrypt(v, key), updated_at: new Date().toISOString(), updated_by: by };
  if (existing) await store.update("app_secrets", name, row);
  else await store.insert("app_secrets", row);
  cache = null;
  return { ok: true };
}
