"use client";

import { Flame } from "lucide-react";
import Link from "next/link";
import { useOptimistic, useState, useTransition } from "react";
import { setStatusAction } from "@/app/actions";
import { euro } from "@/lib/crm";
import { STATUS_LABELS, type LeadStatus } from "@/lib/types";

export interface BoardCard {
  id: string;
  name: string;
  business: string | null;
  status: LeadStatus;
  value: number;
  score: number;
  hot: boolean;
  lastActivity: string;
}

const COLUMNS: LeadStatus[] = ["contacted", "replied", "interested", "booked", "won", "lost"];
const MAX_CARDS = 40;

const ago = (iso: string) => {
  const d = Math.floor((Date.now() - Date.parse(iso)) / 864e5);
  return d <= 0 ? "today" : d === 1 ? "yesterday" : `${d}d ago`;
};

/** Kanban pipeline: drag a card to change its stage (or use the menu on phones). */
export function PipelineBoard({ cards }: { cards: BoardCard[] }) {
  const [, start] = useTransition();
  const [dragging, setDragging] = useState<string | null>(null);
  const [over, setOver] = useState<LeadStatus | null>(null);
  const [optimistic, move] = useOptimistic(cards, (state, { id, status }: { id: string; status: LeadStatus }) =>
    state.map((c) => (c.id === id ? { ...c, status } : c)),
  );
  const moveTo = (id: string, status: LeadStatus) =>
    start(async () => {
      move({ id, status });
      await setStatusAction(id, status);
    });

  return (
    <div className="-mx-4 overflow-x-auto px-4 pb-4 sm:-mx-6 sm:px-6">
      <div className="flex min-w-max gap-3">
        {COLUMNS.map((col) => {
          const inCol = optimistic.filter((c) => c.status === col).sort((a, b) => b.score - a.score);
          const total = inCol.reduce((s, c) => s + c.value, 0);
          return (
            <div
              key={col}
              data-stage={col}
              className={`flex w-64 shrink-0 flex-col rounded-xl border transition-colors ${over === col ? "border-brand-accent bg-brand-accent/10" : "bg-muted/40"}`}
              onDragOver={(e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = "move";
                if (over !== col) setOver(col);
              }}
              onDragLeave={() => setOver((o) => (o === col ? null : o))}
              onDrop={(e) => {
                e.preventDefault();
                const id = dragging ?? e.dataTransfer.getData("text/plain");
                setOver(null);
                setDragging(null);
                if (id && optimistic.find((c) => c.id === id)?.status !== col) moveTo(id, col);
              }}
            >
              <div className="flex items-baseline justify-between border-b px-3 py-2.5">
                <span className="text-sm font-semibold">{STATUS_LABELS[col]} <span className="font-normal text-muted-foreground tabular-nums">{inCol.length}</span></span>
                {col !== "lost" && <span className="text-xs text-muted-foreground tabular-nums">{euro(total)}/mo</span>}
              </div>
              <div className="flex max-h-[70vh] flex-col gap-2 overflow-y-auto p-2">
                {inCol.slice(0, MAX_CARDS).map((c) => (
                  <div
                    key={c.id}
                    data-lead={c.id}
                    draggable
                    onDragStart={(e) => {
                      e.dataTransfer.setData("text/plain", c.id);
                      e.dataTransfer.effectAllowed = "move";
                      setDragging(c.id);
                    }}
                    onDragEnd={() => {
                      setDragging(null);
                      setOver(null);
                    }}
                    className="cursor-grab rounded-lg border bg-card p-2.5 shadow-xs active:cursor-grabbing"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <Link href={`/leads/${c.id}`} className="text-sm leading-tight font-medium hover:underline">{c.name}</Link>
                      <span className={`flex shrink-0 items-center gap-0.5 text-[11px] tabular-nums ${c.hot ? "font-semibold text-orange-600 dark:text-orange-400" : "text-muted-foreground"}`} title="Lead score">
                        {c.hot && <Flame className="size-3" />}{c.score}
                      </span>
                    </div>
                    {c.business && <div className="truncate text-xs text-muted-foreground">{c.business}</div>}
                    <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                      <span className="tabular-nums">{euro(c.value)}/mo</span>
                      <span>{ago(c.lastActivity)}</span>
                    </div>
                    {/* Phones can't drag - quick move menu */}
                    <select
                      aria-label="Move to stage"
                      value={c.status}
                      onChange={(e) => moveTo(c.id, e.target.value as LeadStatus)}
                      className="mt-2 w-full rounded border bg-background px-1 py-0.5 text-[11px] text-muted-foreground md:hidden"
                    >
                      {COLUMNS.map((s) => <option key={s} value={s}>Move to: {STATUS_LABELS[s]}</option>)}
                    </select>
                  </div>
                ))}
                {inCol.length > MAX_CARDS && (
                  <Link href={`/leads?status=${col}`} className="py-1 text-center text-xs text-muted-foreground underline">+{inCol.length - MAX_CARDS} more</Link>
                )}
                {!inCol.length && <div className="py-6 text-center text-xs text-muted-foreground">Drop here</div>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
