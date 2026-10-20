// Check number: CRM lookup, number formats, and parsing Claude's web-search answer.
import assert from "node:assert/strict";
import { test } from "node:test";
import { parseLookup, phoneVariants, webLookup } from "@/lib/lookup";
import * as repo from "@/lib/repo";

test("phone variants cover the ways Irish numbers are written", () => {
  const v = phoneVariants("+353871234567");
  assert.ok(v.includes("087 123 4567"));
  assert.ok(v.includes("0871234567"));
  assert.ok(v.includes("+353 87 123 4567"));
  assert.deepEqual(phoneVariants("not a number"), []);
});

const searchResult = (urls: [string, string][]) => ({
  type: "web_search_tool_result",
  tool_use_id: "t1",
  content: urls.map(([url, title]) => ({ type: "web_search_result", url, title, encrypted_content: "", page_age: null })),
});

test("parseLookup keeps only sources the search actually returned", () => {
  const r = parseLookup([
    searchResult([["https://www.goldenpages.ie/murphy-plumbing", "Murphy Plumbing - Golden Pages"]]),
    {
      type: "text",
      text: 'Found it.<result>{"found":true,"name":"Seán Murphy","business":"Murphy Plumbing & Heating","trade":"Plumber","location":"Cork","website":"murphyplumbing.ie","summary":"Plumber in Cork.","confidence":"high","source_urls":["https://www.goldenpages.ie/murphy-plumbing","https://made-up.example/fake"]}</result>',
      citations: null,
    },
  ] as never);
  assert.equal(r.found, true);
  assert.equal(r.business, "Murphy Plumbing & Heating");
  assert.equal(r.trade, "Plumber");
  assert.deepEqual(r.sources.map((s) => s.url), ["https://www.goldenpages.ie/murphy-plumbing"]); // invented URL dropped
  assert.equal(r.confidence, "high");
});

test("parseLookup: no verifiable source can't be high confidence; private numbers aren't 'found'", () => {
  const noSrc = parseLookup([{ type: "text", text: '<result>{"found":true,"business":"X Ltd","confidence":"high","summary":"s","source_urls":["https://nope.ie"]}</result>', citations: null }] as never);
  assert.equal(noSrc.confidence, "medium");
  assert.equal(noSrc.sources.length, 0);
  const priv = parseLookup([{ type: "text", text: '<result>{"found":false,"name":null,"business":null,"trade":null,"location":null,"website":null,"summary":"Looks like a private mobile - no business listing.","confidence":"none","source_urls":[]}</result>', citations: null }] as never);
  assert.equal(priv.found, false);
  assert.match(priv.summary, /private/);
  assert.equal(parseLookup([{ type: "text", text: "garbage", citations: null }] as never).found, false);
});

test("webLookup resumes paused searches, then caches the answer", async () => {
  process.env.ANTHROPIC_API_KEY = "test";
  let calls = 0;
  const fake = {
    beta: {
      messages: {
        create: async () => {
          calls++;
          if (calls === 1) return { stop_reason: "pause_turn", content: [searchResult([["https://kellyelectrical.ie", "Kelly Electrical"]])] };
          return {
            stop_reason: "end_turn",
            content: [
              searchResult([["https://kellyelectrical.ie", "Kelly Electrical"]]),
              { type: "text", text: '<result>{"found":true,"name":"Aine Kelly","business":"Kelly Electrical","trade":"Electrician","location":"Galway","website":"kellyelectrical.ie","summary":"Electrician in Galway.","confidence":"high","source_urls":["https://kellyelectrical.ie"]}</result>', citations: null },
            ],
          };
        },
      },
    },
  };
  try {
    const r = await webLookup("086 555 0202", { client: fake as never });
    assert.equal(calls, 2);
    assert.equal(r.business, "Kelly Electrical");
    const again = await webLookup("+353865550202", { client: fake as never }); // same number, other format
    assert.equal(calls, 2, "served from cache");
    assert.equal(again.business, "Kelly Electrical");
  } finally {
    delete process.env.ANTHROPIC_API_KEY;
  }
  const noKey = await webLookup("0871111111");
  assert.match(noKey.error ?? "", /ANTHROPIC_API_KEY/);
});

test("crmLookup finds a lead by any number format", async () => {
  const lead = await repo.upsertLead({ name: "Tom Nolan", phone: "087 555 0101", business: "Nolan Roofing" });
  const hit = await repo.crmLookup("+353 87 555 0101");
  assert.equal(hit?.lead?.id, lead.id);
  assert.equal((await repo.crmLookup("0870000001"))?.lead, null);
  assert.equal(await repo.crmLookup("hello"), null);
});
