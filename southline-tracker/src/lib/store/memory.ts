import fs from "node:fs";
import path from "node:path";
import { buildMockData } from "./mock-data";
import type { Store, TableName, Tables } from "./types";

type Db = { [K in TableName]: Tables[K][] };

// Mock data is saved here between restarts in local dev, so CSV imports and
// edits stick around. Delete the file to reset to fresh mock data.
const FILE = process.env.MOCK_DB_FILE || path.join(process.cwd(), ".data", "mock-db.json");

function load(): Db {
  try {
    return JSON.parse(fs.readFileSync(FILE, "utf8")) as Db;
  } catch {
    return buildMockData();
  }
}

function save(db: Db) {
  try {
    fs.mkdirSync(path.dirname(FILE), { recursive: true });
    fs.writeFileSync(FILE, JSON.stringify(db));
  } catch {
    // Read-only filesystem (e.g. serverless) - keep it in memory only.
  }
}

// Keep one copy across hot reloads in dev.
const g = globalThis as unknown as { __mockDb?: Db };

function db(): Db {
  if (!g.__mockDb) g.__mockDb = load();
  return g.__mockDb;
}

function matches<T>(row: T, where?: Partial<T>) {
  if (!where) return true;
  return Object.entries(where).every(([k, v]) => (row as Record<string, unknown>)[k] === v);
}

export const memoryStore: Store = {
  kind: "memory",
  async all(table, where) {
    return db()[table].filter((r) => matches(r, where)).map((r) => ({ ...r }));
  },
  async get(table, id) {
    const row = db()[table].find((r) => r.id === id);
    return row ? { ...row } : null;
  },
  async insert(table, row) {
    (db()[table] as Tables[typeof table][]).push({ ...row });
    save(db());
    return row;
  },
  async update(table, id, patch) {
    const rows = db()[table] as Tables[typeof table][];
    const i = rows.findIndex((r) => r.id === id);
    if (i < 0) throw new Error(`${table} ${id} not found`);
    rows[i] = { ...rows[i], ...patch };
    save(db());
    return { ...rows[i] };
  },
  async remove(table, id) {
    const rows = db()[table] as { id: string }[];
    const i = rows.findIndex((r) => r.id === id);
    if (i >= 0) rows.splice(i, 1);
    save(db());
  },
};
