import type { Campaign, FollowUp, ImportLog, Lead, Message, Note } from "@/lib/types";

/** Every table in the app, keyed by its Postgres name. */
export interface Tables {
  leads: Lead;
  campaigns: Campaign;
  messages: Message;
  notes: Note;
  follow_ups: FollowUp;
  import_logs: ImportLog;
}
export type TableName = keyof Tables;

/**
 * Minimal table-level storage interface. Two implementations:
 *  - memory.ts   (mock data, no setup needed)
 *  - supabase.ts (real Postgres)
 * All business logic lives in lib/repo.ts on top of this, so both behave the same.
 */
export interface Store {
  readonly kind: "memory" | "supabase";
  /** All rows, optionally filtered by exact-match columns. */
  all<T extends TableName>(table: T, where?: Partial<Tables[T]>): Promise<Tables[T][]>;
  get<T extends TableName>(table: T, id: string): Promise<Tables[T] | null>;
  insert<T extends TableName>(table: T, row: Tables[T]): Promise<Tables[T]>;
  update<T extends TableName>(table: T, id: string, patch: Partial<Tables[T]>): Promise<Tables[T]>;
  remove(table: TableName, id: string): Promise<void>;
}
