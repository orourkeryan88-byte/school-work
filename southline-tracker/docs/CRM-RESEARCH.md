# What other CRMs do, and what Southline took from them

Short notes from looking at Close, Pipedrive, HubSpot and AI outreach tools (Oct 2026), and how each idea was applied to a one-person agency selling AI receptionists to Irish tradesmen.

| Idea | Who does it | In Southline |
|---|---|---|
| **Pipeline board** that you drag deals across | Pipedrive (its strongest feature) | **Pipeline** page: stages, € values, weighted forecast, win rate |
| **One inbox for calls, SMS and email** | Close (calling, SMS and email built in) | **Responses** + **Reply queue**: email and SendMode SMS in one place |
| **AI that drafts the reply** | Close (AI email drafting), HubSpot Breeze, Reply.io (AI reply handling across channels) | **Reply queue**: Claude drafts every reply in your tone with your offer; you approve |
| **Scores only matter if they drive an action** | Common advice across AI sales tool round-ups | Score reasons are spelled out, and the score orders the reply queue and Today |
| **Speed to lead** | Widely cited: leads contacted within minutes convert far better than leads contacted later | Speed-to-lead stats on Today and Dashboard; the queue shows how long each lead has waited |
| **Command palette / fast search** | Attio, Linear-style CRMs | ⌘K anywhere |
| **Daily "what to do" view** | HubSpot prospecting workspace, Close smart views | **Today**: Claude brief + waiting + hot + due |

## Claude × SendMode: how it works

1. A reply arrives by SendMode, GHL or an email webhook, and Claude tags it (Interested, Question, ...).
2. If the lead is waiting on you, they join the **Reply queue**. Claude drafts the answer from the whole conversation, your offer (`SOUTHLINE_OFFER`) and your booking link (`BOOKING_URL`). Drafts are cached, so each one is paid for once.
3. You read it, tweak it or tap a goal chip to redraft, then press **Approve & send SMS**. SendMode sends it, it goes on the timeline, and the delivery report comes back.

Guard rails, because these are real people's phones:

- **No autopilot**: a human approves every message, and nothing goes out automatically.
- **STOP is final**: "STOP" or "remove me" marks the lead unsubscribed, and the app refuses to text them again. Irish law (S.I. 336/2011, enforced by the Data Protection Commission) requires opt-outs to be honoured, and Sky Ireland was prosecuted in 2024 for texting after an opt-out.
- **Quiet hours**: no texts outside `SMS_SEND_HOURS` / `SMS_SEND_DAYS` (default 9am–8pm, Mon–Sat, Irish time). This isn't a legal requirement, just good manners with tradesmen.
- **SMS cost**: a fada (Seán, Siobhán) switches a text to Unicode, cutting it from 160 to 70 characters per SMS. The meter shows this, and **Remove them** fixes it in one click.

*Consent:* cold texting businesses still needs a lawful basis under the ePrivacy rules. Check this with your adviser; the app doesn't decide it for you.

## Next ideas (not built yet)

- **Ask your CRM**: chat with Claude about the data ("who in Cork asked about price this month?").
- **Sequences from the app**: multi-step SMS/email follow-ups that stop automatically when someone replies.
- **Autopilot for safe cases**, opt-in only: e.g. send the booking link automatically when someone says "yes, book me in", with a daily digest of what was sent.
- **Call logging**: one tap to log call outcomes, and Claude summaries of voice notes.
- **Enrichment**: pull a lead's Google Business profile (reviews, hours, website) to personalise the first message.
