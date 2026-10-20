import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Lead } from "@/lib/types";

const FIELDS = [
  ["name", "Name"],
  ["business", "Business"],
  ["email", "Email"],
  ["phone", "Phone"],
  ["trade", "Trade"],
  ["county", "County"],
] as const;

/** Lead contact details form, used for "Add lead" and "Edit details". */
export function LeadForm({ lead, action, submit }: { lead?: Lead; action: (form: FormData) => Promise<void>; submit: string }) {
  return (
    <form action={action} className="grid gap-3 sm:grid-cols-2">
      {FIELDS.map(([key, label]) => (
        <div key={key} className="space-y-1.5">
          <Label htmlFor={key}>{label}</Label>
          <Input id={key} name={key} defaultValue={lead?.[key] ?? ""} type={key === "email" ? "email" : "text"} />
        </div>
      ))}
      {lead && (
        <div className="space-y-1.5">
          <Label htmlFor="deal_value">Deal value (€/month)</Label>
          <Input id="deal_value" name="deal_value" type="number" min="0" step="1" defaultValue={lead.deal_value ?? ""} placeholder="Default" />
        </div>
      )}
      <div className="sm:col-span-2">
        <Button size="sm">{submit}</Button>
      </div>
    </form>
  );
}
