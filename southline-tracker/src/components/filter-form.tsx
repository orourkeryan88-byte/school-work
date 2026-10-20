"use client";

import { useRouter, usePathname } from "next/navigation";
import { useRef } from "react";

/**
 * A GET form that updates the URL (?channel=sms&...) whenever a field changes,
 * so filters are shareable/bookmarkable and pages stay server-rendered.
 */
export function FilterForm({ children, className }: { children: React.ReactNode; className?: string }) {
  const router = useRouter();
  const path = usePathname();
  const timer = useRef<number | undefined>(undefined);
  function apply(form: HTMLFormElement) {
    const params = new URLSearchParams();
    new FormData(form).forEach((v, k) => {
      if (typeof v === "string" && v) params.set(k, v);
    });
    router.replace(`${path}?${params}`);
  }
  return (
    <form
      className={className}
      onChange={(e) => {
        // Debounce typing in search boxes; apply selects immediately.
        const form = e.currentTarget;
        if ((e.target as unknown as HTMLInputElement).type === "search") {
          clearTimeout(timer.current);
          timer.current = window.setTimeout(() => apply(form), 300);
        } else apply(form);
      }}
      onSubmit={(e) => {
        e.preventDefault();
        apply(e.currentTarget);
      }}
    >
      {children}
    </form>
  );
}
