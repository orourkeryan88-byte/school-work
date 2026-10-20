// "Request a change": the GitHub issue Claude works from.
import assert from "node:assert/strict";
import { test } from "node:test";
import { createIssue } from "@/lib/adapters/github";
import * as repo from "@/lib/repo";

test("issue text mentions @claude, has a short title and the page", () => {
  const { title, body } = repo.changeRequestIssue("feature", "Add a button to send the price list by SMS\nOn every lead page", "/leads/abc", "ryan@x.ie");
  assert.equal(title, "Feature: Add a button to send the price list by SMS");
  assert.match(body, /^@claude please build this feature/);
  assert.match(body, /\/leads\/abc/);
  assert.match(body, /npm test/);
  assert.ok(repo.changeRequestIssue("bug", "x".repeat(200), null, null).title.length <= 90);
});

test("submitChangeRequest saves the request with the issue link, or the reason it wasn't sent", async () => {
  const sent = await repo.submitChangeRequest({ kind: "bug", text: "Pipeline total wrong", page: "/pipeline", by: "jamie" }, async () => ({ url: "https://github.com/o/r/issues/7", number: 7 }));
  assert.equal(sent.issue_number, 7);
  assert.equal(sent.error, null);
  const notConnected = await repo.submitChangeRequest({ kind: "feature", text: "Dark green theme", page: null, by: null }, () => null);
  assert.equal(notConnected.issue_url, null);
  assert.match(notConnected.error ?? "", /GITHUB_TOKEN/);
  const failed = await repo.submitChangeRequest({ kind: "feature", text: "x", page: null, by: null }, async () => {
    throw new Error("GitHub 401: Bad credentials");
  });
  assert.match(failed.error ?? "", /401/);
});

test("createIssue retries without labels when GitHub rejects them", async () => {
  process.env.GITHUB_REPO = "o/r";
  process.env.GITHUB_TOKEN = "t";
  const bodies: string[] = [];
  const fake = (async (_url: string, init: RequestInit) => {
    bodies.push(String(init.body));
    return bodies.length === 1
      ? new Response("{}", { status: 422 })
      : new Response(JSON.stringify({ html_url: "https://github.com/o/r/issues/9", number: 9 }), { status: 201 });
  }) as unknown as typeof fetch;
  const r = await createIssue("t", "b", ["claude"], fake);
  assert.equal(r.number, 9);
  assert.deepEqual(JSON.parse(bodies[1]).labels, []);
});
