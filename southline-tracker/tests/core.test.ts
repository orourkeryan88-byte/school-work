// Run with: npm test
// tests/setup.ts switches to the in-memory store and rule-based AI.
import assert from "node:assert/strict";
import { test } from "node:test";
import { classifyByRules } from "@/lib/ai";
import { normalizeEvent, parseCsv, toCsv } from "@/lib/ingest";
import * as repo from "@/lib/repo";
import { campaignStats, funnel } from "@/lib/stats";
import { getStore } from "@/lib/store";
import { businessKey, normalizePhone, parseDate } from "@/lib/utils";

test("normalizePhone handles Irish formats", () => {
  assert.equal(normalizePhone("087 123 4567"), "+353871234567");
  assert.equal(normalizePhone("00353 87 123 4567"), "+353871234567");
  assert.equal(normalizePhone("+353 (0)87 1234567"), "+353871234567");
  assert.equal(normalizePhone("353871234567"), "+353871234567");
  assert.equal(normalizePhone(""), null);
});

test("parseDate treats bare dates as Irish time", () => {
  assert.equal(parseDate("2026-10-18 14:22"), "2026-10-18T13:22:00.000Z"); // IST = UTC+1
  assert.equal(parseDate("18/12/2026 14:22"), "2026-12-18T14:22:00.000Z"); // GMT in winter
  assert.equal(parseDate("2026-10-18T14:22:00Z"), "2026-10-18T14:22:00.000Z");
  assert.equal(parseDate("1760000000"), new Date(1760000000000).toISOString());
  assert.equal(parseDate("garbage"), null);
});

test("businessKey ignores punctuation and Ltd", () => {
  assert.equal(businessKey("O'Brien Plumbing Ltd."), businessKey("obrien plumbing"));
});

test("classifyByRules", () => {
  assert.equal(classifyByRules("STOP"), "unsubscribe");
  assert.equal(classifyByRules("Yeah go on, how much is it?"), "interested");
  assert.equal(classifyByRules("No thanks"), "not_interested");
  assert.equal(classifyByRules("I'm out of the office until Monday"), "out_of_office");
  assert.equal(classifyByRules("Customers won't talk to a robot"), "objection");
  assert.equal(classifyByRules("Does it work with my number?"), "question");
});

test("normalizeEvent: Smartlead-style email reply", () => {
  const r = normalizeEvent(
    { event_type: "EMAIL_REPLY", sl_lead_email: "Joe@Example.ie", campaign_name: "Test", reply_message: { text: "Sounds good\n\nOn Mon, 1 Jan Ryan wrote:\n> hi" } },
    "email",
  );
  assert.ok(r.ok);
  assert.equal(r.event.direction, "inbound");
  assert.equal(r.event.email, "Joe@Example.ie");
  assert.equal(r.event.body, "Sounds good");
  assert.equal(r.event.campaign, "Test");
});

test("normalizeEvent: SendMode-style inbound SMS uses 'from' as the lead", () => {
  const r = normalizeEvent({ from: "0871112222", to: "Southline", message: "yes interested" }, "sms", { direction: "inbound" });
  assert.ok(r.ok);
  assert.equal(r.event.phone, "0871112222");
  assert.equal(r.event.direction, "inbound");
});

test("normalizeEvent: rejects missing fields", () => {
  assert.equal(normalizeEvent({ message: "hi" }, "sms").ok, false);
  assert.equal(normalizeEvent({ email: "a@b.ie" }, "email").ok, false);
});

test("CSV round trip", () => {
  const rows = parseCsv("﻿Email,Message,Campaign Name\na@b.ie,hello,X\n");
  assert.equal(rows.length, 1);
  const r = normalizeEvent(rows[0], "email");
  assert.ok(r.ok && r.event.campaign === "X");
  assert.match(toCsv([{ a: 1, b: null }]), /a,b\r?\n1,/);
});

test("recordMessage: matches across channels, links replies, moves status", async () => {
  const sent = await repo.recordMessage({ channel: "email", direction: "outbound", body: "Hi Joe", email: "joe@joesplumbing.ie", business: "Joe's Plumbing Ltd", name: "Joe", campaign: "Test camp", variant: "A" });
  assert.equal(sent.status, "created");
  if (sent.status !== "created") return;
  assert.equal(sent.lead.status, "contacted");

  // SMS with only business name + phone -> same lead (matched on business).
  const sms = await repo.recordMessage({ channel: "sms", direction: "outbound", body: "Hi Joe sms", phone: "087 999 0000", business: "joes plumbing" });
  assert.equal(sms.status === "created" && sms.lead.id, sent.lead.id);

  // Reply by phone -> same lead, linked to the SMS, tagged interested.
  const reply = await repo.recordMessage({ channel: "sms", direction: "inbound", body: "Yeah go on, ring me", phone: "+353879990000" });
  assert.equal(reply.status, "created");
  if (reply.status !== "created") return;
  assert.equal(reply.lead.id, sent.lead.id);
  assert.equal(reply.message.reply_to_id, sms.status === "created" ? sms.message.id : "");
  assert.equal(reply.message.ai_tag, "interested");
  assert.equal(reply.lead.status, "interested");
  assert.equal(reply.lead.phone, "+353879990000");

  // A later send doesn't drag the status backwards.
  const again = await repo.recordMessage({ channel: "email", direction: "outbound", body: "Follow up", email: "joe@joesplumbing.ie" });
  assert.equal(again.status === "created" && again.lead.status, "interested");

  // Duplicate external id is ignored.
  const d1 = await repo.recordMessage({ channel: "sms", direction: "outbound", body: "x", phone: "0861234567", external_id: "abc", source: "sendmode" });
  const d2 = await repo.recordMessage({ channel: "sms", direction: "outbound", body: "x", phone: "0861234567", external_id: "abc", source: "sendmode" });
  assert.equal(d1.status, "created");
  assert.equal(d2.status, "duplicate");

  // STOP marks lost + unsubscribed.
  const stop = await repo.recordMessage({ channel: "sms", direction: "inbound", body: "STOP", phone: "0861234567" });
  assert.ok(stop.status === "created" && stop.lead.status === "lost" && stop.lead.unsubscribed);

  const detail = await repo.getLeadDetail(sent.lead.id);
  assert.ok(detail && detail.messages.length === 4);
  assert.ok(detail.timeline.some((t) => t.type === "note" && t.note.kind === "status"));
});

test("stats over mock data are sane", async () => {
  const store = getStore();
  const [messages, leads, campaigns] = await Promise.all([store.all("messages"), store.all("leads"), store.all("campaigns")]);
  const all = funnel(messages, leads, { from: null, to: null });
  const email = funnel(messages, leads, { from: null, to: null }, "email");
  const sms = funnel(messages, leads, { from: null, to: null }, "sms");
  assert.ok(all.sent > 50 && all.replies > 10);
  assert.equal(email.sent + sms.sent, all.sent);
  assert.equal(email.booked + sms.booked, all.booked);
  assert.ok(all.replyRate > 0 && all.replyRate < 100);
  const cs = campaignStats(campaigns, messages, leads, { from: null, to: null });
  assert.ok(cs.find((c) => c.campaign.id === "cmp_email_dublin")!.variants.length === 2);
});

test("follow-up queue lists people waiting on me", async () => {
  const q = await repo.followUpQueue();
  assert.ok(q.length > 0);
  assert.ok(q.every((i) => !i.lead.unsubscribed));
});
