"""Step 4: figures for the blog (release/blog/b_*.png), the paper (release/paper/f_*.png) and the header card."""
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyArrowPatch
from PIL import Image
from shapely.geometry import box
from common import *

Image.MAX_IMAGE_PIXELS = None
for f in os.listdir(FONTS):
    if f.endswith(".ttf"): fm.fontManager.addfont(f"{FONTS}/{f}")
for f in os.listdir(INKFONTS):
    if f.endswith(".ttf"): fm.fontManager.addfont(f"{INKFONTS}/{f}")
PAPER, INKC, HOT, COOL, MUTED, GOLD = "#F6EED8", "#2B2119", "#A3261B", "#3D6E9E", "#6E604E", "#B8862B"
plt.rcParams.update({"font.family": "Source Serif 4", "font.size": 11, "axes.facecolor": PAPER, "figure.facecolor": PAPER,
                     "axes.edgecolor": INKC, "axes.labelcolor": INKC, "xtick.color": INKC, "ytick.color": INKC, "text.color": INKC,
                     "axes.spines.top": False, "axes.spines.right": False})
BLOG = f"{ROOT}/release/blog"; PAP = f"{ROOT}/release/paper"
os.makedirs(BLOG, exist_ok=True); os.makedirs(PAP, exist_ok=True)
R = jload(f"{DATA}/results.json"); F = jload(f"{DATA}/fits.json"); G = jload(f"{WORK}/grids.json")
L = pd.read_csv(f"{DATA}/located.csv")
C = L[L.sheet != GENERAL]
cs = [s for s in F if s != GENERAL]


def save(fig, name, paper=True):
    fig.savefig(f"{BLOG}/b_{name}.png", dpi=150, bbox_inches="tight", facecolor=PAPER)
    if paper and name in ("grid", "sheets", "reading"):     # photographic figures: JPEG keeps the paper small
        fig.savefig(f"{WORK}/f_tmp.png", dpi=170, bbox_inches="tight", facecolor=PAPER)
        Image.open(f"{WORK}/f_tmp.png").convert("RGB").save(f"{PAP}/f_{name}.jpg", quality=82, optimize=True); os.remove(f"{WORK}/f_tmp.png")
    elif paper: fig.savefig(f"{PAP}/f_{name}.png", dpi=200, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


def title(ax, t, sub=None):
    ax.set_title(t, loc="left", fontfamily="Fraunces", fontweight="bold", fontsize=16, pad=22 if sub else 8)
    if sub: ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=10.5, color=MUTED, va="bottom")


land = gpd.read_file(f"{GEO}/ne_10m_admin_0_countries.geojson")
land = land[land.geometry.intersects(box(-11, 49.5, 2.5, 56.2))].clip(box(-11, 49.5, 2.5, 56.2))

# 1. the atlas: a grid of sheet thumbnails
ids = ["p014", "p032", "p083", "p041", "p086", "p053", "p035", "p101"]
fig, axs = plt.subplots(2, 4, figsize=(13, 6.6))
for ax, s in zip(axs.flat, ids):
    ax.imshow(Image.open(f"{IMG}/thumbs/{s}.jpg")); ax.axis("off")
    ax.set_title(f"{F[s]['short']}, {F[s]['year']}", fontsize=10.5, color=INKC)
fig.suptitle("Eight of the 35 maps in Saxton's atlas (BnF copy)", x=0.02, ha="left", fontfamily="Fraunces", fontweight="bold", fontsize=16)
fig.tight_layout(); save(fig, "sheets")

