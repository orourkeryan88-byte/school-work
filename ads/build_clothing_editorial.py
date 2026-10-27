"""Southline Reel for CLOTHING BRANDS, angle: tired ads ('The Ad Issue'). Fashion-magazine look: cream paper,
Playfair serif, black ink, one red, calm precise motion (rules draw, words rise from masks, ink signs).
Sells Meta ads first; email is mentioned only as the add-on.
Hook: one ad since August, she stopped seeing it. Offer + CTA: a free 15-minute ad review, booked from the link in bio.
~27s, 9:16, no voice baked in.  python3 build_clothing_editorial.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import editorial_scenes as E

A.set_theme("cream", bg=(E.PAPER, E.PAPER), blobs=[], grid=False, ink=E.INK, muted=E.MUTED, accent=E.RED, accent2=E.RED)
E.MAST[:] = ["THE AD ISSUE", "Nº 01 · FOR CLOTHING BRANDS"]

SCENES = [
    E.scene_hook(l1=("One", "ad."), l2=("Since", "August."), l3=("She", "stopped"), l4=("seeing", "it."),
                 note="Clothing brands: when did your ads last change?"),
    E.scene_silence(order=("YOUR AD · LIVE SINCE AUG", "Linen shirt · 'New in'", "1 ad"), tag="Same photo, same words",
                    marks=(("Week 1", 0.0, "new"), ("Week 4", 0.33, "seen it"), ("Week 8", 0.66, "scrolls past"), ("Week 11", 1.0, "ignored")),
                    sub_col=(E.INK, E.MUTED, E.MUTED, E.RED), big=("Same ad.", "Tired feed.")),
    E.scene_quote(lines=("Fashion moves fast.", "So should your ads."), sub="New drop, new season, new ads.", sub2="That's the part we do for you.", size=92),
    E.scene_contents(head="In this issue:", head2="how we run your ads.",
                     rows=(("01", "Fresh ads, made for you", "Make"), ("02", "Tested head to head", "Test"), ("03", "Budget on the winners", "Scale"),
                           ("04", "Show them again", "Retarget"), ("05", "Email to win them back", "Add-on")),
                     by="Meta ads first. Email when you're ready."),
    E.scene_coupon(title=("Meta ads,", "run properly."), stamp_lines=("FREE", "AD REVIEW", "· 15 MIN ·"), foot="Email: optional add-on.",
                   lines=(("We make & run your ads", "fresh creative, tested for you"), ("Your account, your budget", "you see every number"),
                          ("Free 15-min ad review", "we'll show you what we'd change"))),
    E.scene_rsvp(l1="A free ad review.", l2="We'll go through your Meta ads", l3="with you, live. 15 minutes."),
]

if "--stills" in sys.argv:   # quick check: two frames per scene on one sheet
    sheet = Image.new("RGB", (4 * 360, 3 * 640)); k = 0
    for dur, fn, _ in SCENES:
        for x in (dur * 0.55, dur - 0.1): sheet.paste(fn(x)[0].convert("RGB").resize((360, 640)), ((k % 4) * 360, (k // 4) * 640)); k += 1
    sheet.save("out/_stills.png"); sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
total = v.render("out/southline_clothing_editorial.mp4", transition="fade", tr_frames=6, bpm=96, punch=False, drift=0.012,
                 preview_times=[4.4, 9.2, 12.2, 17.5, 22.3, 26.6])
print(f"rendered {total:.2f}s")
