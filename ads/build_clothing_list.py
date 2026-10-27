"""Southline Reel for CLOTHING BRANDS, angle B: pay per new subscriber. Opens on a stream of visitors who mostly
leave, corrects it ('you paid for all 100, you keep 2'), flips to keeping their email, subscribers landing on the
phone, how it works, who we are, the deal, button CTA. Dark + lime scheme. ~27s, 9:16, no voice baked in.
python3 build_clothing_list.py"""
import adkit as A
import ecom3_scenes as E
import coach_scenes as C

A.set_theme("lime")
v = A.Video()

# 1. opener: visitors walk past, nearly all leave
v.add(*E.scene_visitors(dur=5.2))

# 2. the correction
v.add(*A.scene_kinetic([("You paid for", "xb", 80, None), ("all 100.", "bl", 120, None),
                        ("You keep", "xb", 80, None), ("2.", "bl", 160, "grad")], underline_line=3, dur=2.4, y0=680))

# 3. the flip
v.add(*A.scene_match_cut("What if you kept their email?", "A visitor who leaves is gone. A subscriber comes back: "
                         "welcome email, browse reminder, basket email, next drop. Every address stays with you.",
                         sub="Pay per new subscriber", dur=2.4))

# 4. subscribers landing on the phone
v.add(*A.scene_phone_leads([("New subscriber", "Emma · 10% off, first order"), ("New subscriber", "Liam · size guide"),
                            ("New subscriber", "Aoife · 10% off, first order"), ("New subscriber", "Noah · early access"),
                            ("New subscriber", "Grace · 10% off, first order"), ("New subscriber", "Jack · next drop")],
                           app="Your email list", counter="{n} new subscriber{s} today", dur=3.6, interval=0.42))

# 5. how it works
v.add(*A.scene_steps([("Ads bring them to the store", "Meta ads, in your own ad account"),
                      ("A popup gets their email", "A small discount for their address"),
                      ("Emails bring them back to buy", "Welcome, browse, basket, next drop")], mode="slide", dur=3.2))

# 6. who's talking, what's for sale
v.add(*C.scene_intro_card(dur=3.4, pills=("Meta ads", "Email"), who="for clothing brands.", pay_line="Paid per new subscriber."))

# 7. the deal (no price)
v.add(*A.scene_float_cards("The deal", [("MONTHLY RETAINER", "None", "No fee to get started", False),
                                        ("YOUR LIST", "Yours", "Every address stays with you", False),
                                        ("OUR FEE", "Per sub", "Only for new subscribers", True)], dur=3.2))

# 8. CTA
v.add(*A.scene_cta_button("Want the numbers for your store?", "Comment or DM 'LIST'", "Book a call", "SOUTHLINE AGENCY",
                          "Meta ads + email for clothing brands · link in bio", dur=3.4))

total = v.render("out/southline_clothing_list.mp4", transition="whip", punch=True, drift=0.03,
                 preview_times=[2.4, 4.9, 7.3, 9.8, 13.3, 16.5, 19.8, 23.0, 26.6])
print(f"rendered {total:.2f}s")
