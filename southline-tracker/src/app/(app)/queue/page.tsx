import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { ReplyCard } from "@/components/reply-card";
import { sendmodeConfigured } from "@/lib/adapters/sendmode";
import { aiEnabled } from "@/lib/ai";
import { sendWindow } from "@/lib/crm";
import { replyQueue } from "@/lib/repo";

export const metadata: Metadata = { title: "Reply queue" };

// Claude drafts the first few automatically; the rest draft when you click.
const AUTO_DRAFT = 8;

export default async function QueuePage() {
  const queue = await replyQueue();
  const window = sendWindow();
  const smsEnabled = sendmodeConfigured();
  return (
    <>
      <PageHeader
        title="Reply queue"
        description={`${queue.length} people waiting on you · hottest first · ${aiEnabled() ? "Claude drafts every reply" : "template drafts (add ANTHROPIC_API_KEY for Claude)"}`}
      />
      <div className="mb-4 flex flex-wrap gap-2 text-xs">
        <span className={`rounded-md border px-2.5 py-1 ${smsEnabled ? "" : "text-muted-foreground"}`}>SendMode: {smsEnabled ? "connected - approve sends instantly" : "not connected - copy & log instead"}</span>
        <span className={`rounded-md border px-2.5 py-1 ${window.ok ? "" : "border-amber-500/40 text-amber-700 dark:text-amber-300"}`}>{window.ok ? "Inside SMS sending hours" : window.reason}</span>
        <span className="rounded-md border px-2.5 py-1 text-muted-foreground">STOP / unsubscribed leads never appear here</span>
      </div>
      <div className="space-y-4">
        {queue.map((item, i) => (
          <ReplyCard
            key={item.reply.id}
            lead={item.lead}
            reply={item.reply}
            recent={item.messages.slice(-3)}
            score={item.score}
            waitingMinutes={item.waitingMinutes}
            smsEnabled={smsEnabled}
            windowReason={window.ok ? null : window.reason}
            autoDraft={i < AUTO_DRAFT}
          />
        ))}
        {!queue.length && <p className="py-16 text-center text-sm text-muted-foreground">Inbox zero. Nobody is waiting on you.</p>}
      </div>
    </>
  );
}
