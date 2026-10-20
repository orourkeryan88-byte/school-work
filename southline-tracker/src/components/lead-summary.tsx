"use client";

import { Sparkles } from "lucide-react";
import { useState, useTransition } from "react";
import { summariseAction } from "@/app/actions";
import { Button } from "@/components/ui/button";

/** "Summarise in 3 lines" button for the lead page. */
export function LeadSummary({ leadId }: { leadId: string }) {
  const [text, setText] = useState<string | null>(null);
  const [pending, start] = useTransition();
  return (
    <div className="space-y-2">
      <Button size="sm" variant="outline" disabled={pending} onClick={() => start(async () => setText((await summariseAction(leadId)).text))}>
        <Sparkles /> {pending ? "Summarising…" : text ? "Refresh summary" : "Summarise lead"}
      </Button>
      {text && <div className="rounded-md bg-muted p-3 text-sm whitespace-pre-line">{text}</div>}
    </div>
  );
}
