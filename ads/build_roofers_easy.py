"""Southline roofers ad: 'easy to find' angle (new hook, open question, body 1), navy + gold, SA logo on the CTA.
python3 build_roofers_easy.py [--stills | --audio]
With voice_roofers_easy.mp3 + vo_words_roofers_easy.json present, every scene lands on its spoken word.
Without them (no voiceover recorded yet) the timing comes from an estimate of Seán's pace and the render has
music + SFX only, so the on-screen type carries the script."""
import json, os, re, sys
from PIL import Image
import adkit as A
import volt_scenes as V
import maths_scenes as M
import hook_scenes as K

A.set_theme("navy")
SCRIPT = """Roofers… forty patch jobs, or ONE re-roof. Same money. Which one are you chasing?
So how are some roofers booking re-roofs every single week… while you're up a ladder in the rain for a hundred and fifty euro? Stick with me. It's not what you think.
It's not better work. It's not cheaper prices. And it's not luck. It's where they show up.
A homeowner planning a new roof doesn't ring around first. They're on their phone at eleven at night, scrolling Facebook… and the first roofer they see with a "get a quote" button? He usually gets the job. The lad who's GOOD at roofing… loses to the lad who's EASY to find.
So we make YOU the easy one to find. We run Facebook and Instagram ads that go after re-roofs, flat roofs and fascias. Nothing else. The homeowner fills in their details… and it lands on your phone. Name, number, the job. You ring them back.
Try it for fourteen days. No fee. Just three hundred euro in ad spend… and you see every lead yourself.
We're only taking on two roofers this month. Comment "leads"… and I'll send you the details."""
VOICE, WORDS_JSON = "voice_roofers_easy.mp3", "vo_words_roofers_easy.json"
HAVE_VO = os.path.exists(VOICE) and os.path.exists(WORDS_JSON)
LOGO = Image.open("brand/southline_logo_badge.png").convert("RGBA")
PRE = 0.08  # visuals land a hair before the word so the whip-in has cleared


def estimate_words(script, start=0.15):
    """word timings at Seán's pace, fitted to his real 'maths' take: 0.03s + 0.122s per syllable, then the gap
    after the word: 0.45s for … , 0.44s for . , 0.32s for ? , 0.30s for , and 0.04s otherwise"""
    out, t = [], start
    for raw in script.split():
        w = raw.strip('"')
        syl = max(1, len(re.findall(r"[aeiouy]+", w.lower())))
        d = 0.03 + 0.122 * syl; out.append(dict(text=w, start=round(t, 2), end=round(t + d, 2))); t += d
        t += 0.45 if w.endswith("…") else 0.32 if w.endswith("?") else 0.44 if w.endswith(".") else 0.30 if w.endswith(",") else 0.04
    return out


WORDS = [w for w in json.load(open(WORDS_JSON))["words"] if w.get("type", "word") == "word"] if HAVE_VO else estimate_words(SCRIPT)


def at(phrase, after=0.0):
    """start time of the first occurrence of phrase (lower-case words, punctuation ignored) at or after `after` seconds"""
    clean = lambda s: "".join(c for c in s.lower() if c.isalnum() or c == "'").replace("€150", "150")
    alias = {"forty": "40", "fourteen": "14", "hundred": "150", "threehundred": "300"}
    want = [alias.get(clean(p), clean(p)) for p in phrase.split()]; ws = [alias.get(clean(w["text"]), clean(w["text"])) for w in WORDS]
    for i in range(len(ws) - len(want) + 1):
        if ws[i:i + len(want)] == want and WORDS[i]["start"] >= after: return WORDS[i]["start"]
    raise KeyError(phrase)


# scene starts: each on the first word of its line
S = [0.0, at("which one are") - PRE, at("so how are some") - PRE, at("stick with me") - PRE, at("it's not better") - PRE,
     at("it's where they") - PRE, at("a homeowner planning") - PRE, at("the lad who's") - PRE, at("so we make") - PRE,
     at("we run facebook") - PRE, at("name number") - PRE, at("try it for") - PRE, at("we're only taking") - PRE]
END = WORDS[-1]["end"] + 0.8
S = [round(x * A.FPS) / A.FPS for x in S] + [round(END * A.FPS) / A.FPS]
D = [b - a for a, b in zip(S, S[1:])]
r = lambda i, phrase: at(phrase, S[i] - 0.01) - S[i]  # beat time inside scene i

