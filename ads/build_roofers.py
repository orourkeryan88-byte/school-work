"""Southline roofers ad: 'the maths' angle (one re-roof vs forty patch jobs), navy + gold theme, SA logo on the CTA,
timed to the Seán voiceover.  python3 build_roofers.py [--stills | --audio]
Every scene starts on its line and every beat inside a scene lands on its word, using the word timings
in vo_words_roofers_maths.json (ElevenLabs speech-to-text of voice_roofers_maths_take1.mp3)."""
import json, sys
from PIL import Image
import adkit as A
import volt_scenes as V
import maths_scenes as M

A.set_theme("navy")
VOICE = "voice_roofers_maths_take1.mp3"
WORDS = [w for w in json.load(open("vo_words_roofers_maths.json"))["words"] if w.get("type", "word") == "word"]
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
S = [0.0, at("here's the maths") - PRE, at("a slipped slate") - PRE, at("you'd need") - PRE, at("so why are you") - PRE,
     at("the big jobs don't") - PRE, at("so here's what we do") - PRE, at("name number") - PRE, at("try it for") - PRE,
     at("we're only taking") - PRE]
END = WORDS[-1]["end"] + 0.8
S = [round(x * A.FPS) / A.FPS for x in S] + [round(END * A.FPS) / A.FPS]
D = [b - a for a, b in zip(S, S[1:])]
r = lambda i, phrase: at(phrase, S[i] - 0.01) - S[i]  # beat time inside scene i

SCENES = [
    # 0 Roofers… one full re-roof can be worth more than FORTY patch jobs.
    M.scene_scale(dur=D[0], rise_at=r(0, "one full") - 0.05, tip_at=r(0, "40 patch") - 0.05),
    # 1 Here's the maths.
    V.scene_slam([("HERE'S THE|MATHS.", "dh")], dur=D[1], lock_last=True),
    # 2 A slipped slate? €150. A leak in the valley? Maybe €250.  (typical small-job prices, illustrative)
    M.scene_prices([("A SLIPPED SLATE?", "€150"), ("A LEAK IN THE VALLEY?", "€250")], [0.0, r(2, "a leak")],
                   sticker_times=[r(2, "€150") - 0.05, r(2, "€250") - 0.05], dur=D[2]),
    # 3 You'd need forty of them… forty ladders, forty call-outs, forty times up in the rain… just to match ONE re-roof on a three-bed semi.
    M.scene_forty(dur=D[3], fill_from=r(3, "40 of them"), fill_to=r(3, "up in the rain") + 0.3, match_at=r(3, "just to match") - 0.05),
    # 4 So why are you spending your week on the small stuff? Because that's what rings.
    A.scene_dot_matrix(["WHY THE", "SMALL", "STUFF?"], dur=D[4], color=A.TH["accent"], sub="Because that's what rings.",
                       sub_at=r(4, "because that's") - 0.05),
    # 5 The big jobs don't come from luck. They come from being in front of the RIGHT homeowners… the ones already planning a new roof.
    M.scene_targeting(dur=D[5], right_at=r(5, "the right homeowners") - 0.05, planning_at=r(5, "already planning")),
    # 6 So here's what we do. We run Facebook and Instagram ads that go after re-roofs, flat roofs and fascias. Nothing else.
    #   The homeowner fills in their details… and it lands on your phone.
    A.scene_steps([("We run your ads", "Facebook + Instagram, big jobs only"), ("They fill in a form", "Homeowners planning the work"),
                   ("It lands on your phone", "Straight to you, no middleman")],
                  title="Here's what we do", mode="slide", dur=D[6],
                  drops=[r(6, "we run facebook") - 0.1, r(6, "the homeowner fills") - 0.1, r(6, "it lands on") - 0.1]),
    # 7 Name, number, the job. You ring them back.  (example lead)
    M.scene_lead_card([("Name", "Declan K."), ("Number", "087 ••• ••••"), ("The job", "Full re-roof, 3-bed semi")],
                      [r(7, "name"), r(7, "number"), r(7, "the job")], tap_at=r(7, "you ring them") + 0.15, dur=D[7]),
    # 8 Try it for fourteen days. No fee. Just €300 in ad spend… and you see every lead yourself.
    A.scene_float_cards("TRY IT FOR 14 DAYS.", [("TEST DRIVE", "14 days", "See every lead yourself", False),
                                                ("OUR FEE", "€0", "No fee to us", True),
                                                ("AD SPEND", "€300", "Just your ad budget", False)],
                        dur=D[8], times=[r(8, "14 days") - 0.1, r(8, "no fee") - 0.1, r(8, "€300") - 0.1]),
    # 9 We're only taking on two roofers this month. Comment "leads"… and I'll send you the details.  (logo appears here only)
    A.scene_cta_comment("Only taking on 2", "roofers this month.", "LEADS", "SOUTHLINE AGENCY", "Meta ads for Irish roofers",
                        after="for the details.", toast_msg="I'll send you the details", dur=D[9],
                        comment_at=r(9, "comment leads") - 0.05, logo=LOGO),
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
out = "out/southline_roofers_maths_vo.mp4"
total = v.render(out, transition="whip", preview_times=[e - 0.3 for e in S[1:]], voice=VOICE, voice_at=0.0)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s  scene starts {[round(x, 2) for x in S[:-1]]}")
print("voice minus music while speaking (dB): min %.1f, median %.1f" % v.duck_report)
