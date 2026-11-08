"""Step 0 (by hand, with help): reading places on the sheets.

This script does not read anything itself. It makes the pictures I read from:
  python3 00_reading_aid.py gaz                      build the candidate gazetteer (Wikidata settlements, one row per item,
                                                     with the ceremonial or preserved county it falls in)
  python3 00_reading_aid.py overview p041            the sheet at 1,600 px with a 200 px grid in full-size pixels
  python3 00_reading_aid.py crops p041 [n] [crop] [scale]
                                                     the next n candidate places, each as a crop of the full-size scan
                                                     centred where the current fit predicts it, with a ring at the
                                                     prediction and a tick scale in full-size pixels from the centre
  python3 00_reading_aid.py ingest p041              turn my picks (work/picks_p041.txt: 'k dx dy conf [note]' or
                                                     'k x' for not found) into rows of data/readings.csv
  python3 00_reading_aid.py zoom p041 x y [size] [scale]  one crop around a point, for hand-placed readings
The prediction uses the anchors I place by eye on the overview (work/anchors.csv) until a sheet has 6 readings, then a
similarity fit, an affine fit from 8, and a thin-plate spline from 14.
"""
import sys, os, json
import numpy as np, pandas as pd
from PIL import Image, ImageDraw, ImageFont
from common import *

Image.MAX_IMAGE_PIXELS = None
GAZ = f"{WORK}/gaz.csv"
READ = f"{DATA}/readings.csv"
COLS = ["sheet", "name", "engraved", "qid", "lon", "lat", "x", "y", "conf", "kind", "note"]
FONT = ImageFont.truetype(f"{FONTS}/IBMPlexMono-Medium.ttf", 18)
FONTS_ = ImageFont.truetype(f"{FONTS}/IBMPlexMono-Regular.ttf", 13)
TYPE_RANK = {"county town": 0, "city": 0, "big city": 0, "border city": 0, "city of United Kingdom": 0, "market town": 0,
             "town": 1, "town of the United Kingdom": 1, "small town": 1, "college town": 1, "seaside resort": 1, "urban area": 1, "Village": 2, "large village": 2, "nucleated village": 2, "hamlet": 4,
             "suburb": 5, "human settlement": 5, "area of London": 5, "neighborhood": 5, "locality": 5, "inner suburb": 5}


def path(sheet):
    return bnf(int(sheet[1:]))


def gaz():
    import geopandas as gpd
    s = pd.read_csv(SETTLE, sep="\t")
    s.columns = [c.strip("?") for c in s.columns]
    s["qid"] = s.p.str.extract(r"(Q\d+)")
    s["name"] = s.pl.str.replace(r'^"?(.*?)"?@en$', r"\1", regex=True)
    s["typel"] = s.typel.str.replace(r'^"?(.*?)"?@en$', r"\1", regex=True)
    s["rank"] = s.typel.map(TYPE_RANK)
    s = s.sort_values("pop", ascending=False).drop_duplicates("qid").drop(columns="rank").merge(
        s.groupby("qid")["rank"].min().reset_index(), on="qid")
    s = s[s["rank"].notna()]
    xy = s.coord.str.extract(r"POINT\(([-\d.]+) ([-\d.]+)\)").astype(float)
    s["lon"], s["lat"] = xy[0], xy[1]
    s = s.sort_values(["rank", "pop"], ascending=[True, False]).drop_duplicates("qid")
    g = gpd.GeoDataFrame(s, geometry=gpd.points_from_xy(s.lon, s.lat), crs=4326)
    c = gpd.read_file(f"{GEO}/counties_uk.geojson")[["county", "geometry"]].to_crs(4326)
    g27, c27 = g.to_crs(27700), c.to_crs(27700)
    g = gpd.sjoin_nearest(g27, c27, how="left", max_distance=4000).to_crs(4326)   # coastal points fall just outside the generalised outlines
    g = g[g.county.notna()].drop_duplicates("qid")
    out = g[["qid", "name", "lon", "lat", "pop", "rank", "typel", "county"]]
    out.to_csv(GAZ, index=False)
    print(len(out), "candidates")


def overview(sheet):
    im = Image.open(path(sheet)).convert("RGB")
    W, H = im.size
    k = 1600 / W
    sm = im.resize((1600, round(H * k)), Image.LANCZOS)
    d = ImageDraw.Draw(sm)
    for v in range(0, W, 200):
        d.line([(v * k, 0), (v * k, sm.size[1])], fill=(255, 0, 0), width=1)
        d.text((v * k + 2, 2), str(v), fill=(200, 0, 0), font=FONTS_)
    for v in range(0, H, 200):
        d.line([(0, v * k), (1600, v * k)], fill=(255, 0, 0), width=1)
        d.text((2, v * k + 2), str(v), fill=(200, 0, 0), font=FONTS_)
    sm.save(f"{WORK}/ov_{sheet}.jpg", quality=82)
    print(f"{WORK}/ov_{sheet}.jpg", W, H)


