"""Southline pay-per-result Reel for ONLINE COACHES, v4: v3's hook, then it says plainly who's selling and what
(Ryan / Southline Agency / Meta ads + email follow-up / paid per booked call) and spends a scene on what the service
actually includes, with a 'your ad account, your numbers' trust strip. ~30s, 9:16, no voice baked in.
python3 build_coaches_v4.py"""
import adkit as A
import coach_scenes as C

A.set_theme("ocean", accent=(255, 112, 82), accent2=(255, 196, 84), bg=((9, 28, 36), (3, 10, 16)),
            blobs=[(300, 520, 520, (20, 120, 130), 0.5), (850, 1420, 520, (255, 112, 82), 0.22)], grid=False)
v = A.Video()

# 1. opener: ringing prospects, nobody picks up
v.add(*C.scene_unreachable(dur=4.0, calls=((0.6, "No answer"), (1.4, "Voicemail"), (2.2, "Left on seen")),
                           sad_at=2.75, hook=("Empty calendar,", "still paying monthly?"), hook_at=2.85))

# 2. the correction hook
v.add(*A.scene_kinetic([("That's not", "xb", 80, None), ("a leads problem.", "bl", 104, None),
                        ("That's the", "xb", 80, None), ("retainer problem.", "bl", 104, "grad")],
                       underline_line=3, dur=2.3, y0=700))

# 3. who's talking, what's for sale
v.add(*C.scene_intro_card(dur=3.6))

# 4. loss aversion: invoices pile up, calls stay at zero
v.add(*C.scene_invoices(dur=3.4, interval=0.36))

# 5. the flip
v.add(*A.scene_match_cut("What if the risk was ours?", "You only pay when a sales call is actually booked. "
                         "No retainer. No monthly invoice. If the calendar stays empty, you pay nothing.",
                         sub="Pay per booked call", dur=2.3))

# 6. what the service includes + trust strip
v.add(*C.scene_what_we_do([("We write & run your Meta ads", "Facebook + Instagram, in your own ad account"),
                           ("We follow up every lead by email", "So interest turns into a booked call"),
                           ("Calls land on your calendar", "You just show up and sell")], dur=4.2))

# 7. the outcome on his phone
v.add(*A.scene_phone_leads([("Sales call booked", "Sarah · Tue 10:00"), ("Sales call booked", "Marcus · Tue 14:30"),
                            ("Discovery call booked", "Priya · Wed 11:00"), ("Sales call booked", "Dan · Wed 16:00"),
                            ("Strategy call booked", "Emma · Thu 09:30"), ("Sales call booked", "Jordan · Thu 13:00")],
                           app="Your calendar", counter="{n} call{s} booked this week", dur=3.6, interval=0.42))

# 8. the deal (no price, no guarantee)
v.add(*A.scene_float_cards("The deal", [("MONTHLY RETAINER", "None", "No fee to get started", False),
                                        ("AD SPEND", "Yours", "Your account, you see it all", False),
                                        ("OUR FEE", "Per call", "Only when one is booked", True)], dur=3.2))

# 9. CTA
v.add(*A.scene_cta_button("Want the breakdown?", "Comment or DM 'CALLS'", "Book a call", "SOUTHLINE AGENCY",
                          "Meta ads + email for coaches · link in bio", dur=3.4))

total = v.render("out/southline_coaches_trust.mp4", transition="whip", punch=True, drift=0.03,
                 preview_times=[3.7, 6.0, 9.6, 13.1, 15.4, 19.5, 23.0, 26.3, 29.6])
print(f"rendered {total:.2f}s")
