import { cookies } from "next/headers";
import { loginMode, SESSION_COOKIE, verifySessionToken } from "@/lib/session";
import { createAuthClient } from "@/lib/supabase/server";

// Login is off unless switched on - see loginMode() in lib/session.ts.
export function authMode() {
  return loginMode();
}

/** The signed-in user's email/username, or null (always null when login is off). */
export async function currentUserEmail(): Promise<string | null> {
  const mode = authMode();
  if (mode === "off") return null;
  if (mode === "supabase") {
    const supabase = await createAuthClient();
    const { data } = await supabase.auth.getUser();
    return data.user?.email ?? null;
  }
  return verifySessionToken((await cookies()).get(SESSION_COOKIE)?.value);
}
