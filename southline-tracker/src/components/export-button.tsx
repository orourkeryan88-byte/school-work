import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";

/** Downloads the current view as CSV, passing the page's filters through. */
export function ExportButton({ view, params }: { view: string; params?: Record<string, string | undefined> }) {
  const qs = new URLSearchParams({ view });
  for (const [k, v] of Object.entries(params ?? {})) if (v) qs.set(k, v);
  return (
    <Button variant="outline" size="sm" asChild>
      <a href={`/api/export?${qs}`}>
        <Download /> Export CSV
      </a>
    </Button>
  );
}
