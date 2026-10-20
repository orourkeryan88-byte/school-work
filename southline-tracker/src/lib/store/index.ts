import { memoryStore } from "./memory";
import { supabaseStore } from "./supabase";
import type { Store } from "./types";

/** True when Supabase env vars are set; otherwise the app runs on mock data. */
export function isSupabaseConfigured() {
  return Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL &&
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY &&
      process.env.SUPABASE_SERVICE_ROLE_KEY,
  );
}

export function getStore(): Store {
  return isSupabaseConfigured() ? supabaseStore : memoryStore;
}

export type { Store, Tables, TableName } from "./types";
