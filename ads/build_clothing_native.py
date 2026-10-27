"""Southline Reel for CLOTHING BRANDS, 'Black Friday build': everything looks like a phone screen (a note typing the
hook, their inbox filling with competitors' Black Friday emails, the basket flow being built, a flat offer card, a
receipt printing how you pay, a chat CTA). Light, flat, UI-native: nothing like the dark motion-graphic ads.
Offer: basket + welcome + Black Friday emails built and live before Nov 27, no retainer, paid per new subscriber.
~24s, 9:16, no voice baked in.  python3 build_clothing_native.py"""
import adkit as A
import ecom4_scenes as N

A.set_theme("clean", accent=(0, 110, 255), accent2=(120, 60, 255), bg=((247, 247, 250), (236, 238, 244)),
            blobs=[(540, 700, 800, (0, 110, 255), 0.05)], ink=(20, 22, 28), muted=(120, 126, 140), grid=False)
v = A.Video()
v.add(*N.scene_note(dur=3.8))            # 1. hook types itself in Notes
v.add(*N.scene_inbox(dur=4.4))           # 2. their inbox on Black Friday morning: everyone but you
v.add(*N.scene_flow(dur=5.0))            # 3. the basket flow being built, then 'Flow live'
v.add(*N.scene_offer_card(dur=4.0))      # 4. the offer card
v.add(*N.scene_receipt(dur=3.8))         # 5. the receipt: how you pay
v.add(*N.scene_chat(dur=4.0))            # 6. the chat CTA

total = v.render("out/southline_clothing_native.mp4", transition="fade", tr_frames=4, punch=False, drift=0.02,
                 preview_times=[3.5, 7.9, 12.9, 16.9, 20.7, 24.7])
print(f"rendered {total:.2f}s")
