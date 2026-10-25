"""Southline roofers ad: 'storm season' angle, navy + gold theme, SA logo on the CTA, timed to the Seán voiceover.
python3 build_roofers.py [--stills | --audio]
Every scene starts on its line and every beat inside a scene lands on its word, using the word timings
in vo_words_roofers_take1.json (ElevenLabs speech-to-text of voice_roofers_take1.mp3)."""
import json, sys
from PIL import Image
import adkit as A
import volt_scenes as V
import roofer_scenes as R

A.set_theme("navy")
VOICE = "voice_roofers_take1.mp3"
WORDS = [w for w in json.load(open("vo_words_roofers_take1.json"))["words"] if w.get("type", "word") == "word"]
LOGO = Image.open("brand/southline_logo_badge.png").convert("RGBA")
PRE = 0.08  # visuals land a hair before the word so the whip-in has cleared


def at(phrase, after=0.0):
    """start time of the first occurrence of phrase (lower-case words, punctuation ignored) at or after `after` seconds"""
    clean = lambda s: "".join(c for c in s.lower() if c.isalnum() or c == "'")
    want = [clean(p) for p in phrase.split()]; ws = [clean(w["text"]) for w in WORDS]
    for i in range(len(ws) - len(want) + 1):
        if ws[i:i + len(want)] == want and WORDS[i]["start"] >= after: return WORDS[i]["start"]
    raise KeyError(phrase)


# scene starts: each on the first word of its line
S = [0.0, at("if you're up a ladder") - PRE, at("and the big jobs") - PRE, at("this is for you") - PRE, at("storm hits") - PRE,
     at("and here's the part") - PRE, at("the homeowner who") - PRE, at("his work isn't") - PRE, at("so what if") - PRE,
     at("that's exactly") - PRE, at("fourteen days") - PRE, at("we're only taking") - PRE]
END = WORDS[-1]["end"] + 0.8
S = [round(x * A.FPS) / A.FPS for x in S] + [round(END * A.FPS) / A.FPS]
D = [b - a for a, b in zip(S, S[1:])]
r = lambda i, phrase: at(phrase, S[i] - 0.01) - S[i]  # beat time inside scene i

LEADS = [("Full re-roof", "Rathfarnham · 1960s semi"), ("Flat roof", "Clontarf · kitchen extension"),
         ("Fascias + soffits", "Lucan · 4-bed detached"), ("Full re-roof", "Malahide · bungalow"),
         ("Flat roof", "Drumcondra · garage conversion")]

SCENES = [
    # 0 Roofers. If your phone only rings after a storm…
    R.scene_storm_calls(dur=D[0], flash_at=r(0, "after a storm") - 0.05, rise_at=r(0, "if your phone") - 0.05),
    # 1 if you're up a ladder in the rain, fixing slipped slates for a hundred and fifty euro…  (illustrative small jobs)
    R.scene_patch_jobs([("Slipped slates", "Crumlin · front pitch", 150), ("Leaking flashing", "Walkinstown · chimney", 180),
                        ("Blocked gutter", "Tallaght · semi-d", 90)],
                       [r(1, "slipped slates") - 0.3, r(1, "€150") + 0.2, r(1, "€150") + 0.7], dur=D[1]),
    # 2 and the BIG jobs — full re-roofs, flat roofs, fascias and soffits — are going to someone else…
    R.scene_big_jobs_gone([("Full re-roof", "The whole roof, start to finish"), ("Flat roof", "Extensions, garages, dormers"),
                           ("Fascias + soffits", "The full front of the house")],
                          [r(2, "full re-roofs") - 0.1, r(2, "flat roofs") - 0.1, r(2, "fascias and soffits") - 0.1],
                          gone_at=r(2, "going to someone") - 0.05, dur=D[2]),
    # 3 this is for you.
    V.scene_slam([("THIS IS|FOR YOU.", "dh")], dur=D[3], lock_last=True),
    # 4 Storm hits? You're flat out for a week. Then the weather clears… and so does your diary.
    R.scene_storm_diary(dur=D[4], clear_at=r(4, "then the weather") - 0.05, drain_at=r(4, "so does your diary") - 0.05,
                        step_a=r(4, "you're flat out") - 0.05, step_b=r(4, "and so does") - r(4, "then the weather")),
    # 5 And here's the part that stings.
    V.scene_slam([("AND HERE'S|THE PART", "d"), ("THAT|STINGS.", "dh")], dur=D[5], cuts=[0.0, r(5, "that stings")]),
    # 6 The homeowner who needed a whole new roof? They never rang you. They saw the other lad's ad on Facebook.
    R.scene_feed_steal(dur=D[6], never_at=r(6, "they never rang") - 0.05, tap_at=r(6, "ad on facebook")),
    # 7 His work isn't better. He's just SEEN.
    V.scene_slam([("HIS WORK|ISN'T BETTER.", "d"), ("HE'S JUST|SEEN.", "dh")], dur=D[7], lock_last=True, cuts=[0.0, r(7, "he's just")]),
    # 8 So what if every week, homeowners were ringing YOU… for the big jobs? Re-roofs. Flat roofs. Fascias and soffits. Booked in, rain or shine.
    V.scene_own_leads(LEADS, dur=D[8], lines=(("HOMEOWNERS", False), ("RINGING YOU.", True)), icon="house",
                      tag="RE-ROOFS · FLAT ROOFS · FASCIAS", tag_at=r(8, "re-roofs") - 0.05,
                      lt=[r(8, "homeowners were"), r(8, "ringing you") + 0.2, r(8, "re-roofs"), r(8, "flat roofs"), r(8, "fascias and soffits")],
                      price_at=r(8, "rain or shine") - 0.05, price_txt="RAIN OR SHINE."),
    # 9 That's exactly what we set up for you.
    V.scene_slam([("THAT'S EXACTLY|WHAT WE", "d"), ("SET UP|FOR YOU.", "y")], dur=D[9], cuts=[0.0, r(9, "set up")]),
    # 10 Fourteen days. No fee. Just €300 ad spend. See the leads yourself.
    A.scene_offer("14-DAY TEST DRIVE", "€0 fee", "Just €300 ad spend.", "See the leads yourself.",
                  ["Homeowners ringing you direct", "Re-roofs, flat roofs, fascias"], dur=D[10]),
    # 11 We're only taking on two roofers this month. Comment "leads" and we'll send you the details.  (logo appears here only)
    A.scene_cta_comment("Only taking on 2", "roofers this month.", "LEADS", "SOUTHLINE AGENCY", "Meta ads for Irish roofers",
                        after="for the details.", toast_msg="We'll send you the details", dur=D[11],
                        comment_at=r(11, "comment leads") - 0.05, logo=LOGO),
]

if "--audio" in sys.argv:  # soundtrack only, for checking the mix
    v = A.Video(); [v.add(*s) for s in SCENES]
    v.render("out/audio_check.m4a", voice=VOICE, audio_only=True)
    print("voice minus music while speaking (dB): min %.1f, median %.1f" % v.duck_report); sys.exit()

if "--stills" in sys.argv:  # quick layout QA: a few frames per scene, no encode
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video()
for s in SCENES: v.add(*s)
out = "out/southline_roofers_storm_vo.mp4"
total = v.render(out, transition="whip", preview_times=[e - 0.3 for e in S[1:]], voice=VOICE, voice_at=0.0)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s  scene starts {[round(x, 2) for x in S[:-1]]}")
print("voice minus music while speaking (dB): min %.1f, median %.1f" % v.duck_report)
