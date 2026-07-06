"""Round-8: regenerate the select busts AS A PAIR in one canvas — both refs
passed in, model draws them side-by-side at identical zoom/head-size/shoulder
mass, then we split. Fixes the inherent composition mismatch (kenji narrow
with margins vs hayato wide-hat full-bleed)."""
import json, base64, urllib.request, os, time

KEY = os.environ['GEMINI_API_KEY']
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={KEY}"

def b64(p): return base64.b64encode(open(p, 'rb').read()).decode()

PROMPT = (
    "Draw a TWO-PANEL character-select portrait pair for a fighting game, one canvas split "
    "into a left half and a right half, both panels painted by the same artist in the same "
    "16-bit painterly pixel-art style.\n"
    "LEFT panel: the cloaked swordsman from the FIRST reference image - keep his design 100%: "
    "wide thin dark-plum lacquered disc hat tilted low, pale mask-like white face, narrow "
    "glowing RED eyes, crimson scarf knotted at the neck, bone-grey robe.\n"
    "RIGHT panel: the oni-masked ninja from the SECOND reference image - keep his design 100%: "
    "red oni mask with gold horns, black spiky hair, indigo shinobi garb, blade on his back.\n"
    "CRITICAL - the two portraits must be a perfectly MATCHED SET: identical zoom level, "
    "identical head size, head centers at the same height, similar shoulder width and "
    "silhouette mass, both head-and-shoulders busts with the same amount of breathing room "
    "around them, each centered in its own half. Hayato's wide hat may be cropped equally on "
    "both sides if needed. Both face slightly toward each other (left one faces right, right "
    "one faces left). Flat near-black background (#0a0a0c) in both panels, a thin 4-pixel "
    "black gap between panels, no text, no watermark, wide 2:1 composition."
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
parts = [
    {"text": PROMPT},
    {"inline_data": {"mime_type": "image/png", "data": b64('portrait-hayato-bust.png')}},
    {"inline_data": {"mime_type": "image/png", "data": b64('ref-kenji-bust.png')}},
]
body = json.dumps({"contents": [{"parts": parts}],
                   "generationConfig": {"responseModalities": ["IMAGE"]}}).encode()
for c in range(1, 4):
    out = f"portrait-pair-c{c}.png"
    if os.path.exists(out):
        print('skip', out); continue
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL, data=body, headers={'Content-Type': 'application/json'})
            d = json.load(urllib.request.urlopen(req, timeout=120))
            img = next(p for p in d['candidates'][0]['content']['parts'] if 'inlineData' in p)
            open(out, 'wb').write(base64.b64decode(img['inlineData']['data']))
            print('OK', out); break
        except Exception as e:
            print('retry', out, str(e)[:120]); time.sleep(4)
    else:
        print('FAIL', out)
print('DONE')
