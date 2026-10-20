import { cookies } from "next/headers";
import { SESSION_COOKIE, verifySessionToken } from "@/lib/session";
import { isSupabaseConfigured } from "@/lib/store";
import { createAuthClient } from "@/lib/supabase/server";

// Two login modes:
//  - "supabase": Supabase Auth users (when the Supabase env vars are set)
//  - "password": one built-in login from APP_LOGIN_EMAIL / APP_PASSWORD
export function authMode(): "supabase" | "password" {
  return isSupabaseConfigured() ? "supabase" : "password";
}

export async function currentUserEmail(): Promise<string | null> {
  if (authMode() === "supabase") {
    const supabase = await createAuthClient();
    const { data } = await supabase.auth.getUser();
    return data.user?.email ?? null;
  }
  return verifySessionToken((await cookies()).get(SESSION_COOKIE)?.value);
}
