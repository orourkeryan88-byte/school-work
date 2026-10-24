"""Southline plumbers ad: 'one builder' angle, volt theme.  python3 build_plumbers.py [--stills]"""
import sys
import adkit as A
import volt_scenes as V

A.set_theme("volt")

LEADS = [("Boiler swap", "Templeogue · combi, no heat"), ("Bathroom refit", "Dundrum · full ensuite"),
         ("Boiler + cylinder", "Terenure · 1930s house"), ("Bathroom refit", "Clontarf · family bathroom"),
         ("Boiler swap", "Churchtown · 3-bed semi")]

SCENES = [
    # 1. Plumbers. If one builder gives you most of your work…
    V.scene_one_builder(dur=3.3),
    # 2. …you're one phone call away from a quiet month.
    V.scene_slam([("YOU'RE ONE|PHONE CALL", "d"), ("AWAY FROM A", "d"), ("QUIET|MONTH.", "dh")], dur=2.6),
    # 3. When he's busy, you're busy. When he goes quiet… so do you.
    V.scene_linked(dur=4.6),
    # 4. And it's worse than that.
    V.scene_slam([("AND IT'S", "d"), ("WORSE|THAN THAT.", "y")], dur=1.6),
    # 5. You work at his price, because he knows you can't say no.
    V.scene_his_price(dur=4.3),
    # 6. But that's not even the worst part…
    V.scene_slam([("BUT THAT'S|NOT EVEN", "d"), ("THE WORST|PART…", "dh")], dur=1.9, lock_last=True),
    # 7. You get paid when he gets paid. If he's slow paying, so are you.
    V.scene_invoice(dur=4.5),
    # 8. So here's the way out.
    V.scene_slam([("SO HERE'S", "d"), ("THE WAY|OUT.", "dh")], dur=1.6, lock_last=True),
    # 9. Get your own homeowners, coming straight to you. Boiler swaps. Bathroom refits. At your price.
    V.scene_own_leads(LEADS, dur=5.4),
    # 10. Try us for fourteen days. No fee, just €300 ad spend. See the leads yourself.
    A.scene_offer("14-DAY TEST DRIVE", "€0 fee", "Just €300 ad spend.", "See the leads yourself.",
                  ["Homeowners straight to you", "Boiler swaps + bathroom refits"], dur=3.9),
    # 11. We're only taking on two plumbers this month. Comment "leads" to learn more.  (first logo)
    A.scene_cta_comment("Only taking on 2", "plumbers this month.", "LEADS", "SOUTHLINE", "Meta ads for Irish plumbers",
                        after="to learn more.", dur=4.4),
]

if "--stills" in sys.argv:  # quick layout QA: a few frames per scene, no encode
    from PIL import Image
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r, (270 * j, 0)) for j, r in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video()
for s in SCENES: v.add(*s)
ends = []; t = 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render("out/southline_plumbers_one_builder.mp4", transition="whip", preview_times=ends)
print(f"rendered {total:.2f}s")
