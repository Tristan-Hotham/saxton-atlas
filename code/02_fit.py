"""Step 2: fits, misplacements, scales, turns, distortion grids.

For each sheet, true positions are put on a flat local frame in kilometres (azimuthal equidistant about the centre of
the sheet's readings, so 'up' is true north at that centre) and the readings on the sheet in full-size scan pixels (y
turned upward). Then:
  similarity  pixels = a * ground + b (a complex: one scale, one turn; 4 numbers)
  affine      6 numbers; stretch = ratio of the singular values of the linear part
  thin-plate spline (smoothing = number of readings, on km) for the bent grid and a leave-one-out check
Misplacement of a place: the distance on the ground between where it is and where the sheet puts it, taking the sheet
position back through the inverse of that sheet's similarity (so each sheet is judged at its own scale and turn).
Affine misplacement likewise. 'Turn' is the angle by which true north is turned on the sheet (positive anticlockwise, so
a sheet whose north leans to the left of the frame's top has a positive turn).

Outliers: a reading misplaced by more than max(5 km, 4 x the sheet's median) under the similarity is listed in
data/outliers.csv and dropped from the fits (they are, case by case, a misidentified place or a symbol far from its
name); the counts are reported.

The same is done for the general map of England and Wales (p014) over the whole country, for a like-for-like comparison
with the Gough Map (about 1360), whose figure is read from the gough-map study's results.json.

Places read on two county sheets give a sheet-to-sheet check: the distance between the two ground positions the two
sheets give for the same place.
"""
import numpy as np, pandas as pd
from scipy.interpolate import RBFInterpolator
from pyproj import Transformer
from shapely.geometry import MultiPoint, LineString
from common import *

R = pd.read_csv(f"{DATA}/readings.csv")
assert R.duplicated(["sheet", "name"]).sum() == 0, R[R.duplicated(["sheet", "name"], keep=False)]
IMI = jload(f"{DATA}/images.json")
R["region"] = R.sheet.map(lambda s: SHEETS[s][4])
R["sheet_name"] = R.sheet.map(lambda s: SHEETS[s][1])


