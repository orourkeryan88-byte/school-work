"""Southline TRUST video for E-COMMERCE brands: the same format, scenes and look as the trades trust video
(build_trust.py), with the wording, pictures and B-roll swapped for online stores. Sells only Meta ads + email.
Timed to the script read at a natural pace; Ryan records the voiceover, then it gets re-timed to the recording.
python3 build_ecom_trust.py [--stills] [--music song.mp4]"""
import sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw
import adkit as A
import trust_scenes as S
import broll as B
import build_trust_audio as BA

B.KIND = "ecom"  # products and orders in the B-roll instead of kitchens and enquiries

A.set_theme("midnight", accent=S.ACC, accent2=S.ACC, bg=((8, 10, 14), (4, 5, 8)), blobs=[], grid=False)
THUMB = "brand/southline_thumb_square.webp"; w = S.with_shot
GOLD, NAVY = (226, 178, 92), (28, 34, 52)


def shot(w_, h_, bg=((244, 238, 230), (226, 218, 206)), bottles=((0.5, 1.0, (232, 220, 204)),)):
    """product photo: soft backdrop + bottles (x as fraction of width, scale, body colour)"""
    im = Image.fromarray(B.vgrad(w_, h_, *bg).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.ellipse((w_ * 0.1, h_ * 0.78, w_ * 0.9, h_ * 0.96), fill=(0, 0, 0, 25))
    for fx, sc, body in bottles: B.product(d, w_ * fx, h_ * 0.55, sc * h_ / 420, body=body)
    return im

def review(w_, h_):
    im = Image.new("RGBA", (w_, h_), (252, 252, 250, 255)); d = ImageDraw.Draw(im)
    for i in range(5):
        x = 50 + i * 60; y = 70
        d.polygon([(x, y - 26), (x + 8, y - 8), (x + 28, y - 8), (x + 12, y + 4), (x + 18, y + 24), (x, y + 12), (x - 18, y + 24), (x - 12, y + 4), (x - 28, y - 8), (x - 8, y - 8)], fill=GOLD)
    d.text((30, 120), "“Obsessed with this.", font=A.font("bl", 34), fill=(20, 24, 34)); d.text((30, 165), "Already ordered", font=A.font("bl", 34), fill=(20, 24, 34))
    d.text((30, 210), "my second one!”", font=A.font("bl", 34), fill=(20, 24, 34)); d.text((30, 268), "Aoife, Galway · verified buyer", font=A.font("m", 22), fill=(120, 126, 138))
    return im

def best_seller(w_, h_):
    im = shot(w_, h_, ((230, 236, 244), (208, 216, 230)), ((0.5, 1.0, (240, 236, 228)),)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 190, 64), 22, fill=NAVY); d.text((36, 28), "BEST SELLER", font=A.font("bl", 22), fill=GOLD)
    return im

S.TXT.update(
    intro_big="Online stores", question=["Do Facebook ads actually", "work for online stores?"],
    post_name="Your page", post_sub="New drop is live!", comments=("Love this!", "Where's it from?", "Need this"),
    post_pic=lambda: shot(680, 400, bottles=((0.28, 0.85, (232, 220, 204)), (0.5, 1.0, (210, 226, 216)), (0.72, 0.85, (236, 214, 210)))),
    zero="0 sales", cap1="Posting and hoping",
    what_pills=("Meta ads", "Email"), what_mid="for online brands in", what_end="Ireland & the UK.",
    trades=["Skincare", "Clothing", "Supplements", "Home", "Gifts"],
    aim1="more people buying,", aim2="more coming back.", aim_key="coming back", ping="New order",
    how_head="Your best products.", how_pics=lambda: [shot(380, 320), review(380, 320), best_seller(380, 320)],
    how_caps=("Your products", "Your reviews", "Best sellers"), how_b1="In front of people", how_b2="most likely to buy.", how_key="most likely to buy",
    q_h1="Add to basket, then leave?", q_h2="An email brings them back.", q_key="brings them back",
    q_rows=[("ADDED TO BASKET", "Linen shirt"), ("LEFT THE SITE", "11:42pm"), ("EMAIL SENT", "Still thinking?")], q_know="Back to checkout",
    ph_h="Then they buy again.", ph_h2="Repeat customers.", ph_kind="NEW ORDER", ph_title="Order #1043 · €58", ph_sub="Aoife · first order",
    ph_call="Thank-you email", ph_calling="Sent  ✓", ph_steps=("Order 1  ✓", "Order 2  ✓", "Order 3"),
    wom_a1="Spending on ads,", wom_a2="but sales feel flat…", wom_akey="sales feel flat",
    wom_b1="And no emails", wom_b2="going out to customers.", wom_bkey="going out",
    wom_says=[("Ads are getting dear.", -1), ("Sales are flat this month.", 1), ("We don't really do email.", -1)], wom_booked={1: "2 orders", 7: "1 order"},
    end3="Just ads & emails done properly.", end_sub="Meta ads + email for online brands",
)
CHIPS = [["Skincare", "Clothing", "Supplements"], ["Home & gifts"]]

