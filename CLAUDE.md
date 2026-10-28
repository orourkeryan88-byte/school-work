# Southline CRM - notes for Claude (the app lives in `southline-tracker/`)

A sales CRM for Southline Agency (Ireland), a one-person business selling AI receptionists to tradesmen and local service businesses. The owner asks for changes in plain English from the app's "Request a change" button. Each request arrives as a GitHub issue. Build exactly what's asked, keep it simple, and explain the change in plain English in the PR. The owner isn't a developer.

## Commands (run from `southline-tracker/`)

- `npm run dev`: local app on mock data (no login unless `APP_USERS` is set)
- `npm test`: unit tests (node:test, `tests/*.test.ts`)
- `npm run typecheck`, `npm run lint`, `npm run build`

All four must pass before you open a PR. Add or update tests for any logic you change.

## Layout

- `src/app/(app)/*`: pages behind the login (Today, Reply queue, Pipeline, Leads, Check number, ...)
- `src/app/actions.ts`: server actions used by buttons
- `src/app/api/*`: webhooks (ingest, GHL, SendMode), CSV import/export, search
- `src/lib/repo.ts`: business logic. `src/lib/crm.ts`: pure CRM maths (score, pipeline, SMS rules)
- `src/lib/ai.ts` + `src/lib/lookup.ts`: Claude calls (model from `ANTHROPIC_MODEL`, default `claude-opus-5-5`)
- `src/lib/store/*`: storage behind one interface (memory/mock or Supabase). Schema changes need a new file in `supabase/migrations/`, plus the type in `src/lib/types.ts`.
- `src/components/ui/*`: shadcn-style components. Use them, and Tailwind tokens from `globals.css`.

## Rules

- Never commit secrets, passwords or `.env.local`. Config goes in env vars, documented in `.env.example` and the README.
- SMS safety is non-negotiable:
  - Never text unsubscribed leads.
  - Respect quiet hours (`sendWindow`).
  - A human approves every outbound message (no autopilot unless the owner explicitly asks for it).
- Keep the Irish context: Europe/Dublin time, +353 numbers, euro.
- Match the existing style: small, commented, readable code. Mobile-friendly, works in dark mode.
- Update the README when behaviour or setup changes.

## Southline's offer (ads, videos and outreach emails)

Ryan's own rules for anything that sells Southline (Reels, ad scripts, cold emails, replies):

- Meta ads (Facebook + Instagram) is the main and only core service. Lead with it every time.
- Email marketing is an upsell, never the headline. Mention it at most once, near the end, as a bonus: "on top of that, we can set up the emails that bring past customers back".
- Clothing / ecommerce brands: the offer is pay per result, meaning the brand pays per sale our ads bring in, no monthly retainer. Never say "pay per lead" or "pay per new subscriber" for clothing brands.
- Coaches: pay per booked sales call (they fund the ad spend).
- Ads run in the client's own ad account, so they see every number.
- Don't invent prices, guarantees or client results.
