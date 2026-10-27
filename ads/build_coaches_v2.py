"""Southline pay-per-result Reel for ONLINE COACHES, v2: opens on a coach who can't get anyone on the phone,
then a mix of effects (dot-matrix, match-cut, phone alerts, sliding steps, floating cards, button CTA).
Teal + coral colour scheme so it looks nothing like the midnight v1. ~26s, 9:16, no voice baked in.
python3 build_coaches_v2.py"""
import adkit as A
import coach_scenes as C

A.set_theme("ocean", accent=(255, 112, 82), accent2=(255, 196, 84), bg=((9, 28, 36), (3, 10, 16)),
            blobs=[(300, 520, 520, (20, 120, 130), 0.5), (850, 1420, 520, (255, 112, 82), 0.22)], grid=False)
v = A.Video()

# 1. opener: ringing prospects, nobody picks up
v.add(*C.scene_unreachable(dur=5.6))

# 2. LED pattern-interrupt
v.add(*A.scene_dot_matrix(["COLD DMs.", "COLD CALLS.", "NO REPLIES."], sub="You chase. They ignore.", dur=2.3, sub_at=0.5))

# 3. the flip, as a match-cut over a blurred page
v.add(*A.scene_match_cut("What if they came to you?", "People who booked a call because they wanted one. "
                         "Not chased. Not cold. Already interested, already on your calendar, ready to talk.",
                         sub="Pay per booked call", dur=2.9))

# 4. the outcome: booked calls landing on his phone
v.add(*A.scene_phone_leads([("Sales call booked", "Sarah · Tue 10:00"), ("Sales call booked", "Marcus · Tue 14:30"),
                            ("Discovery call booked", "Priya · Wed 11:00"), ("Sales call booked", "Dan · Wed 16:00"),
                            ("Strategy call booked", "Emma · Thu 09:30"), ("Sales call booked", "Jordan · Thu 13:00"),
                            ("Sales call booked", "Chloe · Fri 10:30")],
                           app="Your calendar", counter="{n} call{s} booked this week", dur=5.0, interval=0.5))

# 5. how it works, sliding cards with a connector line
v.add(*A.scene_steps([("You cover the ad spend", "Your Meta account, your budget"),
                      ("We run the ads + follow-up", "Facebook, Instagram and email"),
                      ("You pay per booked call", "No retainer. No call, no fee.")], mode="slide", dur=3.3))

# 6. the deal, as floating cards (no price, no guarantee)
v.add(*A.scene_float_cards("The deal", [("MONTHLY RETAINER", "None", "No fee to get started", False),
                                        ("AD SPEND", "Yours", "Your account, your budget", False),
                                        ("OUR FEE", "Per call", "Only when one is booked", True)], dur=3.8))

# 7. CTA: button tap, with the comment / DM routes in the sub-line
v.add(*A.scene_cta_button("Want the breakdown?", "Comment or DM 'CALLS'", "Book a call", "SOUTHLINE",
                          "Link in bio · or comment CALLS and we'll DM you", dur=3.8))

total = v.render("out/southline_coaches_unreachable.mp4", transition="whip", punch=True, drift=0.03,
                 preview_times=[2.6, 5.3, 7.6, 10.5, 15.5, 18.8, 22.4, 26.3])
print(f"rendered {total:.2f}s")