SCENES = [  # (scene over its B-roll, the line said over it)
    (w(S.scene_intro(dur=4.8), B.parcels), "Online store owners in Ireland and the UK. I'm Ryan, I run a marketing agency,"),
    (w(S.scene_common(dur=2.3), B.parcels), "and the biggest question I get asked is…"),
    (w(S.scene_question(dur=2.7, type_from=0.3), B.desk), "Do Facebook ads actually work for online stores?"),
    (w(S.scene_short(dur=7.4, s1_at=0.2, yeah_at=1.2, props_at=1.65, post_at=3.4, comments_at=(4.0, 4.5, 5.0), calls_at=5.3, cap_at=(5.6, 6.3)), B.phone_feed),
     "Short answer? Yeah, when they're done properly. Posting your products and hoping for the best isn't the same thing."),
    (w(S.scene_title("01", ["So what do we", "actually do?"], 3.0, 1.3, 0.5, 0.55, dur=1.7), B.parcels), "So what do we actually do?"),
    (w(S.scene_what(dur=4.9, s0_at=0.2, pills_at=(0.45, 0.9), s1_at=1.6, pin_at=3.0, s3_at=3.3), B.dashboard),
     "We run Meta ads and email marketing for online brands in Ireland and the UK."),
    (w(S.scene_trades(dur=3.6, times=(0.2, 0.8, 1.4, 2.0, 2.6)), B.checkout), "Skincare, clothing, supplements, home and gifts."),
    (w(S.scene_aim(dur=4.2, ring_at=0.6, pings_at=1.4, lines_at=(0.2, 1.1, 2.3)), B.map_), "The goal's simple: more people buying, and more of them coming back."),
    (w(S.scene_title("02", ["So how do we", "actually do it?"], 5.0, 1.3, 0.5, 0.45, dur=1.7), B.dashboard), "So how do we actually do it?"),
    (w(S.scene_how(dur=7.6, fly_at=3.7), [(0.0, B.checkout), (3.7, B.desk)]),
     "We take your best products, your photos and your reviews, and put them in front of the people most likely to buy."),
    (w(S.scene_questions(dur=4.4, rows_at=(1.0, 1.6, 2.6), h2_at=2.3, know_at=3.4), B.checkout), "When someone adds to basket and leaves, an email brings them back."),
    (w(S.scene_phone(dur=5.4, note_at=0.8, call_at=1.8, tap_at=2.3, quote_at=2.9, book_at=3.6, tools_at=4.3), B.desk),
     "And once they've bought, emails turn them into repeat customers, without paying for another ad."),
    (w(S.scene_title("03", ["So who's", "it for?"], 2.0, 1.2, 0.5, 0.5, dur=1.5, chips=CHIPS), B.map_), "So who's it for?"),
    (w(S.scene_wom(dur=6.4, bubbles_at=(0.6, 1.0, 1.4), dry_at=1.9, swap=2.5, ul_at=3.6, help_at=5.1), B.parcels),
     "Online brands spending on ads, but sales feel flat, and no emails going out. That's who we help."),
    (w(S.scene_end(dur=5.6, card_at=3.9, lines_at=(0.3, 0.95, 1.8)), B.parcels), "That's it. No magic. Just ads and emails done properly."),
    (S.scene_thumb(THUMB, dur=2.5), "(end card / thumbnail, no voice)"),
]

if "--stills" in sys.argv:
    for i, ((dur, fn, _), _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (dur * 0.25, dur * 0.6, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

MUSIC = sys.argv[sys.argv.index("--music") + 1] if "--music" in sys.argv else None
v = A.Video(); [v.add(*s) for s, _ in SCENES]
raw, out, bed = "out/_ecomtrust_raw.mp4", "out/southline_trust_ecom.mp4", "out/_ecomtrust_music.wav"
ends, t = [], 0
for (d, _, _), _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.4)
total = v.render(raw, transition="whip", tr_frames=4, preview_times=ends, music=False, lufs=None, punch=False, drift=0.0)
BA.song_bed(total, MUSIC, bed) if MUSIC else BA.music_bed(total, bed)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-i", bed, "-filter_complex",
                "[0:a]volume=0.4[s];[1:a]volume=1.0[m];[s][m]amix=inputs=2:normalize=0,lowpass=f=15000,loudnorm=I=-22:TP=-3:LRA=11,aresample=48000[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
os.remove(bed); os.replace(raw.replace(".mp4", "_preview.png"), out.replace(".mp4", "_preview.png")); os.remove(raw)
cue, t = [], 0.0
for (d, _, _), line in SCENES: cue.append(f"{int(t // 60)}:{t % 60:05.2f}  {line}"); t += round(d * A.FPS) / A.FPS
open("out/southline_trust_ecom_cues.txt", "w").write("\n".join(cue) + "\n"); print(f"rendered {total:.2f}s"); print("\n".join(cue))