def known(sheet):
    R = pd.read_csv(READ) if os.path.exists(READ) else pd.DataFrame(columns=COLS)
    R = R[R.sheet == sheet]
    A = pd.read_csv(f"{WORK}/anchors.csv") if os.path.exists(f"{WORK}/anchors.csv") else pd.DataFrame(columns=["sheet", "name", "lon", "lat", "x", "y"])
    A = A[A.sheet == sheet]
    return R, A


def predictor(sheet):
    from scipy.interpolate import RBFInterpolator
    R, A = known(sheet)
    P = R if len(R) >= 12 else pd.concat([A[~A.name.isin(R.name)], R])
    X = np.c_[bng(P.lon.values, P.lat.values)]
    Y = np.c_[P.x.values.astype(float), -P.y.values.astype(float)]
    if len(P) >= 14:
        f = RBFInterpolator(X, Y, kernel="thin_plate_spline", smoothing=float(len(P)))
        kind = "tps"
    elif len(P) >= 8:
        f = affine(X, Y)[3]; kind = "affine"
    else:
        f = similarity(X, Y)[2]; kind = "similarity"
    print("predictor", kind, "on", len(P))
    return lambda lon, lat: (lambda q: np.c_[q[:, 0], -q[:, 1]])(f(np.c_[bng(lon, lat)]))


def done(sheet):
    R, A = known(sheet)
    rej = set()
    if os.path.exists(f"{WORK}/rejects.csv"):
        J = pd.read_csv(f"{WORK}/rejects.csv"); rej = set(J[J.sheet == sheet].qid)
    return set(R.qid.astype(str)) | rej


