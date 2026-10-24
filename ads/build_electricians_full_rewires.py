"""Southline Agency - Meta ad for Irish electricians, built around FULL REWIRES (lime theme).
Run from this folder:  python3 build_electricians_full_rewires.py  ->  out/southline_electricians_full_rewires.mp4"""
import os
import adkit as A

A.set_theme("lime")
v = A.Video()

# 01 HOOK - "Electricians," is on screen at full opacity on frame 0, mid-slam
v.add(*A.scene_callout("Electricians,", sub="this is about full rewires.", dur=1.6))
v.add(*A.scene_kinetic([("Homeowners book them", "xb", 88, None), ("every single week.", "xb", 88, None), ("Just not with you.", "bl", 120, "grad")], dur=2.3, y0=720, underline_line=2))

# 02 LEAD
v.add(*A.scene_lead_list([("3 reasons the full rewires", "xb", 80, None), ("skip you.", "bl", 130, "grad")], dur=2.4))

# 03 BODY 1
v.add(*A.unlock_into(A.scene_feed_ad(brand="Brennan Electrical", caption="Full house rewires across South Dublin.", headline="Need a full rewire?", subline="Book a free quote this week",
                                     fields=(("Name", "Sarah K."), ("Phone", "087 ••• ••••"), ("Job", "Full house rewire")), dur=3.7),
                     1, "You're not where they look", "Rewires get planned on the phone at 9pm"))

# 04 OPEN LOOP
v.add(*A.scene_open_loop([("#2 is why you're", "xb", 92, None), ("pricing callouts,", "bl", 104, "grad"), ("not rewires.", "bl", 110, "grad")], nxt="2", dur=2.2))

# 05 BODY 2
v.add(*A.unlock_into(A.scene_phone_leads([("Full house rewire", "Rathfarnham · 3-bed semi"), ("Full rewire + new board", "Terenure · 1930s house"), ("Full house rewire", "Dundrum · moving in March"),
                                          ("Rewire before renovation", "Clonskeagh · extension"), ("Full house rewire", "Churchtown · bungalow")],
                                         app="Rewire leads", icon="bolt", counter=None, cy=1130, dur=3.4, stack_y=560, step=180),
                     2, "You're chasing callouts", "Our ads go after full rewires only"))

# 06 OPEN LOOP
v.add(*A.scene_open_loop([("#3 is why the rewire", "xb", 84, None), ("you quoted Tuesday", "xb", 84, None), ("went to someone else.", "bl", 92, "grad")], nxt="3", dur=2.3))

# 07 BODY 3
v.add(*A.unlock_into(A.scene_race(lead=("New enquiry", "Full house rewire", "Rathfarnham · 3-bed semi"), you=("You", 180, "Rang back 3 hours later"), them=("Another sparky", 4, "Rang back in 4 minutes"),
                                  foot=("Every rewire lead hits your phone", "the second it comes in."), dur=3.7),
                     3, "Slow callbacks", "Whoever rings first gets the rewire"))

# 08 CTA - first time "Southline" appears
v.add(*A.scene_offer("BUILT FOR REWIRES", "10 leads", "in 30 days,", "or we work for free.", ["Ads aimed at full rewires", "Leads straight to your phone"], dur=2.7))
v.add(*A.scene_cta_comment("Only taking on 2", "sparkies this month.", "LEADS", "SOUTHLINE", "Full rewire leads for Irish electricians", after="to learn more.", dur=3.8))

# beat ends (scene starts): 0 1.6 3.9 6.3 11.3 13.5 18.2 20.5 25.5 28.2 32.0
PREVIEW = [0.0, 1.5, 3.7, 6.1, 7.3, 10.9, 13.3, 15.4, 18.0, 19.5, 20.5 + 1.0 + 3.0, 25.4, 28.0, 31.8]
os.makedirs("out", exist_ok=True)
music = dict(music_file="inst.wav", music_start=2.0, sfx_gain=0.75) if os.path.exists("inst.wav") else {}
total = v.render("out/southline_electricians_full_rewires.mp4", preview_times=PREVIEW, **music)
print(f"rendered {total:.1f}s", "with inst.wav" if music else "with the built-in beat")
