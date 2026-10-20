# Southline Outreach Tracker

One place to see every cold email and SMS you've sent, who it went to, whether they replied, what they said, and what happened next.

Standalone Next.js app with its own Postgres database (Supabase). It is **not** a GoHighLevel plugin. Data comes in through webhooks, CSV imports and (optionally) API sync, from any sending tool.

- **Responses**: every reply in one table, filtered by channel, tag, status, trade and date. Each reply is tagged automatically. Quick actions on each row: interested, booked, note, follow-up date, AI draft, retag.
- **Dashboard**: sent, replies, reply rate, positive replies, calls booked and deals won, with cold email and SMS side by side, for today / 7d / 30d / custom.
- **Leads**: searchable list. Each lead has one timeline covering both channels: sends, replies, notes, status changes and follow-ups.
- **Follow-ups**: the daily list of people waiting on you, each with a suggested message.
- **Campaigns**: sent / replied / positive / booked / reply rate per campaign, plus A/B variant comparison.
- **AI assist (Claude)**: tags replies, drafts responses in your tone and sums up a lead in 3 lines.
- **Export**: every page has an *Export CSV* button that downloads exactly what you're looking at.
- Dark mode, works on a phone.

---

## 1. Run it locally (2 minutes, no accounts needed)

```bash
cd southline-tracker
npm install
npm run dev        # http://localhost:3000
```

With no env vars set, the app runs in **demo mode**:

- It uses mock data: 70 Irish trades leads across 4 campaigns.
- There's no login.
- Reply tagging uses keyword rules instead of AI.

Anything you change or import in demo mode is saved to `.data/mock-db.json`. Delete that file to reset.

```bash
npm test           # unit tests (matching, ingest, stats, tagging)
npm run typecheck
npm run lint
```

## 2. Go live

### 2a. Supabase (database + login)

