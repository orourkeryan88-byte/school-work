"use client";

import { AlarmClock, Check } from "lucide-react";
import { useTransition } from "react";
import { addFollowUpAction, completeFollowUpAction } from "@/app/actions";
import { Button } from "@/components/ui/button";
import { addDays, isoDay } from "@/lib/utils";

/** Done / snooze buttons for a follow-up queue item. */
export function FollowUpActions({ leadId, followUpId, reason }: { leadId: string; followUpId: string | null; reason: string }) {
  const [pending, start] = useTransition();
  const snooze = (days: number) =>
    start(async () => {
      if (followUpId) await completeFollowUpAction(followUpId);
      await addFollowUpAction(leadId, addDays(isoDay(), days), reason);
    });
  return (
    <div className="flex flex-wrap gap-1.5">
      {followUpId && (
        <Button size="sm" variant="outline" disabled={pending} onClick={() => start(() => completeFollowUpAction(followUpId))}>
          <Check /> Done
        </Button>
      )}
      <Button size="sm" variant="outline" disabled={pending} onClick={() => snooze(2)}>
        <AlarmClock /> +2 days
      </Button>
      <Button size="sm" variant="ghost" disabled={pending} onClick={() => snooze(7)}>
        +1 week
      </Button>
    </div>
  );
}
