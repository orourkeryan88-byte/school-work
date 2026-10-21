// Menu items, shared by the sidebar, the phone tab bar, the More page and ⌘K search.
// (A plain module, not a client component, so server pages can read it too.)
import { BarChart3, CalendarClock, Columns3, Inbox, KeyRound, Megaphone, PhoneCall, Sparkles, Sun, Upload, Users, Wand2 } from "lucide-react";

/** The four things used every day - the only items in the menu. */
export const MAIN_NAV = [
  { href: "/", label: "Today", icon: Sun },
  { href: "/queue", label: "Replies", icon: Sparkles },
  { href: "/leads", label: "Leads", icon: Users },
  { href: "/check", label: "Check number", icon: PhoneCall },
];

/** Everything else lives on the More page. */
export const MORE_NAV = [
  { href: "/follow-ups", label: "Follow-ups", icon: CalendarClock, hint: "Who to chase today, with a suggested message" },
  { href: "/pipeline", label: "Pipeline board", icon: Columns3, hint: "Your deals by stage, with € values" },
  { href: "/inbox", label: "All replies", icon: Inbox, hint: "Every reply ever received, with filters" },
  { href: "/dashboard", label: "Stats", icon: BarChart3, hint: "Sent, replies, reply rate, bookings - email vs SMS" },
  { href: "/campaigns", label: "Campaigns", icon: Megaphone, hint: "How each campaign and message version is doing" },
  { href: "/import", label: "Import & connect", icon: Upload, hint: "CSV import, GHL and SendMode setup" },
  { href: "/keys", label: "API keys", icon: KeyRound, hint: "Paste your SendMode, GHL and Claude keys" },
  { href: "/changes", label: "Change requests", icon: Wand2, hint: "Features and fixes you've asked Claude for" },
];

/** Every page, for ⌘K search. */
export const NAV = [...MAIN_NAV, ...MORE_NAV];

