import { NextResponse } from "next/server";
import { getStore } from "@/lib/store";

// GET /api/search?q=  - leads for the ⌘K palette (behind login via middleware).
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const q = (new URL(req.url).searchParams.get("q") ?? "").toLowerCase().trim();
  if (q.length < 2) return NextResponse.json({ leads: [] });
  const digits = q.replace(/\D/g, "");
  const leads = (await getStore().all("leads"))
    .filter((l) =>
      [l.name, l.business, l.email, l.county, l.trade].some((s) => s?.toLowerCase().includes(q)) ||
      (digits.length >= 4 && l.phone?.replace(/\D/g, "").includes(digits.replace(/^0/, ""))),
    )
    .slice(0, 8)
    .map((l) => ({ id: l.id, name: l.name ?? l.business ?? l.email ?? l.phone, sub: [l.business, l.trade, l.county].filter(Boolean).join(" · "), status: l.status }));
  return NextResponse.json({ leads });
}
