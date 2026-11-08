"""Reddit collage (light background, 3000 x 2000 px): towns by misplacement, the turn of north, one sheet with its bent grid."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Patch
from PIL import Image
from shapely.geometry import box
from common import *

for d in (FONTS, INKFONTS):
    for f in os.listdir(d):
        if f.endswith(".ttf"): fm.fontManager.addfont(f"{d}/{f}")
BG, INKC, HOT, COOL, MUTED, SEA = "#FBF7EC", "#2B2119", "#A3261B", "#3D6E9E", "#6E604E", "#E6EEF0"
plt.rcParams.update({"font.family": "Source Serif 4", "text.color": INKC, "axes.edgecolor": INKC, "xtick.color": INKC, "ytick.color": INKC})
R = jload(f"{DATA}/results.json"); F = jload(f"{DATA}/fits.json"); G = jload(f"{DATA}/grid/p065.json")
L = pd.read_csv(f"{DATA}/located.csv"); C = L[L.sheet != GENERAL]
land = gpd.read_file(f"{GEO}/ne_10m_admin_0_countries.geojson")
land = land[land.geometry.intersects(box(-11, 49.5, 3, 56.5))].clip(box(-11, 49.5, 3, 56.5))

fig = plt.figure(figsize=(15, 10), dpi=200, facecolor=BG)
fig.text(0.03, 0.955, "Saxton's atlas of England and Wales (1574 to 1579), measured", fontfamily="Fraunces", fontweight="bold", fontsize=30)
fig.text(0.03, 0.915, f"{R['counts']['readings']} towns read on {R['counts']['sheets_county_read']} county maps and the general map. Each sheet fitted to the real positions at its own scale and turn.", fontsize=15, color=MUTED)

# panel A: map
ax = fig.add_axes([0.02, 0.07, 0.40, 0.82]); ax.set_facecolor(SEA)
land.plot(ax=ax, color="#F1E7CF", edgecolor=INKC, lw=.5)
bins = [1, 2, 3, 5]; cols = ["#3D6E9E", "#7FA3B8", "#C9A35A", "#C2603C", "#A3261B"]
labs = ["under 1 km", "1 to 2 km", "2 to 3 km", "3 to 5 km", "over 5 km"]
cat = np.digitize(C.err_km, bins)
for k in range(5):
    m = cat == k
    ax.scatter(C.lon[m], C.lat[m], s=16, color=cols[k], edgecolor=INKC, lw=.3, zorder=3)
ax.set_xlim(-6.3, 2.2); ax.set_ylim(49.8, 56.0); ax.set_aspect(1 / np.cos(np.radians(53))); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
ax.legend(handles=[Patch(color=c_, label=f"{l} ({int((cat == k).sum())})") for k, (c_, l) in enumerate(zip(cols, labs))], loc="upper left",
          title="How far each town is from\nwhere its own sheet puts it", fontsize=11, title_fontsize=11.5, facecolor=BG, edgecolor=INKC, framealpha=1)
ax.text(1.0, 55.55, f"Median: {R['county']['med_km']:.1f} km", fontsize=17, fontweight="bold", color=HOT, ha="center")
ax.text(0.6, 50.15, "English\nChannel", fontsize=11, color=MUTED, style="italic", ha="center")
ax.text(1.4, 54.3, "North\nSea", fontsize=11, color=MUTED, style="italic", ha="center")
ax.set_title("Where the towns are", loc="left", fontfamily="Fraunces", fontweight="bold", fontsize=18)

# panel B: turns
bx = fig.add_axes([0.52, 0.56, 0.44, 0.27]); bx.set_facecolor(BG)
cs = sorted([s for s in F if s != GENERAL], key=lambda s: F[s]["turn_deg"])
v = [F[s]["turn_deg"] for s in cs]
bx.hist(v, bins=np.arange(-26, 18, 2), color=HOT, edgecolor=BG)
bx.axvline(R["turn"]["borough_deg"], color=COOL, lw=2, ls="--")
bx.axvline(R["turn"]["general_deg"], color=MUTED, lw=2, ls=":")
bx.text(R["turn"]["borough_deg"] + .6, max(np.histogram(v, bins=np.arange(-26, 18, 2))[0]) + 0.9, "compass\nvariation,\nLondon 1580:\n~11¼° E", color=COOL, fontsize=11.5, va="top")
bx.text(R["turn"]["general_deg"] - .6, max(np.histogram(v, bins=np.arange(-26, 18, 2))[0]) * 0.6, "general\nmap", color=MUTED, fontsize=11.5, ha="right")
bx.text(-24, 1.6, "Cornwall\n(excluded from\nthe median)", fontsize=11, color=MUTED, ha="center")
bx.set_xlabel("degrees by which true north is turned anticlockwise on the sheet", fontsize=12)
bx.set_ylabel("county sheets", fontsize=12); bx.set_ylim(0, max(np.histogram(v, bins=np.arange(-26, 18, 2))[0]) + 1.5); bx.spines[["top", "right"]].set_visible(False)
bx.set_title(f"North leans west on {R['turn']['n_pos']} of {R['turn']['n']} sheets (median {R['turn']['median_deg']:.1f}°)", loc="left", fontfamily="Fraunces", fontweight="bold", fontsize=17, pad=26)
bx.text(0, 1.015, "The median leaves out Cornwall, turned the other way", transform=bx.transAxes, fontsize=11.5, color=MUTED, va="bottom")

# panel C: a sheet with its grid
cx = fig.add_axes([0.50, 0.08, 0.46, 0.36])
im = Image.open(f"{IMG}/sheets/p065.jpg"); k = jload(f"{DATA}/images.json")["p065"]["k"]
x0, y0, x1, y1 = 420, 160, 1480, 1000
cx.imshow(im.crop((x0, y0, x1, y1)), extent=(x0, x1, y1, y0))
for l in G:
    c_ = np.array(l["c"]); cx.plot(c_[:, 0], c_[:, 1], color=HOT if l["d"] == "v" else COOL, lw=1, alpha=.85)
cx.set_xlim(x0, x1); cx.set_ylim(y1, y0); cx.axis("off")
cx.set_title("Worcestershire, 1577: the true 5 km grid bent onto it", loc="left", fontfamily="Fraunces", fontweight="bold", fontsize=16)
fig.text(0.50, 0.045, "Red lines: true north to south. Blue: true east to west. They lean because the sheet does.", fontsize=11.5, color=MUTED)
fig.text(0.03, 0.018, "Data: Saxton's atlas, BnF copy (Wikimedia Commons, public domain); town positions Wikidata (CC0); coast Natural Earth.  Interactive: maps.tristanhotham.com/saxton-atlas  ·  Dr Tristan Hotham",
         fontsize=11, color=MUTED)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saxton_atlas.png")
fig.savefig(out, dpi=200, facecolor=BG); plt.close(fig)
print(out, Image.open(out).size)