def crops(sheet, n=12, C=320, sc=1.25, maxrank=2):
    assert not os.path.exists(f"{WORK}/picks_{sheet}.txt"), "picks not yet ingested"
    G = pd.read_csv(GAZ)
    G = G[G.county.isin(SHEETS[sheet][3]) & (G["rank"] <= maxrank)]
    im = Image.open(path(sheet)).convert("RGB")
    W, H = im.size
    pr = predictor(sheet)
    Q = pr(G.lon.values, G.lat.values)
    G = G.assign(px=Q[:, 0], py=Q[:, 1])
    G = G[(G.px > 60) & (G.px < W - 60) & (G.py > 60) & (G.py < H - 60)]
    G = G[~G.qid.isin(done(sheet))]
    # spread the picks: skip a candidate whose prediction is within C/3 of one already taken in this batch
    take = []
    for r in G.itertuples():
        if all(np.hypot(r.px - t.px, r.py - t.py) > C / 3 for t in take):
            take.append(r)
        if len(take) == n: break
    D = round(C * sc)
    cols = 4 if n > 9 else 3
    rows = (len(take) + cols - 1) // cols
    cs = Image.new("RGB", (cols * (D + 6), rows * (D + 30)), "white")
    d = ImageDraw.Draw(cs)
    panels = []
    for k, r in enumerate(take):
        x0, y0 = int(r.px - C / 2), int(r.py - C / 2)
        cr = im.crop((x0, y0, x0 + C, y0 + C)).resize((D, D), Image.LANCZOS)
        dd = ImageDraw.Draw(cr)
        c = D / 2
        dd.ellipse([c - 9, c - 9, c + 9, c + 9], outline=(230, 0, 0), width=1)
        for t in range(-C // 2 + C // 2 % 50, C // 2 + 1, 50):
            p = c + t * sc
            dd.line([(p, 0), (p, 8)], fill=(0, 0, 255), width=1); dd.line([(0, p), (8, p)], fill=(0, 0, 255), width=1)
            dd.line([(p, D - 8), (p, D)], fill=(0, 0, 255), width=1); dd.line([(D - 8, p), (D, p)], fill=(0, 0, 255), width=1)
            if t: dd.text((p + 2, 8), str(t), fill=(0, 0, 200), font=FONTS_); dd.text((10, p - 7), str(t), fill=(0, 0, 200), font=FONTS_)
        X, Y = (k % cols) * (D + 6), (k // cols) * (D + 30)
        cs.paste(cr, (X, Y + 26))
        d.text((X + 2, Y + 2), f"{k} {r.name}", fill=(180, 0, 0), font=FONT)
        panels.append({"k": k, "qid": r.qid, "name": r.name, "lon": r.lon, "lat": r.lat, "cx": int(r.px), "cy": int(r.py)})
    json.dump(panels, open(f"{WORK}/panels_{sheet}.json", "w"))
    cs.save(f"{WORK}/crops_{sheet}.jpg", quality=84)
    print(f"{WORK}/crops_{sheet}.jpg", [(p["k"], p["name"]) for p in panels])


def ingest(sheet):
    panels = {p["k"]: p for p in json.load(open(f"{WORK}/panels_{sheet}.json"))}
    R = pd.read_csv(READ) if os.path.exists(READ) else pd.DataFrame(columns=COLS)
    rej = pd.read_csv(f"{WORK}/rejects.csv") if os.path.exists(f"{WORK}/rejects.csv") else pd.DataFrame(columns=["sheet", "qid", "name"])
    new, nrej = [], []
    for line in open(f"{WORK}/picks_{sheet}.txt"):
        t = line.split(None, 4)
        if not t: continue
        p = panels[int(t[0])]
        if t[1] == "x":
            nrej.append({"sheet": sheet, "qid": p["qid"], "name": p["name"]}); continue
        dx, dy, conf = float(t[1]), float(t[2]), int(t[3])
        note = t[4].strip() if len(t) > 4 else ""
        eng = ""
        if note.startswith("'"):
            eng, _, note = note[1:].partition("'"); note = note.strip()
        if "=" in note:                       # the reading is another place seen in this crop: '=Name' (gazetteer) or '=Name@lon,lat'
            note, _, other = note.partition("="); note = note.strip(); other = other.strip()
            if "@" in other:
                nm, ll = other.split("@"); lo, la = map(float, ll.split(","))
                p = {**p, "name": nm, "qid": "hand", "lon": lo, "lat": la}
            else:
                G = pd.read_csv(GAZ); g = G[(G.name == other) & G.county.isin(SHEETS[sheet][3])]
                g = g if len(g) else G[G.name == other]
                g = g.sort_values(["rank", "pop"], ascending=[True, False]).iloc[0]
                p = {**p, "name": g["name"], "qid": g.qid, "lon": g.lon, "lat": g.lat}
        new.append({"sheet": sheet, "name": p["name"], "engraved": eng, "qid": p["qid"], "lon": p["lon"], "lat": p["lat"],
                    "x": round(p["cx"] + dx), "y": round(p["cy"] + dy), "conf": conf, "kind": "town", "note": note})
    R = pd.concat([R, pd.DataFrame(new)], ignore_index=True)
    R = R[~((R.qid == "hand") & R.duplicated(["sheet", "name"], keep="last")) & ~((R.qid != "hand") & R.duplicated(["sheet", "qid"], keep="last"))]
    R[COLS].to_csv(READ, index=False)
    pd.concat([rej, pd.DataFrame(nrej)]).drop_duplicates().to_csv(f"{WORK}/rejects.csv", index=False)
    os.remove(f"{WORK}/picks_{sheet}.txt")
    print(sheet, "added", len(new), "rejected", len(nrej), "sheet total", int((R.sheet == sheet).sum()), "all", len(R))


def zoom(sheet, x, y, C=400, sc=1.0):
    im = Image.open(path(sheet)).convert("RGB")
    D = round(C * sc)
    cr = im.crop((x - C // 2, y - C // 2, x + C // 2, y + C // 2)).resize((D, D), Image.LANCZOS)
    dd = ImageDraw.Draw(cr)
    for t in range(-C // 2, C // 2 + 1, 50):
        p = D / 2 + t * sc
        dd.line([(p, 0), (p, 8)], fill=(0, 0, 255)); dd.line([(0, p), (8, p)], fill=(0, 0, 255))
        dd.text((p + 2, 8), str(x + t), fill=(0, 0, 200), font=FONTS_); dd.text((10, p - 7), str(y + t), fill=(0, 0, 200), font=FONTS_)
    cr.save(f"{WORK}/zoom.jpg", quality=85)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "gaz": gaz()
    elif a[0] == "overview": overview(a[1])
    elif a[0] == "crops": crops(a[1], *(int(v) if i < 2 else float(v) for i, v in enumerate(a[2:])))
    elif a[0] == "ingest": ingest(a[1])
    elif a[0] == "zoom": zoom(a[1], int(a[2]), int(a[3]), *(int(v) if i == 0 else float(v) for i, v in enumerate(a[4:])))
