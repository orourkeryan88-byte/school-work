"use client";

import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { NAV } from "@/components/nav";

type Hit = { id: string; name: string; sub: string; status: string };

/** ⌘K / Ctrl+K: jump to any lead or page. */
export function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);
  const [active, setActive] = useState(0);
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (open) setTimeout(() => input.current?.focus(), 0);
    else setQ("");
  }, [open]);

  useEffect(() => {
    if (q.trim().length < 2) {
      setHits([]);
      return;
    }
    const t = setTimeout(async () => {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      if (res.ok) setHits((await res.json()).leads);
      setActive(0);
    }, 150);
    return () => clearTimeout(t);
  }, [q]);

  const pages = NAV.filter((n) => !q || n.label.toLowerCase().includes(q.toLowerCase()));
  const items = [...hits.map((h) => ({ key: h.id, label: h.name, sub: `${h.sub}${h.sub ? " · " : ""}${h.status}`, href: `/leads/${h.id}` })), ...pages.map((p) => ({ key: p.href, label: p.label, sub: "Go to page", href: p.href }))];
  const go = (href: string) => {
    setOpen(false);
    router.push(href);
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex size-8 items-center justify-center gap-2 rounded-md text-sm text-muted-foreground hover:bg-accent sm:h-8 sm:w-64 sm:justify-start sm:border sm:bg-background sm:px-2.5"
        aria-label="Search"
      >
        <Search className="size-4" />
        <span className="hidden sm:inline">Search leads…</span>
        <kbd className="ml-auto hidden rounded border bg-muted px-1.5 text-[10px] sm:inline">⌘K</kbd>
      </button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 p-4 pt-[12vh]" onClick={() => setOpen(false)}>
          <div className="w-full max-w-lg overflow-hidden rounded-xl border bg-popover shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center gap-2 border-b px-3">
              <Search className="size-4 text-muted-foreground" />
              <input
                ref={input}
                value={q}
                onChange={(e) => setQ(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "ArrowDown") setActive((a) => Math.min(a + 1, items.length - 1));
                  if (e.key === "ArrowUp") setActive((a) => Math.max(a - 1, 0));
                  if (e.key === "Enter" && items[active]) go(items[active].href);
                }}
                placeholder="Name, business, phone, county…"
                className="h-12 flex-1 bg-transparent text-sm outline-none"
              />
            </div>
            <ul className="max-h-80 overflow-y-auto p-1">
              {items.map((it, i) => (
                <li key={it.key}>
                  <button onMouseEnter={() => setActive(i)} onClick={() => go(it.href)} className={`flex w-full flex-col items-start rounded-md px-3 py-2 text-left ${i === active ? "bg-accent" : ""}`}>
                    <span className="text-sm">{it.label}</span>
                    <span className="text-xs text-muted-foreground">{it.sub}</span>
                  </button>
                </li>
              ))}
              {!items.length && <li className="px-3 py-6 text-center text-sm text-muted-foreground">No matches</li>}
            </ul>
          </div>
        </div>
      )}
    </>
  );
}
