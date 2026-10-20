"use server";

// Server actions behind the quick-action buttons. Each one revalidates the
// pages so the UI picks up the change immediately.

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getCredits } from "@/lib/adapters/sendmode";
import { testGhl } from "@/lib/adapters/ghl";
import { classifyReply, dailyBrief, draftMessage, summariseLead } from "@/lib/ai";
import { responseMinutes, scoreLead, speedToLead } from "@/lib/crm";
import { webLookup } from "@/lib/lookup";
import { addDays, isoDay } from "@/lib/utils";
import * as repo from "@/lib/repo";
import { authMode, currentUserEmail } from "@/lib/auth";
import { createIssue, githubConfigured } from "@/lib/adapters/github";
import { checkLogin, createSessionToken, SESSION_COOKIE, SESSION_MAX_AGE } from "@/lib/session";
import { getStore } from "@/lib/store";
import type { Channel, LeadStatus, ReplyTag } from "@/lib/types";
import { LEAD_STATUSES, REPLY_TAGS } from "@/lib/types";
import { createAuthClient } from "@/lib/supabase/server";

function refresh() {
  revalidatePath("/", "layout");
}

export async function setStatusAction(leadId: string, status: LeadStatus) {
  if (!LEAD_STATUSES.includes(status)) throw new Error("bad status");
  await repo.setLeadStatus(leadId, status);
  refresh();
}

export async function retagAction(messageId: string, tag: ReplyTag) {
  if (!REPLY_TAGS.includes(tag)) throw new Error("bad tag");
  await repo.retagMessage(messageId, tag, "manual");
  refresh();
}

/** Re-run the AI classifier on a reply. */
export async function reclassifyAction(messageId: string) {
  const m = await getStore().get("messages", messageId);
  if (!m) return;
  const { tag, source } = await classifyReply(m.body);
  await repo.retagMessage(messageId, tag, source);
  refresh();
}

export async function addNoteAction(leadId: string, body: string) {
  if (!body.trim()) return;
  await repo.addNote(leadId, body.trim());
  refresh();
}

export async function addFollowUpAction(leadId: string, dueDate: string, reason?: string) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dueDate)) throw new Error("bad date");
  await repo.addFollowUp(leadId, dueDate, reason);
  refresh();
}

export async function completeFollowUpAction(id: string) {
  await repo.completeFollowUp(id);
  refresh();
}

export async function draftAction(leadId: string, channel: Channel, goal?: string) {
  const detail = await repo.getLeadDetail(leadId);
  if (!detail) throw new Error("lead not found");
  return draftMessage(detail.lead, detail.messages, channel, goal);
}

export async function summariseAction(leadId: string) {
  const detail = await repo.getLeadDetail(leadId);
  if (!detail) throw new Error("lead not found");
  return summariseLead(detail.lead, detail.messages, detail.notes.filter((n) => n.kind === "note").map((n) => n.body));
}

/** Log a message I sent by hand (e.g. after copying an AI draft into my phone). */
export async function logSentAction(leadId: string, channel: Channel, body: string) {
  const lead = await getStore().get("leads", leadId);
  if (!lead || !body.trim()) return;
  await repo.recordMessage({ channel, direction: "outbound", body: body.trim(), email: lead.email, phone: lead.phone, business: lead.business, source: "manual" });
  refresh();
}

export async function updateLeadAction(leadId: string, form: FormData) {
  const get = (k: string) => (form.get(k) as string | null)?.trim() || null;
  const value = Number(get("deal_value"));
  await repo.updateLead(leadId, {
    name: get("name"), business: get("business"), email: get("email"), phone: get("phone"), trade: get("trade"), county: get("county"),
    deal_value: Number.isFinite(value) && value > 0 ? value : null,
  });
  refresh();
}

export async function createLeadAction(form: FormData) {
  const get = (k: string) => (form.get(k) as string | null)?.trim() || null;
  const lead = await repo.upsertLead({ name: get("name"), business: get("business"), email: get("email"), phone: get("phone"), trade: get("trade"), county: get("county") });
  refresh();
  redirect(`/leads/${lead.id}`);
}

export async function signInAction(form: FormData) {
  const email = String(form.get("email") ?? "").trim().toLowerCase();
  const password = String(form.get("password") ?? "");
  if (authMode() === "off") redirect("/");
  if (authMode() === "supabase") {
    const supabase = await createAuthClient();
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) redirect(`/login?error=${encodeURIComponent(error.message)}`);
  } else {
    const user = checkLogin(email, password);
    if (!user) redirect("/login?error=bad_login");
    (await cookies()).set(SESSION_COOKIE, await createSessionToken(user.login), {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: SESSION_MAX_AGE,
    });
  }
  redirect("/");
}

export async function signOutAction() {
  if (authMode() === "off") redirect("/");
  if (authMode() === "supabase") {
    const supabase = await createAuthClient();
    await supabase.auth.signOut();
  } else {
    (await cookies()).delete(SESSION_COOKIE);
  }
  redirect("/login");
}

