// Loaded before the tests (see "test" script): in-memory store in a temp
// file, rule-based AI, no Supabase.
import os from "node:os";
import path from "node:path";

process.env.MOCK_DB_FILE = path.join(os.tmpdir(), `southline-test-${Date.now()}.json`);
delete process.env.ANTHROPIC_API_KEY;
delete process.env.SUPABASE_SERVICE_ROLE_KEY;