SCENES = [
    # HOOK  Roofers… forty patch jobs, or ONE re-roof. Same money.
    K.scene_hook_scale(dur=D[0], t40=r(0, "forty patch") - 0.05, t1=r(0, "one re-roof") - 0.05, same_at=r(0, "same money") - 0.05),
    #       Which one are you chasing?
    V.scene_slam([("WHICH ONE|ARE YOU", "d"), ("CHASING?", "dh")], dur=D[1], cuts=[0.0, r(1, "chasing")]),
    # OPEN QUESTION  So how are some roofers booking re-roofs every single week… while you're up a ladder in the rain for €150?
    K.scene_split_weeks(dur=D[2], left_at=r(2, "booking re-roofs") - 0.05, right_at=r(2, "while you're up") - 0.05),
    #       Stick with me. It's not what you think.
    V.scene_slam([("STICK|WITH ME.", "d"), ("IT'S NOT WHAT|YOU THINK.", "dh")], dur=D[3], lock_last=True, cuts=[0.0, r(3, "it's not what")]),
    # BODY 1  It's not better work. It's not cheaper prices. And it's not luck.
    K.scene_crossouts(["BETTER WORK", "CHEAPER PRICES", "LUCK"], [r(4, "better work") - 0.1, r(4, "cheaper prices") - 0.1, r(4, "luck") - 0.1], dur=D[4]),
    #       It's where they show up.
    V.scene_slam([("IT'S WHERE THEY", "d"), ("SHOW UP.", "y")], dur=D[5], cuts=[0.0, r(5, "show up") - 0.05]),
    #       A homeowner planning a new roof… on their phone at eleven at night, scrolling Facebook… first roofer they see… usually gets the job.
    K.scene_feed_scroll(dur=D[6], land_at=r(6, "and the first") - 0.05, tap_at=r(6, "get a quote") + 0.2, win_at=r(6, "he usually") - 0.05),
    #       The lad who's GOOD at roofing… loses to the lad who's EASY to find.
    K.scene_versus(dur=D[7], loses_at=r(7, "loses to") - 0.05, easy_at=r(7, "easy to find") - 0.1),
    # SOLUTION  So we make YOU the easy one to find.
    V.scene_slam([("SO WE MAKE YOU", "d"), ("THE EASY|ONE TO FIND.", "dh")], dur=D[8], lock_last=True, cuts=[0.0, r(8, "the easy one") - 0.05]),
    #       We run Facebook and Instagram ads that go after re-roofs, flat roofs and fascias. Nothing else. The homeowner fills in their details… and it lands on your phone.
    A.scene_steps([("We run your ads", "Facebook + Instagram, big jobs only"), ("They fill in a form", "Homeowners planning the work"),
                   ("It lands on your phone", "Straight to you, no middleman")], title="Here's how", mode="slide", dur=D[9],
                  drops=[0.15, r(9, "the homeowner fills") - 0.1, r(9, "it lands on") - 0.1]),
    #       Name, number, the job. You ring them back.  (example lead)
    M.scene_lead_card([("Name", "Declan K."), ("Number", "087 ••• ••••"), ("The job", "Full re-roof, 3-bed semi")],
                      [r(10, "name"), r(10, "number"), r(10, "the job")], tap_at=r(10, "you ring them") + 0.15, dur=D[10]),
    # OFFER  Try it for fourteen days. No fee. Just €300 in ad spend… and you see every lead yourself.
    A.scene_float_cards("TRY IT FOR 14 DAYS.", [("TEST DRIVE", "14 days", "See every lead yourself", False), ("OUR FEE", "€0", "No fee to us", True),
                                                ("AD SPEND", "€300", "Just your ad budget", False)],
                        dur=D[11], times=[r(11, "fourteen days") - 0.1, r(11, "no fee") - 0.1, r(11, "just") - 0.1]),
    # CTA  We're only taking on two roofers this month. Comment "leads"… and I'll send you the details.  (logo appears here only)
    A.scene_cta_comment("Only taking on 2", "roofers this month.", "LEADS", "SOUTHLINE AGENCY", "Meta ads for Irish roofers",
                        after="for the details.", toast_msg="I'll send you the details", dur=D[12],
                        comment_at=r(12, "comment leads") - 0.05, logo=LOGO),
]

if "--stills" in sys.argv:  # quick layout QA: a few frames per scene, no encode
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video()
for s in SCENES: v.add(*s)
out = "out/southline_roofers_easy_vo.mp4" if HAVE_VO else "out/southline_roofers_easy_PREVIEW_no_voice.mp4"
total = v.render(out, transition="whip", preview_times=[e - 0.3 for e in S[1:]], punch=True,
                 **(dict(voice=VOICE, voice_at=0.0) if HAVE_VO else {}))
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s ({'voice' if HAVE_VO else 'NO voice, estimated timing'})  scene starts {[round(x, 2) for x in S[:-1]]}")
if HAVE_VO: print("voice minus music while speaking (dB): min %.1f, median %.1f" % v.duck_report)