1. Create a project at [supabase.com](https://supabase.com) (EU region, e.g. Frankfurt or Ireland).
2. Open **SQL Editor**, then paste and run `supabase/migrations/0001_init.sql`, then `0002_integrations.sql`.
3. Go to **Authentication → Users → Add user**. Create yourself with an email and password. Turn off public sign-ups under **Authentication → Providers → Email**, since this is a one-person app.
4. Go to **Project Settings → API** and copy the URL, the `anon` key and the `service_role` key.

### 2b. Environment variables

Copy `.env.example` to `.env.local` locally, or add these in Vercel → Settings → Environment Variables:

| Variable | Required | What it's for |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | yes | Used for login only |
| `SUPABASE_SERVICE_ROLE_KEY` | yes | Server-side database access. Never expose this to the browser. |
| `ALLOWED_EMAILS` | recommended | Comma-separated list of emails allowed to log in |
| `INGEST_SECRET` | yes (live) | Shared secret for webhooks and sync. Generate one with `openssl rand -hex 24`. |
| `APP_URL` | optional | Your public URL, used to show the right webhook URLs on the Import page |
| `ANTHROPIC_API_KEY` | optional | Turns on Claude for tagging, drafts and summaries. Without it you get rules and templates. |
| `ANTHROPIC_MODEL` | optional | Defaults to `claude-opus-5-5` |
| `GHL_API_KEY` | optional | GoHighLevel Private Integration token. Used to look up contact details for message events. |
| `GHL_LOCATION_ID` | optional | GHL sub-account id, used by *Test connection* |
| `SENDMODE_ACCESS_KEY` | optional | SendMode API access key. Turns on **Send SMS via SendMode** from drafts. |
| `SENDMODE_SENDER_ID` | optional | Sender name or number for texts sent from the app |
| `INSTANTLY_API_KEY` | optional | Enables `/api/sync/instantly` |

Once all three Supabase variables are set, the app switches from mock data to your database, and every page needs a login.

### 2c. Deploy

**Vercel (easiest):**

1. Push this repo to GitHub.
2. At [vercel.com/new](https://vercel.com/new), import the repo and set **Root Directory** to `southline-tracker`.
3. Add the env vars from 2b and deploy.
4. Set `APP_URL` to the URL Vercel gives you, then redeploy so the Import page shows the right webhook URLs.

**Anywhere else:** a `Dockerfile` is included (Railway, Render, Fly.io or a VPS):

```bash
docker build -t southline-tracker .
docker run -p 3000:3000 --env-file .env.local southline-tracker
```

Without Docker, `npm ci && npm run build && npm start` on any Node 20+ host also works.

---

## 3. Connect your tools

All data comes in through two endpoints:

```
POST https://YOUR_APP/api/ingest/email?secret=INGEST_SECRET
POST https://YOUR_APP/api/ingest/sms?secret=INGEST_SECRET
```

- **Secret**: put it in `?secret=`, in an `x-ingest-secret` header, or as `Authorization: Bearer <secret>`.
- **Body**: JSON (one event, an array, or `{ "events": [...] }`), or form-encoded. GET with query params also works, for SMS gateways that forward that way.
- **Optional defaults**: `?direction=inbound|outbound`, `?source=instantly|smartlead|ghl|sendmode` and `?campaign=Name` apply to events that don't say.
- **Duplicates**: an event with a known `id` from the same source is skipped. So is an identical message to the same lead at the same time. Re-sending is safe.
- **Response**: a JSON summary of what was imported, which also shows up on **Import & connect → Import log**.

### Fields the app understands

Field names are matched loosely: case-insensitive, with spaces and dashes treated as `_`, and nested objects like `contact.email` handled.

| Meaning | Accepted names (first match wins) |
|---|---|
| Lead email | `email`, `lead_email`, `contact_email`, `sl_lead_email`. Inbound also checks `from_email` / `from`; outbound checks `to_email` / `to`. |
| Lead phone | `phone`, `mobile`, `msisdn`, `phone_number`, `number`. Inbound also checks `from` / `sender` / `originator`; outbound checks `to` / `recipient`. |
| Message text | `body`, `message`, `text`, `content`, `reply_text`, `reply_message` (or `reply_message.text`), `reply`, `email_body`, `sms` |
| Sent or reply? | `direction`, `type`, `event`, `event_type`, `status`. Anything with *reply / inbound / received* counts as a reply; *sent / outbound / delivered* counts as a send. Otherwise `?direction=` decides, defaulting to *sent*. |
| Name / business | `name`, `first_name` + `last_name`, `company`, `company_name`, `business` |
| Trade / county | `trade`, `industry`, `category` / `county`, `city`, `location` |
| Campaign / variant | `campaign`, `campaign_name`, `sequence` / `variant`, `step`, `sequence_step`, `template` |
| Time | `sent_at`, `timestamp`, `date`, `received_at`, `replied_at`. ISO, unix seconds, or `18/10/2026 14:22`. Times with no timezone are read as Irish time. |
| Unique id | `external_id`, `id`, `message_id`, `email_id`, `sms_id` |

Quoted text is stripped from email replies ("On Mon, X wrote:" and `>` lines).

### How contacts are matched

Every event is matched to an existing lead by **email**, then **phone** (normalised to +353…), then **business name** (case, punctuation and "Ltd" ignored). So a lead who got a cold email and later texted back ends up on **one timeline**. New details like a phone number are added to the lead as they arrive.

### What happens when a reply arrives

1. It's linked to the last message you sent that lead on the same channel. That's the "Message I sent" column.
2. It's tagged as Interested / Not interested / Question / Objection / Out of office / Unsubscribe.
3. The lead's status moves forward automatically: Contacted → Replied → Interested. "No" or STOP sets it to Lost and marks the lead unsubscribed. Automatic changes never move a lead backwards (a new send won't undo *Booked*), and they never touch Won/Lost. You can always set the status by hand.

### Cold email tools

**Instantly**: Settings → Integrations → Webhooks → Add webhook

- URL: `https://YOUR_APP/api/ingest/email?secret=…&source=instantly`
- Events: *Email sent* and *Reply received*. Instantly's `event_type` values (`email_sent`, `reply_received`) are detected automatically.
- Optional backfill: set `INSTANTLY_API_KEY` and call `POST /api/sync/instantly?secret=…` from a cron (e.g. Vercel Cron or cron-job.org, every 30 min). It pulls recent emails from Instantly's v2 API and skips anything already imported. Keep `source=instantly` on the webhook URL so webhook and sync events dedupe against each other. *This adapter couldn't be tested against a live Instantly account. If Instantly changes its field names, rows are skipped and logged rather than imported wrongly.*

**Smartlead**: Campaign → Settings → Webhooks (or Settings → Webhooks for all campaigns)

- URL: `https://YOUR_APP/api/ingest/email?secret=…&source=smartlead`
- Events: `EMAIL_SENT`, `EMAIL_REPLY`. Fields like `sl_lead_email`, `reply_message.text` and `campaign_name` are understood.

**GoHighLevel**: see [GoHighLevel integration](#gohighlevel-integration) below.

**Any other tool**: send at least an email address and a message body. Or export a CSV.

### GoHighLevel integration

Endpoint: `POST https://YOUR_APP/api/integrations/ghl?secret=INGEST_SECRET`. It takes two kinds of GHL webhook. Use either, or both.

**Option A: Private Integration webhooks (recommended, catches every email and SMS automatically)**

1. In GHL go to **Settings → Private Integrations → Create new integration**.
2. Give it the scopes `contacts.readonly` and `conversations/message.readonly`. Copy the token into `GHL_API_KEY`, and your sub-account id into `GHL_LOCATION_ID`.
3. In the integration's **Webhooks** section, set the URL to `https://YOUR_APP/api/integrations/ghl?secret=…` and subscribe to **InboundMessage** and **OutboundMessage**.
   - If your GHL plan doesn't show webhooks on Private Integrations, use a Marketplace app with the same two events, or use Option B.

What happens to each event:
- `messageType` SMS is logged as SMS, and Email as cold email. Calls, chats and other message types are ignored and still answered with 200, so GHL doesn't retry them.
- These events carry a `contactId` but often no email address. When `GHL_API_KEY` is set, the app fetches the contact (name, email, phone, company) from the GHL API.
- Each lead stores its GHL contact id, so later events for that contact always land on the same timeline, even without an email or phone.

**Option B: Workflow webhooks (no API key needed)**

Create a workflow per event, each with a **Webhook** action. The URL decides the channel and direction:

| Workflow trigger | Webhook URL |
|---|---|
| Email sent (or your campaign's send step) | `…/api/integrations/ghl?secret=…&channel=email&direction=outbound` |
| Customer replied, channel Email | `…/api/integrations/ghl?secret=…&channel=email&direction=inbound` |
| SMS sent | `…/api/integrations/ghl?secret=…&channel=sms&direction=outbound` |
| Customer replied, channel SMS | `…/api/integrations/ghl?secret=…&channel=sms&direction=inbound` |

GHL sends the contact's standard fields automatically (`contact_id`, `full_name`, `email`, `phone`, `company_name`). Under **Custom Data**, add:

- `message`: the message body. Use the reply-text custom value for reply triggers.
- optionally `campaign`, `variant`, `trade` and `county`.

**Test connection**: with the API key set, there's a button for it on **Import & connect**.

### SendMode integration

All three parts are set up in the SendMode portal under **Settings → API Settings**.

1. **Replies (incoming SMS).** Set the incoming SMS forwarding URL to

   ```
   https://YOUR_APP/api/integrations/sendmode/inbound?secret=INGEST_SECRET
   ```

   It accepts GET, form posts or JSON, and needs the sender's number (`from` / `sender` / `originator` / `msisdn` / `phone`) and the text (`message` / `text` / `body`). It answers `True` when the reply is saved. If a field isn't recognised it answers `False: <reason>` with a 422, and the same reason shows in the **Import log**.

2. **Delivery reports.** Set **Post Delivery Reports to URL** to

   ```
   https://YOUR_APP/api/integrations/sendmode/delivery?secret=INGEST_SECRET
   ```

   SendMode posts `EventID`, `Phonenumber`, `Status` and `CustomerID`. For texts sent from this app, the status (e.g. *delivered*) appears next to the message on the lead's timeline. The endpoint always answers `True`, as SendMode requires.

3. **Send SMS from the app.** Create an API access key and set `SENDMODE_ACCESS_KEY` (plus `SENDMODE_SENDER_ID`).
   - SMS drafts on the inbox, lead page and follow-up queue then get a **Send SMS via SendMode** button. It asks for confirmation before sending.
   - It uses SendMode's REST API (`POST https://rest.sendmode.com/v2/send`) and logs the text on the lead's timeline.
   - It refuses to text leads who have unsubscribed (replied STOP).
   - **Test connection** on **Import & connect** checks the key and shows your credit balance.

**Bulk blasts** still run from SendMode itself. Export the sent report after each blast and import it as CSV (channel *SMS*, rows *Messages I sent*), so the dashboard counts them.

### CSV import

Go to **Import & connect → CSV import**:

1. Pick the channel and whether the rows are *sends* or *replies*.
2. Optionally pick a default campaign.
3. Upload the file.

Column names are matched with the same rules as the webhook fields above. A file can mix sends and replies if it has a `direction`/`type`/`status` column. Re-importing the same file creates no duplicates. Sample files are in `public/samples/`.

Test it with curl:

```bash
curl -X POST "http://localhost:3000/api/ingest/sms?direction=inbound" \
  -d "from=0871234567&message=Yeah go on, how much is it?"
```

---

## 4. AI assist

With `ANTHROPIC_API_KEY` set, Claude (`claude-opus-5-5` by default):

- **Tags each reply** as it arrives (structured JSON output, so it's always one of the six tags). Use *Re-tag* to run it again, or pick the tag by hand.
- **Drafts replies and follow-ups** in your tone: short, direct, Irish market, SMS under 300 characters. Edit the draft, copy it, send it from your normal tool, then press **Log as sent** so it lands on the timeline.
- **Summarises a lead** in 3 lines: who they are, where the conversation stands, and the next step.

Calls run at low effort to keep them quick and cheap. Server-side fallback is enabled (`fallbacks: "default"`), so if the model declines a request, the API retries on Anthropic's recommended fallback model.

Without a key, tagging uses keyword rules (`src/lib/ai.ts`), drafts use templates, and summaries are built from the data. Everything still works.

To change your tone of voice, edit `TONE` in `src/lib/ai.ts`.

## 5. Follow-up queue rules

The Follow-ups page lists:

1. Follow-ups you scheduled that are due today or overdue.
2. Leads who **replied or are interested** and are waiting on you, or who haven't answered your last message in 2+ days.
3. In a collapsible "No reply yet" section: leads you sent exactly one message 4–30 days ago with no reply. Leads with more sends are left out, because your sequence tool is probably already nudging them.

Use **Done** to clear an item, or **+2 days / +1 week** to snooze it.

## 6. How the numbers are calculated

- **Sent / replies**: messages in the date range.
- **Reply rate**: unique leads who replied ÷ unique leads contacted in the range.
- **Positive**: replies tagged *Interested*.
- **Calls booked / deals won**: leads marked Booked/Won during the range. Each is credited to the channel the lead first replied on, so email + SMS always add up to the total.
- **Campaign variants**: compared on first-touch messages only. Messages with "follow" in the variant name are excluded.

## Project layout

```
src/
  app/                    pages (dashboard, inbox, leads, follow-ups, campaigns, import, login)
    actions.ts            server actions behind the quick-action buttons
    api/ingest/[channel]  POST /api/ingest/email | /api/ingest/sms
    api/import            CSV upload
    api/export            CSV download for every view
    api/integrations/     GoHighLevel + SendMode (inbound, delivery reports)
    api/sync/[source]     optional API pull (instantly)
  components/             UI (shadcn/ui-style components in components/ui)
  lib/
    types.ts              data model
    repo.ts               business logic: matching, ingest, status rules, read models
    ingest.ts             payload/CSV field mapping (the "adapters")
    importer.ts           shared import pipeline + import log
    stats.ts              dashboard & campaign numbers (pure functions)
    ai.ts                 Claude calls + rule/template fallbacks
    adapters/             ghl.ts, sendmode.ts, instantly.ts
    store/                memory (mock) and Supabase storage behind one interface
supabase/migrations/      database schema
tests/                    unit tests (node:test)
```

**Data model**: Lead, Message (channel, direction, body, timestamp, campaign, variant, reply link, AI tag), Campaign, Note (manual notes and status changes, for the timeline), FollowUp, ImportLog.

**Scale**: queries load whole tables and aggregate in code. That's simple and fast for a solo operator, up to tens of thousands of messages. Past that, move the aggregations in `stats.ts` into SQL views.

**shadcn/ui**: the components in `src/components/ui` follow shadcn's structure and `components.json` is set up, so `npx shadcn add <component>` works for adding more.
