import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { ReplyCard } from "@/components/reply-card";
import { sendmodeConfigured } from "@/lib/adapters/sendmode";
import Link from "next/link";
import { sendWindow } from "@/lib/crm";
import { replyQueue } from "@/lib/repo";

export const metadata: Metadata = { title: "Replies" };

// Claude drafts the first few automatically; the rest draft when you click.
const AUTO_DRAFT = 8;

export default async function QueuePage() {
  const queue = await replyQueue();
  const window = sendWindow();
  const smsEnabled = sendmodeConfigured();
  return (
    <>
      <PageHeader
        title="Replies"
        description={queue.length ? `${queue.length} ${queue.length === 1 ? "person is" : "people are"} waiting on you. Hottest first - check the draft, then send.` : undefined}
      >
        <Link href="/inbox" className="text-sm text-muted-foreground underline">All replies</Link>
      </PageHeader>
      {!window.ok && <p className="mb-4 rounded-lg bg-amber-500/10 px-3 py-2 text-sm text-amber-800 dark:text-amber-200">{window.reason}. Texts can be sent again in the morning.</p>}
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
