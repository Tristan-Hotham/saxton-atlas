"""Step 1: the sheets for the page and figures.

Each BnF sheet used (the general map and the 34 county maps) is reduced to 2,000 px wide (img/sheets/<id>.jpg) for the
page, plus a 480 px thumbnail (img/thumbs/<id>.jpg) for the sheet picker. Full-size pixel positions are kept in the data;
the page scales them by the factor stored in data/images.json. Page 119 (a map of Scotland bound with the atlas, not
Saxton's) and the five single sheets from other copies are not published here.
"""
from PIL import Image
from common import *

Image.MAX_IMAGE_PIXELS = None
os.makedirs(f"{IMG}/sheets", exist_ok=True)
os.makedirs(f"{IMG}/thumbs", exist_ok=True)
info = {}
for sid in sorted(SHEETS):
    im = Image.open(bnf(int(sid[1:]))).convert("RGB")
    W, H = im.size
    w = 2000
    sm = im.resize((w, round(H * w / W)), Image.LANCZOS)
    sm.save(f"{IMG}/sheets/{sid}.jpg", quality=72, optimize=True, progressive=True)
    th = im.resize((480, round(H * 480 / W)), Image.LANCZOS)
    th.save(f"{IMG}/thumbs/{sid}.jpg", quality=70, optimize=True)
    info[sid] = {"w": W, "h": H, "web_w": w, "web_h": sm.size[1], "k": w / W}
mb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(IMG) for f in fs) / 1e6
print(len(info), "sheets", round(mb, 1), "MB")
jsave(info, f"{DATA}/images.json", indent=1)
