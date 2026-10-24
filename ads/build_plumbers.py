"""Southline plumbers ad: 'relying on one builder' angle, volt theme, timed to the Seán voiceover.
python3 build_plumbers.py [--stills]
Every scene starts on its line and every beat inside a scene lands on its word, using the word timings
in vo_words_take1.json (ElevenLabs speech-to-text of voice_plumbers_v2_take1.mp3)."""
import json, sys
import adkit as A
import volt_scenes as V

A.set_theme("volt")
VOICE = "voice_plumbers_v2_take1.mp3"
WORDS = [w for w in json.load(open("vo_words_take1.json"))["words"] if w.get("type", "word") == "word"]
PRE = 0.08  # visuals land a hair before the word so the whip-in has cleared


def at(phrase, after=0.0):
    """start time of the first occurrence of phrase (lower-case words, punctuation ignored) at or after `after` seconds"""
    clean = lambda s: "".join(c for c in s.lower() if c.isalnum() or c == "'")
    want = [clean(p) for p in phrase.split()]; ws = [clean(w["text"]) for w in WORDS]
    for i in range(len(ws) - len(want) + 1):
        if ws[i:i + len(want)] == want and WORDS[i]["start"] >= after: return WORDS[i]["start"]
    raise KeyError(phrase)


# scene starts: each on the first word of its line
S = [0.0, at("if you're relying on word") - PRE, at("you're one phone call") - PRE, at("when he's flat") - PRE,
     at("and it gets worse") - PRE, at("you're working at") - PRE, at("and you only get paid") - PRE,
     at("so how come") - PRE, at("their own customers") - PRE, at("that's exactly") - PRE, at("fourteen days") - PRE,
     at("we're only taking") - PRE]
END = WORDS[-1]["end"] + 0.8
S = [round(x * A.FPS) / A.FPS for x in S] + [round(END * A.FPS) / A.FPS]
D = [b - a for a, b in zip(S, S[1:])]
r = lambda i, phrase: at(phrase, S[i] - 0.01) - S[i]  # beat time inside scene i

LEADS = [("Boiler + cylinder", "Terenure · 1930s house"), ("Bathroom refit", "Dundrum · full ensuite"),
         ("Boiler swap", "Templeogue · combi, no heat"), ("Bathroom refit", "Clontarf · family bathroom"),
         ("Boiler swap", "Churchtown · 3-bed semi")]

