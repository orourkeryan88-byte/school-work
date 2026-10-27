"""Southline pay-per-result Reel for ONLINE COACHES, v3: same unreachable-prospects opener, but the hook is a
correction ('not a leads problem, a retainer problem') followed by a loss-aversion invoice stack, so the viewer feels
the cost of the model they're on before the offer. Built from the research in the chat (correction / contrast /
direct-address hooks, risk reversal). ~29s, 9:16, no voice baked in.
python3 build_coaches_v3.py"""
import adkit as A
import coach_scenes as C

A.set_theme("ocean", accent=(255, 112, 82), accent2=(255, 196, 84), bg=((9, 28, 36), (3, 10, 16)),
            blobs=[(300, 520, 520, (20, 120, 130), 0.5), (850, 1420, 520, (255, 112, 82), 0.22)], grid=False)
v = A.Video()

# 1. opener: ringing prospects, nobody picks up. Hook names the two things they recognise at once.
v.add(*C.scene_unreachable(dur=4.4, calls=((0.7, "No answer"), (1.6, "Voicemail"), (2.5, "Left on seen")),
                           sad_at=3.05, hook=("Empty calendar,", "still paying monthly?"), hook_at=3.2))

# 2. the correction hook
v.add(*A.scene_kinetic([("That's not", "xb", 80, None), ("a leads problem.", "bl", 104, None),
                        ("That's the", "xb", 80, None), ("retainer problem.", "bl", 104, "grad")],
                       underline_line=3, dur=2.6, y0=700))

# 3. loss aversion: invoices pile up, calls stay at zero
v.add(*C.scene_invoices(dur=4.0))

# 4. LED pattern-interrupt
v.add(*A.scene_dot_matrix(["YOU CARRY", "ALL THE RISK."], sub="Not with us.", dur=1.8, sub_at=0.5))

# 5. the flip, as a match-cut over a blurred page
v.add(*A.scene_match_cut("What if the risk was ours?", "You only pay when a sales call is actually booked. "
                         "No retainer. No monthly invoice. If the calendar stays empty, you pay nothing.",
                         sub="Pay per booked call", dur=2.5))

# 6. the outcome: booked calls landing on his phone
v.add(*A.scene_phone_leads([("Sales call booked", "Sarah · Tue 10:00"), ("Sales call booked", "Marcus · Tue 14:30"),
                            ("Discovery call booked", "Priya · Wed 11:00"), ("Sales call booked", "Dan · Wed 16:00"),
                            ("Strategy call booked", "Emma · Thu 09:30"), ("Sales call booked", "Jordan · Thu 13:00"),
                            ("Sales call booked", "Chloe · Fri 10:30")],
                           app="Your calendar", counter="{n} call{s} booked this week", dur=4.2, interval=0.45))

# 7. how it works, sliding cards
v.add(*A.scene_steps([("You cover the ad spend", "Your Meta account, your budget"),
                      ("We run the ads + follow-up", "Facebook, Instagram and email"),
                      ("You pay per booked call", "No retainer. No call, no fee.")], mode="slide", dur=3.0))

# 8. the deal (no price, no guarantee)
v.add(*A.scene_float_cards("The deal", [("MONTHLY RETAINER", "None", "No fee to get started", False),
                                        ("AD SPEND", "Yours", "Your account, your budget", False),
                                        ("OUR FEE", "Per call", "Only when one is booked", True)], dur=3.2))

# 9. CTA
v.add(*A.scene_cta_button("Want the breakdown?", "Comment or DM 'CALLS'", "Book a call", "SOUTHLINE",
                          "Link in bio · or comment CALLS and we'll DM you", dur=3.6))

total = v.render("out/southline_coaches_risk.mp4", transition="whip", punch=True, drift=0.03,
                 preview_times=[4.1, 6.7, 10.7, 12.4, 14.9, 19.0, 22.0, 25.2, 28.9])
print(f"rendered {total:.2f}s")