// ---------- Integrations ----------

/** Send an SMS through SendMode (the button in the draft box). */
export async function sendSmsAction(leadId: string, text: string): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await repo.sendSmsToLead(leadId, text);
    if (res.ok) refresh();
    return res;
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

export async function testSendmodeAction() {
  const r = await getCredits();
  return r.ok ? { ok: true, detail: `Connected - ${r.credits} credits` } : { ok: false, detail: r.error ?? "failed" };
}

export async function testGhlAction() {
  return testGhl();
}

// ---------- Reply queue ----------

export async function draftReplyAction(messageId: string, regenerate = false, goal?: string) {
  return repo.draftForReply(messageId, { regenerate, goal });
}

/** Approve a drafted reply: SMS goes out via SendMode, email is logged as sent (send it from your email tool). */
export async function approveReplyAction(messageId: string, text: string): Promise<{ ok: boolean; error?: string; sent?: boolean }> {
  try {
    const reply = await getStore().get("messages", messageId);
    if (!reply) return { ok: false, error: "Reply not found" };
    if (reply.channel === "sms") {
      const res = await repo.sendSmsToLead(reply.lead_id, text);
      if (!res.ok) return res;
      refresh();
      return { ok: true, sent: true };
    }
    await logSentAction(reply.lead_id, "email", text);
    return { ok: true, sent: false };
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

export async function dismissReplyAction(messageId: string) {
  await repo.dismissReply(messageId, "Reply handled outside the app");
  refresh();
}

// ---------- Today ----------

const briefCache = globalThis as unknown as { __brief?: { key: string; text: string; source: string } };

/** Today's AI brief. Cached for an hour so reloading the page doesn't cost a Claude call each time. */
export async function briefAction(force = false) {
  const today = isoDay();
  const [queue, followUps, leads, messages] = await Promise.all([repo.replyQueue(), repo.followUpQueue(today), getStore().all("leads"), getStore().all("messages")]);
  const byLead = repo.groupBy(messages, (m) => m.lead_id);
  const hot = leads
    .map((l) => ({ l, s: scoreLead(l, byLead.get(l.id) ?? []) }))
    .filter((x) => x.s.hot)
    .sort((a, b) => b.s.score - a.s.score)
    .slice(0, 5);
  const yday = addDays(today, -1);
  const ym = messages.filter((m) => isoDay(m.sent_at) === yday);
  const input = {
    waitingCount: queue.length,
    waiting: queue.slice(0, 8).map((q) => ({ name: q.lead.name ?? q.lead.business ?? "lead", said: q.reply.body.slice(0, 140), tag: q.reply.ai_tag, hours: Math.round(q.waitingMinutes / 60), score: q.score.score })),
    followUpsDue: followUps.filter((f) => f.followUp).length,
    hot: hot.map((h) => ({ name: h.l.name ?? h.l.business ?? "lead", reasons: h.s.reasons })),
    yesterday: { sent: ym.filter((m) => m.direction === "outbound").length, replies: ym.filter((m) => m.direction === "inbound").length, positive: ym.filter((m) => m.ai_tag === "interested").length },
    medianReplyMinutes: speedToLead(responseMinutes(messages, { from: new Date(Date.now() - 7 * 864e5).toISOString(), to: null })).median,
  };
  const key = `${new Date().toISOString().slice(0, 13)}:${JSON.stringify(input).length}:${queue.length}`;
  if (!force && briefCache.__brief?.key === key) return briefCache.__brief;
  const out = await dailyBrief(input);
  briefCache.__brief = { key, ...out };
  return briefCache.__brief;
}

// ---------- Check number ----------

export async function crmLookupAction(number: string) {
  return repo.crmLookup(number);
}

export async function webLookupAction(number: string, fresh = false) {
  return webLookup(number, { fresh });
}

/** Save what Claude found as a lead (or fill in gaps on the existing lead). */
export async function saveLookupAction(number: string, found: { name?: string | null; business?: string | null; trade?: string | null; location?: string | null }, note?: string) {
  const lead = await repo.upsertLead({ phone: number, name: found.name, business: found.business, trade: found.trade, county: found.location });
  if (note) await repo.addNote(lead.id, note);
  refresh();
  return { id: lead.id };
}

// ---------- Request a change (Claude builds it) ----------

export async function requestChangeAction(kind: "feature" | "bug", text: string, page: string | null) {
  if (!text.trim()) return { ok: false as const, error: "Describe the change first." };
  const by = await currentUserEmail();
  const saved = await repo.submitChangeRequest({ kind, text, page, by }, (title, body, labels) => (githubConfigured() ? createIssue(title, body, labels) : null));
  refresh();
  return saved.issue_url ? { ok: true as const, url: saved.issue_url, number: saved.issue_number } : { ok: false as const, error: saved.error ?? "Not sent", saved: true, issueText: repo.changeRequestIssue(kind, text, page, by).body };
}
