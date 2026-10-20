// Built-in login: signed session cookies.
import assert from "node:assert/strict";
import { test } from "node:test";
import { createSessionToken, verifySessionToken } from "@/lib/session";

test("session tokens verify, and forged or expired ones don't", async () => {
  const t = await createSessionToken("ryan@southline.ie");
  assert.equal(await verifySessionToken(t), "ryan@southline.ie");

  const [body, sig] = t.split(".");
  const forgedBody = Buffer.from("attacker@x.ie|9999999999999").toString("base64url");
  assert.equal(await verifySessionToken(`${forgedBody}.${sig}`), null);
  assert.equal(await verifySessionToken(`${body}.x${sig.slice(1)}`), null);
  assert.equal(await verifySessionToken(undefined), null);
  assert.equal(await verifySessionToken("garbage"), null);

  const realNow = Date.now;
  Date.now = () => realNow() + 31 * 24 * 3600 * 1000; // past the 30-day expiry
  try {
    assert.equal(await verifySessionToken(t), null);
  } finally {
    Date.now = realNow;
  }
});

test("APP_USERS: several logins, email or username, case-insensitive login", async () => {
  const { checkLogin, builtInUsers } = await import("@/lib/session");
  process.env.APP_USERS = "Ryan@Example.ie:pw-1,jamie:pw-2";
  try {
    assert.equal(builtInUsers().isDefault, false);
    assert.equal(checkLogin("ryan@example.ie", "pw-1")?.login, "ryan@example.ie");
    assert.equal(checkLogin(" JAMIE ", "pw-2")?.login, "jamie");
    assert.equal(checkLogin("jamie", "pw-1"), null);
    assert.equal(checkLogin("demo@southline.ie", "southline"), null); // the old demo login never works
  } finally {
    delete process.env.APP_USERS;
  }
  assert.equal(builtInUsers().isDefault, true);
});

test("login is off by default, on with APP_USERS, Supabase only when asked", async () => {
  const { loginMode } = await import("@/lib/session");
  assert.equal(loginMode(), "off");
  process.env.APP_USERS = "ryan:pw";
  assert.equal(loginMode(), "password");
  delete process.env.APP_USERS;
  process.env.LOGIN = "supabase";
  assert.equal(loginMode(), "off", "LOGIN=supabase needs the Supabase keys too");
  Object.assign(process.env, { NEXT_PUBLIC_SUPABASE_URL: "u", NEXT_PUBLIC_SUPABASE_ANON_KEY: "a", SUPABASE_SERVICE_ROLE_KEY: "s" });
  try {
    assert.equal(loginMode(), "supabase");
  } finally {
    for (const k of ["LOGIN", "NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY"]) delete process.env[k];
  }
});
