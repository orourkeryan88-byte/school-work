"""Southline Reel for CLOTHING BRANDS, angle A: the Black Friday abandoned basket. Opens on a basket being filled
then left at checkout, corrects it ('not lost, unfinished'), shows the email rescue, orders on the phone, who we are,
and a comment/DM CTA. Plum + hot pink scheme. ~25s, 9:16, no voice baked in.
python3 build_clothing_basket.py"""
import adkit as A
import ecom3_scenes as E
import coach_scenes as C

A.set_theme("midnight", accent=(255, 82, 122), accent2=(255, 200, 90), bg=((42, 12, 44), (10, 4, 18)),
            blobs=[(260, 520, 520, (255, 82, 122), 0.30), (860, 1420, 560, (120, 40, 200), 0.35)], card=(34, 22, 44), grid=False)
v = A.Video()

# 1. opener: basket filled, then abandoned
v.add(*E.scene_basket(dur=5.6))

# 2. the correction
v.add(*A.scene_kinetic([("That's not", "xb", 80, None), ("lost revenue.", "bl", 110, None),
                        ("It's just", "xb", 80, None), ("unfinished.", "bl", 120, "grad")], underline_line=3, dur=2.4, y0=700))

# 3. the rescue: three emails, order comes back
v.add(*E.scene_email_rescue(dur=5.2))

# 4. and the ads bring the next basket
v.add(*A.scene_phone_leads([("New order #1044", "Heavy hoodie · €68"), ("New order #1045", "Oversized tee ×2 · €68"),
                            ("New order #1046", "Straight jeans · €59"), ("New order #1047", "Hoodie + tee · €102"),
                            ("New order #1048", "Straight jeans ×2 · €118")],
                           app="Your store", counter="{n} order{s} from one ad", dur=3.4, interval=0.42))

# 5. who's talking, what's for sale
v.add(*C.scene_intro_card(dur=3.4, pills=("Meta ads", "Email flows"), who="for clothing brands.", pay_line="Meta ads + email, done for you."))

# 6. CTA: comment / DM / link
v.add(*A.scene_cta_comment("Black Friday's coming.", "Is your basket flow ready?", "BASKET", "SOUTHLINE AGENCY",
                           "Or DM 'BASKET' · link in bio", after="for the plan.",
                           toast_msg="We'll DM you the plan", dur=4.2))

total = v.render("out/southline_clothing_basket.mp4", transition="whip", punch=True, drift=0.03,
                 preview_times=[2.0, 5.3, 7.7, 12.9, 16.2, 19.6, 24.0])
print(f"rendered {total:.2f}s")
