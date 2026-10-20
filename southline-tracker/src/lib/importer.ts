import { normalizeEvent } from "@/lib/ingest";
import { loadCtx, recordMessage } from "@/lib/repo";
import { getStore } from "@/lib/store";
import type { Channel, Direction, ImportLog } from "@/lib/types";
import { newId, nowIso } from "@/lib/utils";

export interface ImportOptions {
  channel: Channel;
  kind: ImportLog["kind"];
  direction?: Direction; // default when the row doesn't say
  source?: string | null;
  campaign?: string | null; // default campaign name when the row doesn't say
  filename?: string | null;
}

export interface ImportSummary {
  total: number;
  imported: number;
  duplicates: number;
  skipped: number;
  errors: string[];
  logId: string;
}

/**
 * Shared by webhooks, CSV import and API sync: normalise each raw row,
 * record it, and write one ImportLog entry with the result.
 */
export async function importRows(rows: Record<string, unknown>[], opts: ImportOptions): Promise<ImportSummary> {
  const ctx = await loadCtx();
  const errors: string[] = [];
  let imported = 0;
  let duplicates = 0;

  for (const [i, row] of rows.entries()) {
    const res = normalizeEvent(row, opts.channel, opts);
    if (!res.ok) {
      errors.push(`Row ${i + 1}: ${res.error}`);
      continue;
    }
    try {
      const r = await recordMessage(res.event, ctx);
      if (r.status === "created") imported++;
      else duplicates++;
    } catch (e) {
      errors.push(`Row ${i + 1}: ${(e as Error).message}`);
    }
  }

  const log = await getStore().insert("import_logs", {
    id: newId(),
    channel: opts.channel,
    kind: opts.kind,
    source: opts.source ?? null,
    filename: opts.filename ?? null,
    rows_total: rows.length,
    rows_imported: imported,
    rows_skipped: rows.length - imported,
    errors: errors.slice(0, 50), // keep the log small
    created_at: nowIso(),
  });

  return { total: rows.length, imported, duplicates, skipped: rows.length - imported - duplicates, errors, logId: log.id };
}
