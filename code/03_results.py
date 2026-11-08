"""Step 3: every number used anywhere (data/results.json) and the page data (data/site.json)."""
import numpy as np, pandas as pd
from common import *

L = pd.read_csv(f"{DATA}/located.csv")
R0 = pd.read_csv(f"{DATA}/readings.csv")
F = jload(f"{DATA}/fits.json")
OUTL = pd.read_csv(f"{DATA}/outliers.csv")
IMI = jload(f"{DATA}/images.json")
GO = jload(GOUGH)

C = L[L.sheet != GENERAL]
Gm = L[L.sheet == GENERAL]
cs = [s for s in F if s != GENERAL]
Res = {"meta": {"slug": SLUG, "page": PAGE, "repo": REPO, "year": 2026}}
Res["counts"] = {
    "readings": int(len(R0)), "readings_county": int((R0.sheet != GENERAL).sum()), "readings_general": int((R0.sheet == GENERAL).sum()),
    "used": int(len(L)), "used_county": int(len(C)), "outliers": int(len(OUTL)),
    "sheets_county_read": len(cs), "sheets_county_total": 34, "sheets_county_unread": 34 - len(cs),
    "places_unique": int(L.qid.nunique()), "conf1": int((C.conf == 1).sum()), "conf2": int((C.conf == 2).sum()), "conf3": int((C.conf == 3).sum()),
    "conf1_pct": round(100 * float((C.conf == 1).mean())), "per_sheet_median": int(np.median([F[s]["n"] for s in cs])),
    "per_sheet_min": int(min(F[s]["n"] for s in cs)), "per_sheet_max": int(max(F[s]["n"] for s in cs)),
    "files_dup": len(DUPES), "scans": 41}
unread = [s for s in SHEETS if s not in F]
Res["unread"] = [SHEETS[s][0] for s in sorted(unread)]

e = C.err_km.values
Res["county"] = {"med_km": round(float(np.median(e)), 2), "mean_km": round(float(e.mean()), 2),
                 "within1_pct": round(100 * float((e <= 1).mean())), "within2_pct": round(100 * float((e <= 2).mean())),
                 "within5_pct": round(100 * float((e <= 5).mean())), "over5": int((e > 5).sum()),
                 "med_aff_km": round(float(C.err_aff_km.median()), 2), "loo_tps_med_km": round(float(C.loo_tps_km.median()), 2),
                 "med_conf1_km": round(float(C[C.conf == 1].err_km.median()), 2), "med_conf2_km": round(float(C[C.conf == 2].err_km.median()), 2),
                 "sheet_med_best": min(cs, key=lambda s: F[s]["med_km"]), "sheet_med_worst": max(cs, key=lambda s: F[s]["med_km"]),
                 "sheet_meds_median": round(float(np.median([F[s]["med_km"] for s in cs])), 2)}
Res["county"]["best_name"] = F[Res["county"]["sheet_med_best"]]["short"]; Res["county"]["best_km"] = F[Res["county"]["sheet_med_best"]]["med_km"]
Res["county"]["worst_name"] = F[Res["county"]["sheet_med_worst"]]["short"]; Res["county"]["worst_km"] = F[Res["county"]["sheet_med_worst"]]["med_km"]
top = C.sort_values("err_km", ascending=False).head(6)
Res["county"]["biggest"] = [{"name": r.name, "sheet": r.sheet_name, "km": round(r.err_km, 1)} for r in top.itertuples()]

# turns: true north on the sheet
turns = {s: F[s]["turn_deg"] for s in cs}
tx = [t for s, t in turns.items() if s != "p035"]
Res["turn"] = {"median_deg": round(float(np.median(tx)), 1), "mean_deg": round(float(np.mean(tx)), 1),
               "q1_deg": round(float(np.percentile(tx, 25)), 1), "q3_deg": round(float(np.percentile(tx, 75)), 1),
               "n_pos": int(sum(t > 0 for t in turns.values())), "n": len(turns), "n_5_to_16": int(sum(5 <= t <= 16 for t in turns.values())),
               "cornwall_deg": turns["p035"], "max_sheet": max(tx and [s for s in cs if s != "p035"], key=lambda s: turns[s]),
               "general_deg": F[GENERAL]["turn_deg"], "neg": [{"sheet": F[s]["short"], "deg": t} for s, t in turns.items() if t < 0]}
Res["turn"]["max_name"] = F[Res["turn"]["max_sheet"]]["short"]; Res["turn"]["max_deg"] = turns[Res["turn"]["max_sheet"]]
# Borough measured the compass variation at Limehouse in October 1580 as about 11 degrees 14 minutes east (Encyclopaedia Britannica 1911, "Magnetism, Terrestrial")
Res["turn"]["borough_deg"] = 11.2

