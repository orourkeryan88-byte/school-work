// Lead scoring, reply queue, speed-to-lead, quiet hours, SMS segments, pipeline.
import assert from "node:assert/strict";
import { test } from "node:test";
import { awaitingReply, pipelineTotals, responseMinutes, scoreLead, sendWindow, smsSegments, speedToLead, toGsmFriendly } from "@/lib/crm";
import * as repo from "@/lib/repo";
import { getStore } from "@/lib/store";
import type { Lead, Message } from "@/lib/types";

const now = Date.parse("2026-10-20T12:00:00Z");
const lead = (over: Partial<Lead> = {}): Lead => ({
  id: "L", name: "Joe", business: "Joe's", email: null, phone: "+353870000000", trade: null, county: null, status: "replied",
  unsubscribed: false, booked_at: null, won_at: null, created_at: "", updated_at: "", ...over,
});
let n = 0;
const msg = (direction: Message["direction"], hoursAgo: number, over: Partial<Message> = {}): Message => ({
  id: `m${++n}`, lead_id: "L", campaign_id: null, channel: "sms", direction, body: "x", subject: null, variant: null,
  sent_at: new Date(now - hoursAgo * 36e5).toISOString(), reply_to_id: null, ai_tag: null, ai_tag_source: null, source: null, external_id: null, created_at: "", ...over,
});

test("awaitingReply: only when their message is the latest and needs an answer", () => {
  assert.ok(awaitingReply(lead(), [msg("outbound", 10), msg("inbound", 2, { ai_tag: "question" })]));
  assert.equal(awaitingReply(lead(), [msg("inbound", 5), msg("outbound", 1)]), null); // I already answered
  assert.equal(awaitingReply(lead(), [msg("outbound", 10), msg("inbound", 2, { ai_tag: "unsubscribe" })]), null);
  assert.equal(awaitingReply(lead(), [msg("outbound", 10), msg("inbound", 2, { ai_tag: "out_of_office" })]), null);
  assert.equal(awaitingReply(lead(), [msg("inbound", 2, { reply_handled_at: "x" })]), null); // dismissed
  assert.equal(awaitingReply(lead({ unsubscribed: true }), [msg("inbound", 2)]), null);
});

test("scoreLead: fresh interested reply waiting on me is hot, with readable reasons", () => {
  const s = scoreLead(lead({ status: "interested" }), [msg("outbound", 30), msg("inbound", 3, { ai_tag: "interested" })], now);
  assert.ok(s.hot, `expected hot, got ${s.score}`);
  assert.ok(s.reasons.includes("Waiting on your reply"));
  assert.ok(s.reasons.includes("Said they're interested"));
  const cold = scoreLead(lead({ status: "contacted" }), [msg("outbound", 24 * 10)], now);
  assert.ok(cold.score < 20 && !cold.hot);
  assert.equal(scoreLead(lead({ unsubscribed: true }), [], now).score, 0);
});

test("speed to lead: time from their reply to my next message", () => {
  const mins = responseMinutes([msg("outbound", 50), msg("inbound", 10), msg("inbound", 9.5), msg("outbound", 9), msg("inbound", 5), msg("outbound", 2)]);
  // 10h -> 9h = 60 min (the 9.5h follow-on message isn't timed separately), 5h -> 2h = 180 min
  assert.deepEqual(mins.map(Math.round), [60, 180]);
  const s = speedToLead(mins);
  assert.equal(s.median, 120);
  assert.equal(s.within1h, 50);
});

test("quiet hours use Irish time", () => {
  process.env.SMS_SEND_HOURS = "09-20";
  process.env.SMS_SEND_DAYS = "1-6";
  try {
    assert.equal(sendWindow(new Date("2026-10-20T10:00:00Z")).ok, true); // Tue 11:00 IST
    assert.equal(sendWindow(new Date("2026-10-20T19:30:00Z")).ok, false); // Tue 20:30 IST
    assert.equal(sendWindow(new Date("2026-12-15T08:30:00Z")).ok, false); // 08:30 GMT in winter
    assert.equal(sendWindow(new Date("2026-10-25T12:00:00Z")).ok, false); // Sunday
  } finally {
    process.env.SMS_SEND_HOURS = "00-24";
    process.env.SMS_SEND_DAYS = "1-7";
  }
});

test("SMS segments: a fada turns 160-char SMS into 70-char Unicode", () => {
  assert.deepEqual(smsSegments("a".repeat(160)), { length: 160, unicode: false, segments: 1, limit: 160 });
  assert.equal(smsSegments("a".repeat(161)).segments, 2);
  const irish = `Hi Seán, ${"x".repeat(70)}`;
  assert.equal(smsSegments(irish).unicode, true);
  assert.equal(smsSegments(irish).segments, 2);
  assert.equal(toGsmFriendly("Seán Ó Briain – Siobhán’s"), "Sean O Briain - Siobhan's");
  assert.equal(smsSegments(toGsmFriendly(irish)).segments, 1);
  assert.equal(smsSegments("€5").length, 3); // € is a 2-unit GSM extension char
});

test("pipeline totals and weighted forecast", () => {
  const t = pipelineTotals([lead({ status: "interested", deal_value: 100 }), lead({ status: "booked", deal_value: 200 }), lead({ status: "won", deal_value: 149 }), lead({ status: "lost", deal_value: 999 })]);
  assert.equal(t.openValue, 300);
  assert.equal(t.weighted, Math.round(100 * 0.35 + 200 * 0.6));
  assert.equal(t.wonMrr, 149);
});

test("reply queue: drafts are cached, sending/dismissing clears the item, quiet hours block SMS", async () => {
  const q = await repo.replyQueue();
  assert.ok(q.length > 0);
  assert.ok(q.every((i, k) => k === 0 || q[k - 1].score.score >= i.score.score), "sorted hottest first");
  const first = q[0];

  const d1 = await repo.draftForReply(first.reply.id);
  assert.ok(d1.text.length > 0);
  const stored = await getStore().get("messages", first.reply.id);
  assert.equal(stored?.ai_draft, d1.text); // cached

  await repo.dismissReply(first.reply.id);
  assert.ok(!(await repo.replyQueue()).some((i) => i.reply.id === first.reply.id));

  const smsItem = (await repo.replyQueue()).find((i) => i.reply.channel === "sms")!;
  process.env.SMS_SEND_HOURS = "00-00"; // nothing allowed
  try {
    const r = await repo.sendSmsToLead(smsItem.lead.id, "hi", (async () => ({ ok: true, raw: {} })) as never);
    assert.equal(r.ok, false);
    assert.match(r.ok ? "" : r.error, /Quiet hours/);
  } finally {
    process.env.SMS_SEND_HOURS = "00-24";
  }
  const sent = await repo.sendSmsToLead(smsItem.lead.id, "hi", (async () => ({ ok: true, raw: {} })) as never);
  assert.ok(sent.ok);
  assert.ok(!(await repo.replyQueue()).some((i) => i.lead.id === smsItem.lead.id), "answered lead leaves the queue");
});
