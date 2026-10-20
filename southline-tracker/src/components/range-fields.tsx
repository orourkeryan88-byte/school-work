"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { NativeSelect } from "@/components/ui/select";

/** Date filter: Today / 7d / 30d / All / Custom (shows from-to pickers). Lives inside a FilterForm. */
export function RangeFields({ range, from, to, defaultRange = "30d" }: { range?: string; from?: string; to?: string; defaultRange?: string }) {
  const [value, setValue] = useState(range || defaultRange);
  return (
    <>
      <NativeSelect name="range" aria-label="Date range" value={value} onChange={(e) => setValue(e.target.value)}>
        <option value="today">Today</option>
        <option value="7d">Last 7 days</option>
        <option value="30d">Last 30 days</option>
        <option value="all">All time</option>
        <option value="custom">Custom…</option>
      </NativeSelect>
      {value === "custom" && (
        <>
          <Input type="date" name="from" defaultValue={from} aria-label="From" className="w-38" />
          <Input type="date" name="to" defaultValue={to} aria-label="To" className="w-38" />
        </>
      )}
    </>
  );
}
