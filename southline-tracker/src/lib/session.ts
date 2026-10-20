// Signed session cookie for the built-in login (used when Supabase isn't set up).
// Uses Web Crypto only, so it runs in middleware (edge) and on the server.

export const SESSION_COOKIE = "sl_session";
const MAX_AGE_DAYS = 30;
export const SESSION_MAX_AGE = MAX_AGE_DAYS * 24 * 60 * 60;

export interface LoginUser {
  login: string; // email or username, lower-cased
  password: string;
}

/**
 * Built-in logins, from env (never hard-code passwords in the repo):
 *   APP_USERS="you@example.com:password1,jamie:password2"   (several users)
 *   or APP_LOGIN_EMAIL + APP_PASSWORD                       (one user)
 * With neither set, a demo login is used and shown on the login page.
 */
export function builtInUsers(): { users: LoginUser[]; isDefault: boolean } {
  const list = (process.env.APP_USERS ?? "")
    .split(",")
    .map((entry) => {
      const i = entry.indexOf(":");
      return i > 0 ? { login: entry.slice(0, i).trim().toLowerCase(), password: entry.slice(i + 1).trim() } : null;
    })
    .filter((u): u is LoginUser => !!u && !!u.login && !!u.password);
  if (process.env.APP_PASSWORD) list.push({ login: (process.env.APP_LOGIN_EMAIL || "admin").toLowerCase(), password: process.env.APP_PASSWORD });
  if (list.length) return { users: list, isDefault: false };
  return { users: [{ login: "demo@southline.ie", password: "southline" }], isDefault: true };
}

/** The matching user for a login + password, or null. */
export function checkLogin(login: string, password: string): LoginUser | null {
  const wanted = login.trim().toLowerCase();
  return builtInUsers().users.find((u) => u.login === wanted && passwordMatches(password, u.password)) ?? null;
}

// Set AUTH_SECRET in production. Without it, the key is derived from the
// configured passwords (so changing a password also signs everyone out).
function secret() {
  return process.env.AUTH_SECRET || `southline:${builtInUsers().users.map((u) => u.password).join("|")}`;
}

const enc = new TextEncoder();
const b64url = (bytes: ArrayBuffer | Uint8Array) =>
  btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

async function sign(data: string) {
  const key = await crypto.subtle.importKey("raw", enc.encode(secret()), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return b64url(await crypto.subtle.sign("HMAC", key, enc.encode(data)));
}

function safeEqual(a: string, b: string) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function createSessionToken(email: string) {
  const payload = `${email}|${Date.now() + SESSION_MAX_AGE * 1000}`;
  return `${b64url(enc.encode(payload))}.${await sign(payload)}`;
}

/** Returns the signed-in email, or null if the token is missing/forged/expired. */
export async function verifySessionToken(token: string | undefined | null): Promise<string | null> {
  if (!token) return null;
  const [body, sig] = token.split(".");
  if (!body || !sig) return null;
  let payload: string;
  try {
    payload = atob(body.replace(/-/g, "+").replace(/_/g, "/"));
  } catch {
    return null;
  }
  if (!safeEqual(sig, await sign(payload))) return null;
  const [email, exp] = payload.split("|");
  if (!email || Number(exp) < Date.now()) return null;
  return email;
}

/** Compare passwords in constant time. */
export function passwordMatches(given: string, expected: string) {
  return safeEqual(given, expected);
}