# 2. reading close up: Worcestershire, readings and where the fit puts the true places
s = "p065"; im = Image.open(bnf(65)).convert("RGB")
D = L[L.sheet == s]
x0, y0, x1, y1 = 1300, 500, 2600, 1900
fig, ax = plt.subplots(figsize=(8.5, 8.5 * (y1 - y0) / (x1 - x0)))
ax.imshow(im.crop((x0, y0, x1, y1)), extent=(x0, x1, y1, y0))
for r in D.itertuples():
    if not (x0 < r.x < x1 and y0 < r.y < y1): continue
    ax.add_patch(FancyArrowPatch((r.x, r.y), (r.fit_x, r.fit_y), arrowstyle="-|>", mutation_scale=9, color=HOT, lw=1.6))
    ax.plot(r.x, r.y, "o", ms=6, mfc="none", mec=COOL, mew=1.6)
    ax.text(r.x + 14, r.y - 14, r.name, fontsize=9, color=INKC, bbox=dict(fc="#FBF5E4", ec="none", alpha=.8, pad=1))
ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.axis("off")
title(ax, "Reading the sheet: Worcestershire, 1577", "Blue rings: the town symbols I read. Red arrows: to where the true town falls at the sheet's own scale and turn.")
save(fig, "reading")

# 3. median misplacement per sheet
order = sorted(cs, key=lambda s: F[s]["med_km"])
fig, ax = plt.subplots(figsize=(9, 8.6))
y = np.arange(len(order))
ax.barh(y, [F[s]["med_km"] for s in order], color=[RCOL[F[s]["region"]] for s in order], height=.7)
ax.set_yticks(y, [f"{F[s]['short']} ({F[s]['n']})" for s in order], fontsize=9.5)
ax.axvline(R["county"]["med_km"], color=INKC, lw=1, ls="--")
ax.text(R["county"]["med_km"] + .05, len(order) - .4, f"all county readings: {R['county']['med_km']:.1f} km", fontsize=9.5)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=rn) for rn, c in REGIONS if rn != "General"], frameon=False, loc="lower right", fontsize=9.5)
ax.set_xlabel("median misplacement (km), each sheet at its own scale and turn")
title(ax, "Most county sheets put a town within 1 to 2 km", f"{R['counts']['used_county']} places on {R['counts']['sheets_county_read']} county sheets (number read in brackets)")
save(fig, "errors")

# 4. the turn of north
order = sorted(cs, key=lambda s: F[s]["turn_deg"])
fig, ax = plt.subplots(figsize=(9, 8.6))
y = np.arange(len(order))
ax.axvspan(R["turn"]["q1_deg"], R["turn"]["q3_deg"], color=GOLD, alpha=.18, lw=0)
ax.axvline(0, color=INKC, lw=1)
ax.axvline(R["turn"]["borough_deg"], color=COOL, lw=1.6, ls="--")
ax.text(R["turn"]["borough_deg"] - .4, 3.5, "compass variation\nat London, 1580\n(Borough):\nabout 11¼° east", color=COOL, fontsize=9.5, va="center", ha="right")
ax.axvline(R["turn"]["general_deg"], color=MUTED, lw=1.2, ls=":")
ax.text(R["turn"]["general_deg"] - .5, 8, "general map\nof 1579", color=MUTED, fontsize=9.5, ha="right")
ax.scatter([F[s]["turn_deg"] for s in order], y, s=46, color=[RCOL[F[s]["region"]] for s in order], zorder=3, edgecolor=INKC, lw=.5)
ax.set_yticks(y, [F[s]["short"] for s in order], fontsize=9.5)
ax.set_xlabel("degrees by which true north is turned anticlockwise on the sheet")
ax.set_ylim(-2.2, len(order))
title(ax, f"County sheets lean about {R['turn']['median_deg']:.0f}° to the west (Cornwall excluded)", f"Median {R['turn']['median_deg']:.1f}° (shaded: middle half of sheets, Cornwall left aside); the general map is close to true north")
save(fig, "turns")

# 5. every place on the ground, coloured by misplacement
fig, ax = plt.subplots(figsize=(8.4, 10))
land.plot(ax=ax, color="#EFE3C4", edgecolor=INKC, lw=.5)
bins = [0, 1, 2, 3, 5, 99]; cols = ["#3D6E9E", "#7FA3B8", "#C9A35A", "#C2603C", "#A3261B"]
labs = ["under 1 km", "1 to 2 km", "2 to 3 km", "3 to 5 km", "over 5 km"]
cat = np.digitize(C.err_km, bins[1:-1])
for k in range(5):
    m = cat == k
    ax.scatter(C.lon[m], C.lat[m], s=13, color=cols[k], edgecolor=INKC, lw=.25, label=f"{labs[k]} ({int(m.sum())})", zorder=3)
