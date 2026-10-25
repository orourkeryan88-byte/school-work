"""Southline roofers SILENT ad (~24s, no voiceover): 'ghosted after the quote'. Hook -> open loop -> reveal -> flip.
Black + safety-orange 'hazard' theme, SA logo on the CTA only. On-screen type carries the whole message.
python3 build_roofers_ghost.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import volt_scenes as V
import maths_scenes as M
import ghost_scenes as G

A.set_theme("hazard")
LOGO = Image.open("brand/southline_logo_badge.png").convert("RGBA")

SCENES = [
    # 1 HOOK  quote sent -> Seen 21:04 -> typing… -> gone -> Tue, Wed, Thu, Fri -> …AND THEN NOTHING.
    G.scene_ghosted(dur=3.7),
    # 2 OPEN LOOP  the question they need answered (paid off by scene 3)
    V.scene_slam([("WHY DO THEY|GO QUIET?", "d"), ("IT'S NOT|YOUR PRICE.", "dh"), ("IT'S THIS:", "y")], dur=3.0, cuts=[0.0, 1.1, 2.15], stagger=0.07),
    # 3 REVEAL  their 'can anyone recommend a roofer?' post; 47 comments bury yours  (illustrative)
    G.scene_group_post(dur=4.6),
    # 4 THE POINT
    V.scene_slam([("THEY WEREN'T|LOOKING FOR YOU.", "d"), ("THEY WERE|SHOPPING.", "dh")], dur=2.5, cuts=[0.0, 1.25], lock_last=True, stagger=0.07),
    # 5 FLIP
    V.scene_slam([("WHAT IF THEY", "d"), ("ASKED FOR|YOU?", "y")], dur=1.6, cuts=[0.0, 0.55], stagger=0.07),
    # 6 the enquiry you want: they found your ad and asked for you  (example lead)
    M.scene_lead_card([("From", "Aoife M."), ("Found you via", "Your ad"), ("Message", "Can you ring me?")], [0.3, 0.65, 1.0],
                      tap_at=1.85, dur=2.9, title="New enquiry", job_tag="ASKED FOR YOU"),
    # 7 OFFER
    A.scene_offer("14-DAY TEST DRIVE", "€0 fee", "Just €300 ad spend.", "See every lead yourself.",
                  ["Homeowners asking for YOU", "Leads straight to your phone"], dur=3.0),
    # 8 CTA  (logo appears here only)
    A.scene_cta_comment("Only taking on 2", "roofers this month.", "LEADS", "SOUTHLINE AGENCY", "Meta ads for Irish roofers",
                        after="for the details.", toast_msg="I'll send you the details", dur=3.6, comment_at=0.4, logo=LOGO),
]

if "--stills" in sys.argv:  # quick layout QA: a few frames per scene, no encode
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video()
for s in SCENES: v.add(*s)
out = "out/southline_roofers_ghosted.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="whip", preview_times=ends, punch=True, drift=0.035)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s")
