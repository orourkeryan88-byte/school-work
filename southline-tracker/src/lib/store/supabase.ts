import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import type { Store, TableName } from "./types";

// Server-only client using the service role key. It bypasses RLS, so it must
// never be imported into client components. Page access is protected by
// Supabase Auth in middleware.ts.
let client: SupabaseClient | null = null;

function sb() {
  if (!client) {
    client = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
      auth: { persistSession: false },
    });
  }
  return client;
}

const PAGE = 1000; // Supabase returns at most 1000 rows per request

/** Column to page through a table in a stable order. app_secrets has no created_at. */
export function orderColumn(table: TableName) {
  return table === "app_secrets" ? "id" : "created_at";
}

export const supabaseStore: Store = {
  kind: "supabase",
  async all(table, where) {
    const out = [];
    for (let from = 0; ; from += PAGE) {
      let q = sb().from(table).select("*").order(orderColumn(table)).range(from, from + PAGE - 1);
      if (where) q = q.match(where as Record<string, unknown>);
      const { data, error } = await q;
      if (error) throw new Error(`${table}: ${error.message}`);
      out.push(...data);
      if (data.length < PAGE) break;
    }
    return out;
  },
  async get(table, id) {
    const { data, error } = await sb().from(table).select("*").eq("id", id).maybeSingle();
    if (error) throw new Error(`${table}: ${error.message}`);
    return data;
  },
  async insert(table, row) {
    const { data, error } = await sb().from(table).insert(row).select().single();
    if (error) throw new Error(`${table}: ${error.message}`);
    return data;
  },
  async update(table, id, patch) {
    const { data, error } = await sb().from(table).update(patch as never).eq("id", id).select().single();
    if (error) throw new Error(`${table}: ${error.message}`);
    return data;
  },
  async remove(table, id) {
    const { error } = await sb().from(table).delete().eq("id", id);
    if (error) throw new Error(`${table}: ${error.message}`);
  },
};
