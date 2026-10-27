"""Southline pay-per-result Reel for ONLINE COACHES and course creators (9:16, ~24s, no voice baked in).
Offer confirmed by Ryan: they fund the ad spend, Southline is paid per booked sales call, no retainer.
CTA covers all three routes: comment CALLS, DM CALLS, or the booking link in bio.
python3 build_coaches.py"""
import adkit as A

A.set_theme("midnight")
v = A.Video()

# 1. callout: who it's for
v.add(*A.scene_callout("Coaches,", sub="and course creators…", dur=1.8))

# 2. pain hook
v.add(*A.scene_kinetic([("Paying a retainer", "bl", 104, None), ("every month…", "bl", 104, None),
                        ("and still staring at", "xb", 70, None), ("an empty calendar?", "bl", 96, "grad")],
                       underline_line=3, dur=3.2))

# 3. the flip
v.add(*A.scene_kinetic([("What if you only paid", "xb", 72, None), ("when a call", "bl", 124, "grad"),
                        ("actually gets booked?", "bl", 88, None)], underline_line=1, dur=2.8, y0=700))

# 4. the outcome: calls landing in the calendar
CALLS = ["Sales call", "Discovery", "Strategy call", "Sales call", "Discovery",
         "Sales call", "Strategy call", "Discovery", "Sales call", "Discovery"]
v.add(*A.scene_diary(CALLS, title="Your next 2 weeks", done_label="Booked calls: {n}", dur=5.0))

# 5. how it works
v.add(*A.scene_steps([("You cover the ad spend", "Your Meta account, your budget"),
                      ("We run the ads + follow-up", "Facebook, Instagram and email"),
                      ("You pay per booked call", "No retainer. No call, no fee.")], dur=3.4))

# 6. offer card (no price, no guarantee: those stay for the call)
v.add(*A.scene_offer("PAY PER RESULT", "No retainer", "You fund the ad spend.", "We're paid per call booked.",
                     ["Sales calls on your calendar", "Built for coaches & creators"], dur=3.8))

# 7. CTA: comment / DM / link in bio
v.add(*A.scene_cta_comment("Want the breakdown?", "Comment, DM or tap the link.", "CALLS", "SOUTHLINE",
                           "Or DM 'CALLS' · booking link in bio", after="and we'll send it over.", dur=4.4))

total = v.render("out/southline_coaches_ppr.mp4", transition="whip", punch=True, drift=0.03,
                 preview_times=[1.5, 4.7, 7.5, 12.5, 15.9, 19.7, 24.0])
print(f"rendered {total:.2f}s")