SCENES = [
    # 0 Plumbers, if you're relying on ONE builder for most of your work…
    V.scene_one_builder(l1="IF YOU'RE RELYING ON", l2="ONE BUILDER…", dur=D[0],
                        pop_at=r(0, "one builder") - 0.05, rise_at=r(0, "if you're relying") - 0.05),
    # 1 if you're relying on word of mouth to fill the gaps… and you're relying on that phone ringing before the van payment goes out…
    V.scene_relying([("One builder", "for most of your work"), ("Word of mouth", "to fill the gaps"),
                     ("The phone ringing", "before the van payment goes out")],
                    [0.0, r(1, "word of mouth") - 0.3, r(1, "phone ringing") - 0.3], dur=D[1]),
    # 2 you're one phone call away from a DEAD month.
    V.scene_slam([("YOU'RE ONE|PHONE CALL", "d"), ("AWAY FROM A", "d"), ("DEAD|MONTH.", "dh")], dur=D[2],
                 cuts=[0.0, r(2, "away from"), r(2, "dead month")]),
    # 3 When he's flat out? You're flat out. When he goes quiet… you're sitting in the van, staring at your phone.
    V.scene_linked(dur=D[3], flip=r(3, "when he goes quiet") - 0.05, lag=r(3, "sitting in the van") - r(3, "when he goes quiet"),
                   A_lines=(("WHEN HE'S FLAT OUT,", False), ("YOU'RE FLAT OUT.", True)),
                   B_lines=(("WHEN HE GOES QUIET…", False), ("YOU'RE SAT IN THE VAN.", True)),
                   step_a=r(3, "you're flat out") - 0.05, step_b=r(3, "you're sitting") - r(3, "when he goes quiet")),
    # 4 And it gets WORSE.
    V.scene_slam([("AND IT GETS", "d"), ("WORSE.", "dh")], dur=D[4], cuts=[0.0, r(4, "worse")]),
    # 5 You're working at HIS price. Not yours. Because he knows you can't say no.  (illustrative quote numbers)
    V.scene_his_price(dur=D[5], lines=(("YOU'RE WORKING AT", False), ("HIS PRICE.", True)),
                      stamp_at=r(5, "his price") - 0.05, strike_at=r(5, "not yours") - 0.05,
                      sub_txt="He knows you can't say no.", sub_at=r(5, "because he knows")),
    # 6 And you only get paid when HE gets paid. Sixty days… seventy days… and the van payment? That doesn't wait.
    V.scene_invoice(dur=D[6], lines=(("YOU ONLY GET PAID WHEN", False), ("HE GETS PAID.", True)),
                    keys=((0.6, 0), (r(6, "sixty days") + 0.3, 60), (r(6, "seventy days") + 0.3, 70)),
                    sub_txt="And the van payment?", sub_at=r(6, "and the van payment"),
                    van="THAT DOESN'T WAIT.", van_at=r(6, "that doesn't wait")),
    # 7 So how come some plumbers NEVER have a quiet week?
    V.scene_slam([("SO HOW COME|SOME PLUMBERS", "d"), ("NEVER HAVE A|QUIET WEEK?", "dh")], dur=D[7], lock_last=True,
                 cuts=[0.0, r(7, "never have")]),
    # 8 Their own customers. Homeowners ringing them direct. Boiler swaps. Bathroom refits. At THEIR price.
    V.scene_own_leads(LEADS, dur=D[8], lines=(("THEIR OWN", False), ("CUSTOMERS.", True)),
                      lt=[r(8, "homeowners"), r(8, "ringing them") + 0.2, r(8, "boiler swaps"), r(8, "bathroom refits"), r(8, "bathroom refits") + 0.55],
                      tag_at=r(8, "boiler swaps"), price_at=r(8, "at their price") - 0.05, price_txt="AT THEIR PRICE."),
    # 9 That's exactly what we set up for you.
    V.scene_slam([("THAT'S EXACTLY|WHAT WE", "d"), ("SET UP|FOR YOU.", "y")], dur=D[9], cuts=[0.0, r(9, "set up")]),
    # 10 Fourteen days. No fee. Just €300 ad spend. See the leads yourself.
    A.scene_offer("14-DAY TEST DRIVE", "€0 fee", "Just €300 ad spend.", "See the leads yourself.",
                  ["Homeowners straight to you", "Boiler swaps + bathroom refits"], dur=D[10]),
    # 11 We're only taking on two plumbers this month. Comment "leads" and we'll send you the details.  (first logo)
    A.scene_cta_comment("Only taking on 2", "plumbers this month.", "LEADS", "SOUTHLINE", "Meta ads for Irish plumbers",
                        after="for the details.", toast_msg="We'll send you the details", dur=D[11],
                        comment_at=r(11, "comment leads") - 0.05),
]

if "--audio" in sys.argv:  # soundtrack only, for checking the mix
    v = A.Video(); [v.add(*s) for s in SCENES]
    v.render("out/audio_check.m4a", voice=VOICE, audio_only=True)
    print("voice minus music while speaking (dB): min %.1f, median %.1f" % v.duck_report); sys.exit()

if "--stills" in sys.argv:  # quick layout QA: a few frames per scene, no encode
    from PIL import Image
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video()
for s in SCENES: v.add(*s)
out = "out/southline_plumbers_relying_vo.mp4"
total = v.render(out, transition="whip", preview_times=[e - 0.3 for e in S[1:]], voice=VOICE, voice_at=0.0)
print(f"rendered {total:.2f}s  scene starts {[round(x, 2) for x in S[:-1]]}")
print("voice minus music while speaking (dB): min %.1f, median %.1f" % v.duck_report)
