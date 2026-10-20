// GoHighLevel + SendMode adapters. No network: fetch is stubbed.
import assert from "node:assert/strict";
import { test } from "node:test";
import { mergeContact, parseGhlPayload } from "@/lib/adapters/ghl";
import { parseDeliveryReport, sendSms } from "@/lib/adapters/sendmode";
import { importRows } from "@/lib/importer";
import * as repo from "@/lib/repo";
import { getStore } from "@/lib/store";

test("GHL InboundMessage SMS -> inbound sms row keyed on contact", () => {
  const r = parseGhlPayload({
    type: "InboundMessage", locationId: "loc1", contactId: "c_123", conversationId: "conv1", messageId: "m1",
    messageType: "SMS", body: "Yeah how much?", direction: "inbound", dateAdded: "2026-10-19T10:00:00.000Z", from: "+353871110000", to: "+353861234567",
  });
  assert.equal(r.kind, "row");
  if (r.kind !== "row") return;
  assert.equal(r.channel, "sms");
  assert.equal(r.row.direction, "inbound");
  assert.equal(r.row.phone, "+353871110000"); // the contact, not my number
  assert.equal(r.row.external_id, "m1");
  assert.equal(r.needsLookup, false);
});

test("GHL OutboundMessage email without address needs a contact lookup", () => {
  const r = parseGhlPayload({ type: "OutboundMessage", contactId: "c_9", messageType: "Email", html: "<p>Hi Joe</p>", messageId: "e1" });
  assert.ok(r.kind === "row" && r.channel === "email" && r.needsLookup && r.row.body === "Hi Joe" && r.row.direction === "outbound");
  if (r.kind !== "row") return;
  const merged = mergeContact(r.row, { id: "c_9", firstName: "Joe", lastName: "Byrne", email: "joe@byrne.ie", companyName: "Byrne Roofing" });
  assert.equal(merged.email, "joe@byrne.ie");
  assert.equal(merged.name, "Joe Byrne");
  assert.equal(merged.business, "Byrne Roofing");
});

test("GHL calls are ignored", () => {
  assert.equal(parseGhlPayload({ type: "InboundMessage", messageType: "CALL", contactId: "c" }).kind, "ignore");
});

test("GHL workflow webhook uses contact fields + custom data + URL defaults", () => {
  const r = parseGhlPayload(
    { contact_id: "c_55", first_name: "Aine", last_name: "Kelly", email: "aine@kelly.ie", phone: "+353865550202", company_name: "Kelly Electrical", customData: { message: "Not for us", campaign: "GHL Nov" } },
    { channel: "email", direction: "inbound" },
  );
  assert.ok(r.kind === "row");
  if (r.kind !== "row") return;
  assert.equal(r.channel, "email");
  assert.equal(r.row.direction, "inbound");
  assert.equal(r.row.body, "Not for us");
  assert.equal(r.row.name, "Aine Kelly");
  assert.equal(r.row.campaign, "GHL Nov");
});

test("GHL rows import and match on contact id across events", async () => {
  const a = await importRows([{ direction: "outbound", body: "Hi from GHL", email: "ghltest@example.ie", ghl_contact_id: "c_777" }], { channel: "email", kind: "webhook", source: "ghl" });
  // Later event only has the contact id (no API key to look it up) - still lands on the same lead.
  const b = await importRows([{ direction: "inbound", body: "Sounds good, ring me", ghl_contact_id: "c_777" }], { channel: "email", kind: "webhook", source: "ghl" });
  assert.equal(a.imported, 1);
  assert.equal(b.imported, 1);
  const lead = (await getStore().all("leads")).find((l) => l.ghl_contact_id === "c_777")!;
  const msgs = await getStore().all("messages", { lead_id: lead.id });
  assert.equal(msgs.length, 2);
  assert.equal(lead.status, "interested");
});

test("SendMode send builds the documented request", async () => {
  process.env.SENDMODE_ACCESS_KEY = "test-key";
  process.env.SENDMODE_SENDER_ID = "Southline";
  let seen: { url: string; init: RequestInit } | null = null;
  const fake = (async (url: string, init: RequestInit) => {
    seen = { url, init };
    return new Response(JSON.stringify({ status: "OK", statusCode: 0 }), { status: 200 });
  }) as unknown as typeof fetch;
  const res = await sendSms({ to: "+353871234567", text: "Hi Tom", customerId: "ref1" }, fake);
  assert.ok(res.ok);
  assert.equal(seen!.url, "https://rest.sendmode.com/v2/send");
  assert.equal((seen!.init.headers as Record<string, string>).Authorization, "test-key");
  const msg = JSON.parse(new URLSearchParams(String(seen!.init.body)).get("message")!);
  assert.deepEqual(msg, { messagetext: "Hi Tom", recipients: ["353871234567"], customerid: "ref1", senderid: "Southline" });
});

test("SendMode errors are reported, not swallowed", async () => {
  process.env.SENDMODE_ACCESS_KEY = "bad";
  const fake = (async () => new Response(JSON.stringify({ errorCode: 14, description: "INVALID_ACCESS_KEY" }), { status: 401 })) as unknown as typeof fetch;
  const res = await sendSms({ to: "+353871234567", text: "x", customerId: "r" }, fake);
  assert.equal(res.ok, false);
  assert.match(res.error!, /INVALID_ACCESS_KEY/);
});

test("SendMode delivery report parsing is case-insensitive", () => {
  assert.deepEqual(parseDeliveryReport({ EventID: "9", Phonenumber: "35387", DataType: "SMS", Status: "Delivered", CustomerID: "abc" }), {
    eventId: "9", phone: "35387", status: "Delivered", customerId: "abc",
  });
});

test("sendSmsToLead logs the message and the delivery report updates it", async () => {
  const lead = await repo.upsertLead({ name: "Tom", phone: "087 555 0101", business: "Nolan Roofing" });
  let ref = "";
  const fakeSend = async (o: { customerId: string }) => {
    ref = o.customerId;
    return { ok: true, raw: {} };
  };
  const res = await repo.sendSmsToLead(lead.id, "Hi Tom, quick one", fakeSend as never);
  assert.ok(res.ok);
  assert.ok(await repo.applyDeliveryReport(ref, "Delivered"));
  const m = (await getStore().all("messages", { lead_id: lead.id })).find((x) => x.external_id === ref)!;
  assert.equal(m.delivery_status, "delivered");
  assert.equal(m.source, "sendmode");

  // Unsubscribed leads are never texted.
  await getStore().update("leads", lead.id, { unsubscribed: true });
  const blocked = await repo.sendSmsToLead(lead.id, "again", fakeSend as never);
  assert.equal(blocked.ok, false);
});

test("SendMode network failure returns an error instead of throwing", async () => {
  process.env.SENDMODE_ACCESS_KEY = "k";
  const fake = (async () => {
    throw Object.assign(new TypeError("fetch failed"), { cause: { code: "ENOTFOUND" } });
  }) as unknown as typeof fetch;
  const res = await sendSms({ to: "+353871234567", text: "x", customerId: "r" }, fake);
  assert.equal(res.ok, false);
  assert.match(res.error!, /ENOTFOUND/);
});
