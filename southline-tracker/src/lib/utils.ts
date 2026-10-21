import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind classes (shadcn/ui helper). */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function newId() {
  return crypto.randomUUID();
}

export function nowIso() {
  return new Date().toISOString();
}

/** YYYY-MM-DD in Irish time, so "today" matches the user's day. */
export function isoDay(d: Date | string = new Date()) {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Dublin" }).format(new Date(d));
}

export function addDays(day: string, n: number) {
  const d = new Date(`${day}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}

export function formatDateTime(iso: string) {
  return new Intl.DateTimeFormat("en-IE", {
    timeZone: "Europe/Dublin",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

export function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en-IE", {
    timeZone: "Europe/Dublin",
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(iso.length === 10 ? `${iso}T12:00:00Z` : iso));
}

export function pct(n: number, d: number) {
  return d === 0 ? 0 : Math.round((n / d) * 1000) / 10;
}

/**
 * Normalise a phone number to E.164. Irish numbers are the default:
 * "087 123 4567" -> "+353871234567", "00353..." -> "+353...".
 */
export function normalizePhone(raw: string | null | undefined): string | null {
  if (!raw) return null;
  let s = String(raw).trim().replace(/[^\d+]/g, "");
  if (!s) return null;
  if (s.startsWith("00")) s = "+" + s.slice(2);
  if (s.startsWith("+")) return s.replace(/^\+3530/, "+353");
  if (s.startsWith("353")) return "+" + s.replace(/^3530/, "353");
  if (s.startsWith("0")) return "+353" + s.slice(1);
  return s.length >= 9 ? "+353" + s : s;
}

export function normalizeEmail(raw: string | null | undefined): string | null {
  const s = raw?.trim().toLowerCase();
  return s && s.includes("@") ? s : null;
}

/** Loose business-name key: "O'Brien Plumbing Ltd." -> "obrien plumbing". */
export function businessKey(raw: string | null | undefined): string | null {
  if (!raw) return null;
  const s = raw
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9 ]/g, "")
    .replace(/\b(ltd|limited|teo|llc|inc|co)\b/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return s || null;
}

/** Minutes Europe/Dublin is ahead of UTC at a given moment (0 in winter, 60 in summer). */
function dublinOffset(d: Date) {
  const local = new Date(d.toLocaleString("en-US", { timeZone: "Europe/Dublin" }));
  const utc = new Date(d.toLocaleString("en-US", { timeZone: "UTC" }));
  return (local.getTime() - utc.getTime()) / 60000;
}

/**
 * Parse dates from webhooks/CSVs into ISO. Handles ISO strings, unix
 * timestamps, and Irish-style "18/10/2026 14:22". Dates with no timezone
 * are taken as Irish time.
 */
export function parseDate(raw: string | null | undefined): string | null {
  if (!raw) return null;
  const s = String(raw).trim();
  if (/^\d{10}$/.test(s)) return new Date(Number(s) * 1000).toISOString();
  if (/^\d{13}$/.test(s)) return new Date(Number(s)).toISOString();

  let norm = s;
  const dmy = s.match(/^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})(?:[ T](\d{1,2}):(\d{2})(?::(\d{2}))?)?$/);
  if (dmy) {
    const [, d, m, y, hh = "12", mm = "00", ss = "00"] = dmy;
    norm = `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}T${hh.padStart(2, "0")}:${mm}:${ss}`;
  } else if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
    norm = `${s}T12:00:00`;
  } else {
    norm = s.replace(/^(\d{4}-\d{2}-\d{2}) /, "$1T");
  }

  const hasZone = /(Z|[+-]\d{2}:?\d{2})$/i.test(norm) || /GMT|UTC/i.test(norm);
  if (hasZone || !/^\d{4}-\d{2}-\d{2}T/.test(norm)) {
    const t = Date.parse(norm);
    return isNaN(t) ? null : new Date(t).toISOString();
  }
  const asUtc = Date.parse(`${norm}Z`);
  if (isNaN(asUtc)) return null;
  return new Date(asUtc - dublinOffset(new Date(asUtc)) * 60000).toISOString();
}

/** Two-letter initials for avatars, e.g. "Conor O'Connor" -> "CO", "Seán Ó Briain" -> "SÓ". Numbers-only -> "#". */
export function initials(name: string | null | undefined) {
  const letters = (name ?? "").split(/\s+/).map((w) => w.match(/\p{L}/u)?.[0]).filter(Boolean);
  return letters.slice(0, 2).join("").toUpperCase() || "#";
}
