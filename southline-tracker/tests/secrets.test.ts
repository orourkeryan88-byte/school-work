// API keys page: encrypted storage, host env vars win, full keys never shown.
import assert from "node:assert/strict";
import crypto from "node:crypto";
import { test } from "node:test";
import { cipherKey, decrypt, encrypt, keyStatuses, saveKey, secret } from "@/lib/secrets";
import { getStore } from "@/lib/store";

test("encrypt/decrypt round trip; a different key can't read it", () => {
  const k = crypto.randomBytes(32);
  const enc = encrypt("live_abc-123", k);
  assert.notEqual(enc.includes("live_abc"), true);
  assert.equal(decrypt(enc, k), "live_abc-123");
  assert.equal(decrypt(enc, crypto.randomBytes(32)), null);
  assert.equal(decrypt("not base64 at all", k), null);
});

test("saved keys are stored encrypted, readable by the app, and only the last 4 are shown", async () => {
  assert.ok(cipherKey(), "mock data mode always has a key");
  const r = await saveKey("SENDMODE_ACCESS_KEY", "  live_test-key-9876  ", "me");
  assert.deepEqual(r, { ok: true });
  assert.equal(await secret("SENDMODE_ACCESS_KEY"), "live_test-key-9876");

  const row = await getStore().get("app_secrets", "SENDMODE_ACCESS_KEY");
  assert.ok(row && !row.value_enc.includes("live_test"), "not stored in plain text");

  const s = (await keyStatuses()).find((k) => k.name === "SENDMODE_ACCESS_KEY")!;
  assert.equal(s.source, "app");
  assert.equal(s.preview, "•••• 9876");
  assert.ok(!JSON.stringify(await keyStatuses()).includes("live_test-key"), "full key never in the page data");

  // non-secret settings (sender ID) are shown in full
  await saveKey("SENDMODE_SENDER_ID", "Southline", null);
  assert.equal((await keyStatuses()).find((k) => k.name === "SENDMODE_SENDER_ID")!.preview, "Southline");

  // empty value removes it
  assert.deepEqual(await saveKey("SENDMODE_ACCESS_KEY", "", null), { ok: true });
  assert.equal(await secret("SENDMODE_ACCESS_KEY"), undefined);
  await saveKey("SENDMODE_SENDER_ID", "", null);
});

test("the host's env var wins and can't be overwritten from the app", async () => {
  process.env.GHL_API_KEY = "pit-from-host-1111";
  try {
    const r = await saveKey("GHL_API_KEY", "pit-from-app-2222", null);
    assert.equal(r.ok, false);
    assert.equal(await secret("GHL_API_KEY"), "pit-from-host-1111");
    assert.equal((await keyStatuses()).find((k) => k.name === "GHL_API_KEY")!.source, "host");
  } finally {
    delete process.env.GHL_API_KEY;
  }
});

test("unknown names and keys with spaces are rejected", async () => {
  assert.equal((await saveKey("SUPABASE_SERVICE_ROLE_KEY", "x", null)).ok, false);
  assert.equal((await saveKey("ANTHROPIC_API_KEY", "sk ant with spaces", null)).ok, false);
});

test("Supabase paging order: every table sorts by created_at except app_secrets (which has no such column)", async () => {
  const { orderColumn } = await import("@/lib/store/supabase");
  assert.equal(orderColumn("app_secrets"), "id");
  for (const t of ["leads", "messages", "campaigns", "notes", "follow_ups", "import_logs", "change_requests"] as const) assert.equal(orderColumn(t), "created_at");
  // and the schema agrees: app_secrets is the only table created without created_at
  const fs = await import("node:fs");
  const sql = fs.readFileSync("supabase/migrations/0005_app_secrets.sql", "utf8");
  assert.ok(!sql.includes("created_at"));
});
