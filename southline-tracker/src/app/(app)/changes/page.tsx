import { ExternalLink } from "lucide-react";
import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { RequestChange } from "@/components/request-change";
import { Badge } from "@/components/ui/badge";
import { githubConfigured } from "@/lib/adapters/github";
import { getStore } from "@/lib/store";
import { formatDateTime } from "@/lib/utils";

export const metadata: Metadata = { title: "Change requests" };

export default async function ChangesPage() {
  const rows = (await getStore().all("change_requests")).sort((a, b) => b.created_at.localeCompare(a.created_at));
  return (
    <>
      <PageHeader title="Change requests" description={(await githubConfigured()) ? "Features and fixes you've asked Claude for. Each one is a GitHub issue - Claude replies there and opens a pull request." : "GitHub isn't connected yet - requests are saved here. See README → \"Ask Claude to change the app\"."}>
        <div className="w-52"><RequestChange /></div>
      </PageHeader>
      <ul className="divide-y rounded-xl border">
        {rows.map((r) => (
          <li key={r.id} className="flex flex-wrap items-start justify-between gap-3 p-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Badge variant="outline">{r.kind === "bug" ? "Bug" : "Feature"}</Badge>
                <span className="font-medium">{r.title}</span>
              </div>
              <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{r.body}</p>
              <div className="mt-1 text-xs text-muted-foreground">{formatDateTime(r.created_at)}{r.created_by ? ` · ${r.created_by}` : ""}{r.page ? ` · from ${r.page}` : ""}</div>
            </div>
            {r.issue_url ? (
              <a href={r.issue_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sm underline"><ExternalLink className="size-3.5" /> Issue #{r.issue_number}</a>
            ) : (
              <span className="text-xs text-amber-700 dark:text-amber-300" title={r.error ?? ""}>Not sent</span>
            )}
          </li>
        ))}
        {!rows.length && <li className="p-10 text-center text-sm text-muted-foreground">No requests yet. Spot a bug or want a feature? Use “Request a change”.</li>}
      </ul>
    </>
  );
}
