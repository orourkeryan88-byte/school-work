"use server";

// Server actions behind the quick-action buttons. Each one revalidates the
// pages so the UI picks up the change immediately.

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getCredits } from "@/lib/adapters/sendmode";
import { testGhl } from "@/lib/adapters/ghl";
import { classifyReply, draftMessage, summariseLead } from "@/lib/ai";
import * as repo from "@/lib/repo";
import { authMode } from "@/lib/auth";
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
  await repo.updateLead(leadId, { name: get("name"), business: get("business"), email: get("email"), phone: get("phone"), trade: get("trade"), county: get("county") });
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
  redirect("/inbox");
}

export async function signOutAction() {
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
