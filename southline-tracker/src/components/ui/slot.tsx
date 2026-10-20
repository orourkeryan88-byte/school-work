import * as React from "react";
import { cn } from "@/lib/utils";

/** Tiny stand-in for @radix-ui/react-slot: merges props/className into its only child. */
export function Slot({ children, className, ...props }: React.HTMLAttributes<HTMLElement> & { children?: React.ReactNode }) {
  if (!React.isValidElement<{ className?: string }>(children)) return null;
  return React.cloneElement(children, { ...props, className: cn(className, children.props.className) });
}