def frame(lat0, lon0):
    t = Transformer.from_crs(4326, f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=km", always_xy=True)
    return (lambda lo, la: np.c_[t.transform(np.asarray(lo, float), np.asarray(la, float))]), \
           (lambda x, y: np.c_[t.transform(np.asarray(x, float), np.asarray(y, float), direction="INVERSE")])


def fit_sheet(D):
    lat0, lon0 = float(D.lat.mean()), float(D.lon.mean())
    fwd, inv = frame(lat0, lon0)
    X = fwd(D.lon.values, D.lat.values)
    Y = np.c_[D.x.values.astype(float), -D.y.values.astype(float)]
    s, th, f, finv = similarity(X, Y)
    G = finv(Y)
    err = np.hypot(*(G - X).T)
    M, C, an, af, ainv = affine(X, Y)
    Ga = ainv(Y)
    erra = np.hypot(*(Ga - X).T)
    return dict(lat0=lat0, lon0=lon0, fwd=fwd, inv=inv, X=X, Y=Y, s=s, th=th, f=f, finv=finv, G=G, err=err, M=M, C=C, aniso=an, af=af, ainv=ainv, erra=erra)


OUT, rows, outl, grids, arrows = {}, [], [], {}, {}
for sid in sorted(SHEETS):
    D0 = R[R.sheet == sid].reset_index(drop=True)
    if len(D0) < 6: continue
    F = fit_sheet(D0)
    med = np.median(F["err"])
    bad = F["err"] > max(5.0, 4 * med) if sid != GENERAL else F["err"] > max(25.0, 4 * med)
    # refit without outliers, then recheck once
    D = D0[~bad].reset_index(drop=True)
    F = fit_sheet(D)
    bad2 = F["err"] > (max(5.0, 4 * np.median(F["err"])) if sid != GENERAL else max(25.0, 4 * np.median(F["err"])))
    for r in D0[bad].itertuples():
        outl.append({"sheet": sid, "name": r.name, "engraved": r.engraved, "conf": r.conf, "stage": 1})
    for r in D[bad2].itertuples():
        outl.append({"sheet": sid, "name": r.name, "engraved": r.engraved, "conf": r.conf, "stage": 2})
    D = D[~bad2].reset_index(drop=True)
    F = fit_sheet(D)
    # thin-plate spline, ground km to pixels, and leave-one-out
    sm = float(len(D))
    tps = RBFInterpolator(F["X"], F["Y"], kernel="thin_plate_spline", smoothing=sm)
    loo = []
    for i in range(len(D)):
        k = np.arange(len(D)) != i
        p = RBFInterpolator(F["X"][k], F["Y"][k], kernel="thin_plate_spline", smoothing=sm)(F["X"][i:i + 1])[0]
        loo.append(float(np.hypot(*(p - F["Y"][i])) / F["s"]))
    lo, la = F["inv"](F["G"][:, 0], F["G"][:, 1]).T
    D["map_lon"], D["map_lat"] = np.round(lo, 5), np.round(la, 5)
    D["err_km"] = np.round(F["err"], 2)
    D["dE_km"], D["dN_km"] = np.round(F["G"][:, 0] - F["X"][:, 0], 2), np.round(F["G"][:, 1] - F["X"][:, 1], 2)
    D["err_aff_km"] = np.round(F["erra"], 2)
    D["loo_tps_km"] = np.round(loo, 2)
    # where the similarity puts the TRUE place on the sheet (pixels), for the arrows on the sheet view
    P = F["f"](F["X"])
    D["fit_x"], D["fit_y"] = np.round(P[:, 0]), np.round(-P[:, 1])
    rows.append(D)
    # sheet corners on the ground (affine inverse), for laying the sheet on the modern map
    W, H = IMI[sid]["w"], IMI[sid]["h"]
    corners = F["ainv"](np.array([[0, 0], [W, 0], [W, -H], [0, -H]], float))
    clo, cla = F["inv"](corners[:, 0], corners[:, 1]).T
    # bent grid: 10 km lines (25 km on the general map) of the local frame drawn on the sheet within the readings' hull + margin
    step = 25 if sid == GENERAL else 5
    hull = MultiPoint([tuple(p) for p in F["X"]]).convex_hull.buffer(step * (1.2 if sid == GENERAL else 1.5))
    xmin, ymin, xmax, ymax = hull.bounds
    lines = []
    for vert in (True, False):
        for v in np.arange(np.floor((xmin if vert else ymin) / step) * step, (xmax if vert else ymax) + step, step):
            t = np.arange(ymin if vert else xmin, (ymax if vert else xmax) + 0.5, step / 10)
            Pg = np.c_[np.full_like(t, v), t] if vert else np.c_[t, np.full_like(t, v)]
            seg = LineString(Pg).intersection(hull)
            for g in (seg.geoms if hasattr(seg, "geoms") else [seg]):
                if g.is_empty or g.length < step: continue
                c = np.array(g.coords)
                c = np.vstack([np.interp(np.linspace(0, len(c) - 1, max(2, int(g.length / (step / 10)))), np.arange(len(c)), c[:, j]) for j in range(2)]).T
                Q = tps(c)
                lines.append({"d": "v" if vert else "h", "c": np.round(np.c_[Q[:, 0], -Q[:, 1]]).astype(int).tolist(),
                              "s": np.round(np.c_[F["f"](c)[:, 0], -F["f"](c)[:, 1]]).astype(int).tolist()})
    grids[sid] = {"step_km": step, "lines": lines}
    OUT[sid] = {"title": SHEETS[sid][0], "short": SHEETS[sid][1], "year": SHEETS[sid][2], "region": SHEETS[sid][4],
                "n_read": int(len(D0)), "n": int(len(D)), "n_out": int(len(D0) - len(D)),
                "n_conf1": int((D.conf == 1).sum()),
                "px_per_km": round(F["s"], 3), "km_per_1000px": round(1000 / F["s"], 2),
                "turn_deg": round(F["th"], 2), "aniso": round(F["aniso"], 3),
                "med_km": round(float(np.median(F["err"])), 2), "mean_km": round(float(F["err"].mean()), 2),
                "p90_km": round(float(np.percentile(F["err"], 90)), 2), "max_km": round(float(F["err"].max()), 2),
                "med_aff_km": round(float(np.median(F["erra"])), 2), "loo_tps_med_km": round(float(np.median(loo)), 2),
                "med_conf1_km": round(float(np.median(F["err"][D.conf.values == 1])), 2) if (D.conf == 1).sum() >= 3 else None,
                "worst": D.sort_values("err_km").iloc[-1][["name", "err_km"]].to_dict(),
                "centre": [round(F["lon0"], 4), round(F["lat0"], 4)],
                "corners": np.round(np.c_[clo, cla], 5).tolist(),
                "affine_px": np.round(F["C"], 6).tolist()}
    print(f"{sid} {SHEETS[sid][1]:24s} n={len(D):3d}/{len(D0):3d} {F['s']:.2f}px/km turn {F['th']:+.1f} aniso {F['aniso']:.2f} "
          f"med {np.median(F['err']):.2f} aff {np.median(F['erra']):.2f} loo {np.median(loo):.2f} km")

L = pd.concat(rows, ignore_index=True)
cols = ["sheet", "sheet_name", "region", "name", "engraved", "qid", "lon", "lat", "x", "y", "conf", "map_lon", "map_lat",
        "dE_km", "dN_km", "err_km", "err_aff_km", "loo_tps_km", "fit_x", "fit_y", "note"]
L[cols].to_csv(f"{DATA}/located.csv", index=False)
pd.DataFrame(outl, columns=["sheet", "name", "engraved", "conf", "stage"]).to_csv(f"{DATA}/outliers.csv", index=False)
jsave(grids, f"{WORK}/grids.json")
jsave(OUT, f"{DATA}/fits.json", indent=1)
print("outliers", len(outl)); print(pd.DataFrame(outl).to_string())
