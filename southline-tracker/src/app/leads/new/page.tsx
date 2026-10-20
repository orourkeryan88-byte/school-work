import { createLeadAction } from "@/app/actions";
import { LeadForm } from "@/components/lead-form";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent } from "@/components/ui/card";

export default function NewLeadPage() {
  return (
    <>
      <PageHeader title="Add lead" description="If the email, phone or business already exists, the details are merged into that lead." />
      <Card className="max-w-2xl">
        <CardContent>
          <LeadForm action={createLeadAction} submit="Add lead" />
        </CardContent>
      </Card>
    </>
  );
}
