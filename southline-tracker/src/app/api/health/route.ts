import { NextResponse } from "next/server";
import { aiEnabled } from "@/lib/ai";
import { isSupabaseConfigured } from "@/lib/store";

/** GET /api/health - quick check that the app is up and which mode it's in. */
export async function GET() {
  return NextResponse.json({ ok: true, data: isSupabaseConfigured() ? "supabase" : "mock", ai: (await aiEnabled()) ? "claude" : "rules" });
}
