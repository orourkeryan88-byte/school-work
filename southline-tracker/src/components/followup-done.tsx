"use client";

import { Check } from "lucide-react";
import { useTransition } from "react";
import { completeFollowUpAction } from "@/app/actions";
import { Button } from "@/components/ui/button";

export function FollowUpDoneButton({ id, label = "Done" }: { id: string; label?: string }) {
  const [pending, start] = useTransition();
  return (
    <Button size="sm" variant="outline" disabled={pending} onClick={() => start(() => completeFollowUpAction(id))}>
      <Check /> {label}
    </Button>
  );
}