ax.set_xlim(-6.1, 2.0); ax.set_ylim(49.85, 55.95); ax.set_aspect(1 / np.cos(np.radians(53)))
ax.axis("off"); ax.legend(loc="lower right", frameon=True, facecolor=PAPER, edgecolor=INKC, title="misplacement", fontsize=9.5)
title(ax, "Every town I read, by how far its own sheet misplaces it", f"{R['counts']['used_county']} readings, {R['counts']['places_unique']} places in all")
save(fig, "map")

# 6. the bent grid on a sheet: Cornwall
s = "p035"; im = Image.open(f"{IMG}/sheets/{s}.jpg"); k = jload(f"{DATA}/images.json")[s]["k"]
fig, ax = plt.subplots(figsize=(10, 10 * im.size[1] / im.size[0]))
ax.imshow(im)
for l in G[s]["lines"]:
    c = np.array(l["c"]) * k
    ax.plot(c[:, 0], c[:, 1], color=HOT if l["d"] == "v" else COOL, lw=.9, alpha=.85)
ax.axis("off")
title(ax, "Cornwall, 1576, with the true 5 km grid bent onto it", f"Red lines run true north and south; the sheet is turned {abs(R['turn']['cornwall_deg']):.0f}° clockwise, perhaps to fit the peninsula on the plate")
save(fig, "grid")

# 7. general map against the Gough Map
Gm = L[L.sheet == GENERAL]
fig, ax = plt.subplots(figsize=(8.4, 9.6))
land.plot(ax=ax, color="#EFE3C4", edgecolor=INKC, lw=.5)
for r in Gm.itertuples():
    ax.annotate("", xy=(r.lon + 5 * (r.map_lon - r.lon), r.lat + 5 * (r.map_lat - r.lat)), xytext=(r.lon, r.lat), arrowprops=dict(arrowstyle="-|>", color=HOT, lw=1.2, mutation_scale=8))
ax.scatter(Gm.lon, Gm.lat, s=10, color=INKC, zorder=3)
ax.set_xlim(-5.0, 2.0); ax.set_ylim(50.3, 54.3); ax.set_aspect(1 / np.cos(np.radians(52.5)))
ax.axis("off")
ax.text(0.02, 0.03, f"General map (1579): median {R['general']['med_km']:.1f} km\nGough Map (about 1360): median {R['gough']['med_km']:.1f} km",
        transform=ax.transAxes, fontsize=11, bbox=dict(fc=PAPER, ec=INKC))
title(ax, f"The general map of 1579: where it puts {R['general']['n']} towns", "Arrows from the true place towards where the map puts it, drawn 5 times longer than life")
save(fig, "general")

# header card 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1200); ax.set_ylim(630, 0)
th = Image.open(f"{IMG}/sheets/p065.jpg"); th = th.crop((500, 150, 1450, 1150)).resize((560, 590))
ax.imshow(th, extent=(620, 1180, 610, 20))
ax.text(40, 120, "Saxton's atlas,", fontfamily="Fraunces", fontweight="bold", fontsize=40)
ax.text(40, 185, "measured", fontfamily="MedievalSharp", fontsize=44, color=HOT)
ax.text(40, 270, f"{R['counts']['readings']} towns read on {R['counts']['sheets_county_read'] + 1} maps of 1574 to 1579.", fontsize=17)
ax.text(40, 310, f"A median town is {R['county']['med_km']:.1f} km from where its", fontsize=17)
ax.text(40, 345, f"county sheet puts it, and north leans {R['turn']['median_deg']:.0f}° west", fontsize=17)
ax.text(40, 380, "(median of county sheets, Cornwall excluded).", fontsize=17)
ax.text(40, 590, "Dr Tristan Hotham · maps.tristanhotham.com/saxton-atlas", fontfamily="IBM Plex Mono", fontsize=12, color=MUTED)
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=PAPER); plt.close(fig)
print("figures done")
