import type { Metadata } from "next";
import { CheckNumber } from "@/components/check-number";
import { PageHeader } from "@/components/page-header";
import { aiEnabled } from "@/lib/ai";

export const metadata: Metadata = { title: "Check number" };

export default async function CheckPage({ searchParams }: { searchParams: Promise<{ number?: string }> }) {
  const { number } = await searchParams;
  return (
    <>
      <PageHeader title="Check number" description="Not sure who you're texting? Paste the number - see what your CRM knows, and what Claude finds online." />
      <CheckNumber initial={number} aiOn={aiEnabled()} />
    </>
  );
}