# scale
pk = {s: F[s]["px_per_km"] for s in cs}
smax, smin = max(pk, key=pk.get), min(pk, key=pk.get)
Res["scale"] = {"max_sheet": F[smax]["short"], "min_sheet": F[smin]["short"], "max_px_km": pk[smax], "min_px_km": pk[smin],
                "ratio": round(pk[smax] / pk[smin], 1), "general_px_km": F[GENERAL]["px_per_km"],
                "county_over_general_median": round(float(np.median([pk[s] / F[GENERAL]["px_per_km"] for s in cs])), 1),
                "aniso_median": round(float(np.median([F[s]["aniso"] for s in cs])), 2), "aniso_max": max(F[s]["aniso"] for s in cs),
                "aniso_max_name": F[max(cs, key=lambda s: F[s]["aniso"])]["short"]}

# sheet to sheet: places read on two county sheets
pairs = []
C = C.assign(key=np.where(C.qid == "hand", C["name"], C.qid))
for q, g in C.groupby("key"):
    if len(g) < 2: continue
    a, b = g.iloc[0], g.iloc[1]
    import math
    p1, p2 = math.radians(a.map_lat), math.radians(b.map_lat)
    dl = math.radians(b.map_lon - a.map_lon)
    d = 6371 * math.acos(min(1, math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)))
    pairs.append({"name": a["name"], "a": a.sheet_name, "b": b.sheet_name, "km": round(d, 2), "err_a": a.err_km, "err_b": b.err_km})
P = pd.DataFrame(pairs)
Res["shared"] = {"n": int(len(P)), "med_km": round(float(P.km.median()), 2), "max_km": float(P.km.max()), "max_name": P.sort_values("km").iloc[-1]["name"],
                 "rows": P.sort_values("km").to_dict("records")}

# regions (county sheets)
reg = {}
for rn, _ in REGIONS:
    g = C[C.region == rn]
    if len(g) == 0: continue
    reg[rn] = {"n": int(len(g)), "sheets": int(g.sheet.nunique()), "med_km": round(float(g.err_km.median()), 2)}
Res["regions"] = reg

# general map and the Gough Map
Res["general"] = {"n": F[GENERAL]["n"], "med_km": F[GENERAL]["med_km"], "p90_km": F[GENERAL]["p90_km"], "turn_deg": F[GENERAL]["turn_deg"],
                  "aniso": F[GENERAL]["aniso"], "med_aff_km": F[GENERAL]["med_aff_km"], "within10_pct": round(100 * float((Gm.err_km <= 10).mean())),
                  "max_km": F[GENERAL]["max_km"], "worst": F[GENERAL]["worst"]["name"]}
Res["gough"] = {"med_km": GO["shape"]["err_median_km"], "n": GO["located"].get("n", None) if isinstance(GO["located"], dict) else None,
                "ratio_general": round(GO["shape"]["err_median_km"] / F[GENERAL]["med_km"], 1),
                "ratio_county": round(GO["shape"]["err_median_km"] / Res["county"]["med_km"], 1), "page": GOUGH_PAGE}

# the sheet table
Res["sheets"] = [{"id": s, **{k: F[s][k] for k in ("title", "short", "year", "region", "n", "n_out", "px_per_km", "turn_deg", "aniso", "med_km", "med_aff_km", "loo_tps_med_km", "max_km")},
                  "worst": F[s]["worst"]["name"]} for s in sorted(F, key=lambda s: (s != GENERAL, s))]
jsave(Res, f"{DATA}/results.json", indent=1)

# page data: per sheet, the readings (web pixel scale) and the fit info; grids are loaded per sheet from grids.json
site = {"sheets": {}}
for s in F:
    k = IMI[s]["k"]
    g = L[L.sheet == s]
    site["sheets"][s] = {"t": F[s]["title"], "sh": F[s]["short"], "y": F[s]["year"], "r": F[s]["region"], "w": IMI[s]["web_w"], "h": IMI[s]["web_h"], "k": round(k, 6),
                         "n": F[s]["n"], "med": F[s]["med_km"], "turn": F[s]["turn_deg"], "pxkm": F[s]["px_per_km"], "aniso": F[s]["aniso"],
                         "corners": F[s]["corners"],
                         "p": [[r.name, r.engraved if isinstance(r.engraved, str) else "", round(r.x * k, 1), round(r.y * k, 1), round(r.fit_x * k, 1), round(r.fit_y * k, 1),
                                r.lon, r.lat, r.map_lon, r.map_lat, r.err_km, int(r.conf), r.qid] for r in g.itertuples()]}
site["unread"] = Res["unread"]
jsave(site, f"{DATA}/site.json")
print(json.dumps({k: Res[k] for k in ("counts", "county", "turn", "scale", "general", "gough", "regions")}, indent=1)[:4000])
print("shared", Res["shared"]["n"], Res["shared"]["med_km"], Res["shared"]["max_km"], Res["shared"]["max_name"])
