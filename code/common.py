"""Shared paths, constants and helpers for the saxton-atlas study ("Saxton's atlas, measured").

Raw inputs (read in place, never modified):
  RAW/Saxton_s_atlas_of_England_-_btv1b55007148q_(NNN_of_131).jpg
      Christopher Saxton, Atlas of England and Wales (engraved 1574 to 1579, published 1579), the Bibliotheque nationale
      de France copy (ark:/12148/btv1b55007148q), Wikimedia Commons scans at 3,840 px wide, public domain (PD-Art).
      Pages 014 to 116 (every third page) are the general map and the 34 county maps; page 119 is a map of Scotland
      (Scotiae Tabula, not by Saxton) bound in with them and is not used.
  RAW/Devoniae_..., Dorcestriae_..., Promontorium_..., Sc_Saxton_Wiltonia.jpg, Somersetensem_...
      Five single sheets from other copies on Commons (Devon, Dorset, Cornwall, Wiltshire, Somerset). They duplicate BnF
      sheets and are used only as a copy-to-copy check (06 in 02_fit.py), not in the main results.
  SETTLE = raw_new8/uk_settlements.tsv   Wikidata UK settlements (CC0): item, label, point, population, type.
  GEO/counties_uk.geojson (ONS/OS ceremonial and preserved counties, OGL), ne_10m_admin_0_countries.geojson (Natural Earth).

Inputs written by hand (data/):
  readings.csv   one row per place read on a sheet: sheet, name as engraved where legible, the place, its Wikidata item
                 or 'hand' with typed coordinates, pixel x, y on the full-size scan (the church or town symbol, a bridge,
                 a river mouth), and a confidence flag: 1 the name is legible and the place certain, 2 probable (name
                 partly legible, symbol in the right place), 3 the place is certain but its exact point is doubtful.
"""
import json, gzip, os, re, unicodedata, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("SX_RAW", "/home/claude/newdata/raw_new8/saxton")
SETTLE = os.environ.get("SX_SETTLE", "/home/claude/newdata/raw_new8/uk_settlements.tsv")
GEO = os.environ.get("SX_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("SX_FONTS", "/home/claude/ref/fonts")
INK = os.environ.get("SX_INK", "/home/claude/studies/ink-map")
INKFONTS = os.path.join(INK, "fonts", "ttf")
GOUGH = os.environ.get("SX_GOUGH", "/home/claude/studies/gough-map/data/results.json")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
WORK = os.path.join(os.environ.get("SXTMP", "/home/claude/work/new8/saxton-atlas"), "work")
for d in (DATA, IMG, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "saxton-atlas"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
GOUGH_PAGE = "https://maps.tristanhotham.com/gough-map/"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"
BNF = "https://gallica.bnf.fr/ark:/12148/btv1b55007148q"
COMMONS = "https://commons.wikimedia.org/wiki/Category:Saxton%27s_atlas_of_England_-_btv1b55007148q"


def bnf(p):
    return f"{RAW}/Saxton_s_atlas_of_England_-_btv1b55007148q_({p:03d}_of_131).jpg"


# sheet id -> (title, short name, engraved date on the cartouche as commonly given, ceremonial or preserved counties
# used to choose candidate places, region)
SHEETS = {
    "p017": ("Kent, Sussex, Surrey and Middlesex", "Kent and Sussex", 1575, ["Kent", "East Sussex", "West Sussex", "Surrey", "Greater London"], "South-east"),
    "p020": ("Hampshire", "Hampshire", 1575, ["Hampshire"], "South-east"),
    "p023": ("Dorset", "Dorset", 1575, ["Dorset"], "South-west"),
    "p026": ("Wiltshire", "Wiltshire", 1576, ["Wiltshire"], "South-west"),
    "p029": ("Somerset", "Somerset", 1575, ["Somerset", "Bristol"], "South-west"),
    "p032": ("Devon", "Devon", 1575, ["Devon"], "South-west"),
    "p035": ("Cornwall", "Cornwall", 1576, ["Cornwall"], "South-west"),
    "p038": ("Essex", "Essex", 1576, ["Essex"], "East"),
    "p041": ("Hertfordshire", "Hertfordshire", 1577, ["Hertfordshire"], "East"),
    "p044": ("Oxfordshire, Buckinghamshire and Berkshire", "Oxon, Bucks, Berks", 1574, ["Oxfordshire", "Buckinghamshire", "Berkshire"], "South-east"),
    "p047": ("Gloucestershire", "Gloucestershire", 1577, ["Gloucestershire", "Bristol"], "South-west"),
    "p050": ("Suffolk", "Suffolk", 1575, ["Suffolk"], "East"),
    "p053": ("Norfolk", "Norfolk", 1574, ["Norfolk"], "East"),
    "p056": ("Northamptonshire, Bedfordshire, Cambridgeshire, Huntingdonshire and Rutland", "Northants and Cambs", 1576, ["Northamptonshire", "Bedfordshire", "Cambridgeshire", "Rutland"], "Midlands"),
    "p059": ("Warwickshire and Leicestershire", "Warwick and Leicester", 1576, ["Warwickshire", "Leicestershire", "West Midlands"], "Midlands"),
    "p062": ("Staffordshire", "Staffordshire", 1577, ["Staffordshire", "West Midlands"], "Midlands"),
    "p065": ("Worcestershire", "Worcestershire", 1577, ["Worcestershire"], "Midlands"),
    "p068": ("Shropshire", "Shropshire", 1577, ["Shropshire"], "Midlands"),
    "p071": ("Herefordshire", "Herefordshire", 1577, ["Herefordshire"], "Midlands"),
    "p074": ("Lincolnshire and Nottinghamshire", "Lincs and Notts", 1576, ["Lincolnshire", "Nottinghamshire"], "Midlands"),
    "p077": ("Derbyshire", "Derbyshire", 1577, ["Derbyshire"], "Midlands"),
    "p080": ("Cheshire", "Cheshire", 1577, ["Cheshire"], "North"),
    "p083": ("Yorkshire", "Yorkshire", 1577, ["North Yorkshire", "South Yorkshire", "West Yorkshire", "East Riding of Yorkshire"], "North"),
    "p086": ("Lancashire", "Lancashire", 1577, ["Lancashire", "Merseyside", "Greater Manchester", "Cumbria"], "North"),
    "p089": ("Durham", "Durham", 1576, ["Durham"], "North"),
    "p092": ("Westmorland and Cumberland", "Cumberland", 1576, ["Cumbria"], "North"),
    "p095": ("Northumberland", "Northumberland", 1576, ["Northumberland"], "North"),
    "p098": ("Monmouthshire", "Monmouthshire", 1577, ["Gwent"], "Wales"),
    "p101": ("Glamorgan", "Glamorgan", 1578, ["Mid Glamorgan", "West Glamorgan", "South Glamorgan", "Dyfed"], "Wales"),
    "p104": ("Radnor, Brecknock, Cardigan and Carmarthen", "Mid and south Wales", 1578, ["Powys", "Dyfed"], "Wales"),
    "p107": ("Pembrokeshire", "Pembrokeshire", 1578, ["Dyfed"], "Wales"),
    "p110": ("Montgomery and Merioneth", "Montgomery", 1578, ["Powys", "Gwynedd"], "Wales"),
    "p113": ("Denbigh and Flint", "Denbigh and Flint", 1577, ["Clwyd"], "Wales"),
    "p116": ("Caernarfon and Anglesey", "Caernarfon and Anglesey", 1578, ["Gwynedd"], "Wales"),
}
EW = sorted({c for v in SHEETS.values() for c in v[3]} | {"Isle of Wight", "Merseyside", "Greater Manchester", "Tyne and Wear", "Greater London", "West Midlands", "Bristol", "South Yorkshire", "West Yorkshire", "East Riding of Yorkshire", "Gwent", "Powys", "Gwynedd", "Clwyd", "Dyfed", "Hertfordshire", "Cumbria", "Lancashire", "Northumberland", "Durham"})
SHEETS["p014"] = ("England and Wales (general map)", "General map", 1579, EW, "General")
GENERAL = "p014"          # Anglia, the general map of England and Wales (1579)
SCOTLAND = "p119"         # Scotiae Tabula, not Saxton's; not used
DUPES = {"Devoniae_Comitat_Rerumquae.jpg": "p032", "Dorcestriae_Comitatus_Vicinarumque_Regionum_nova_veraq_Descriptio_._1575.jpg": "p023",
         "Promontorium_._Proiectum_Cornubia_dicitur.jpg": "p035", "Sc_Saxton_Wiltonia.jpg": "p026",
         "Somersetensem_Comitat_(agri_fertilitate_Celebrem)_hec_ob_oculus_ponit_Tabula_Anno_1575_et_D_Elizabethe_Regine_Ao_17.jpg": "p029"}
REGIONS = [("South-west", "#A3261B"), ("South-east", "#8C6A43"), ("East", "#2E7F86"), ("Midlands", "#3D6E9E"), ("North", "#5B4B8A"), ("Wales", "#4E7D3A")]
RCOL = dict(REGIONS)


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def nonan(v):
    if isinstance(v, float) and v != v:
        return None
    if isinstance(v, list):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {k: nonan(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "abs": return f"{abs(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "absf1": return f"{abs(float(v)):.1f}"
    raise ValueError(f)


_TF = {}


def bng(lon, lat):
    """WGS84 to British National Grid, in km."""
    from pyproj import Transformer
    import numpy as np
    if "f" not in _TF:
        _TF["f"] = Transformer.from_crs(4326, 27700, always_xy=True)
    e, n = _TF["f"].transform(np.asarray(lon, float), np.asarray(lat, float))
    return np.asarray(e) / 1000.0, np.asarray(n) / 1000.0


def wgs(e_km, n_km):
    from pyproj import Transformer
    import numpy as np
    if "b" not in _TF:
        _TF["b"] = Transformer.from_crs(27700, 4326, always_xy=True)
    lo, la = _TF["b"].transform(np.asarray(e_km, float) * 1000, np.asarray(n_km, float) * 1000)
    return np.asarray(lo), np.asarray(la)


def similarity(X, Y):
    """Y ~ a X + b in complex numbers (one scale, one turn, a shift). X ground km (E, N); Y image px with y up.
    Returns scale (px per km), turn (deg, anticlockwise from ground to image), forward and inverse functions."""
    import numpy as np
    zx = X[:, 0] + 1j * X[:, 1]; zy = Y[:, 0] + 1j * Y[:, 1]
    A = np.c_[zx, np.ones(len(zx))]
    (a, b), *_ = np.linalg.lstsq(A, zy, rcond=None)
    f = lambda P: (lambda z: np.c_[z.real, z.imag])(a * (P[:, 0] + 1j * P[:, 1]) + b)
    inv = lambda Q: (lambda z: np.c_[z.real, z.imag])(((Q[:, 0] + 1j * Q[:, 1]) - b) / a)
    return float(abs(a)), float(np.degrees(np.angle(a))), f, inv


def affine(X, Y):
    import numpy as np
    A = np.c_[X, np.ones(len(X))]
    C, *_ = np.linalg.lstsq(A, Y, rcond=None)
    M = C[:2].T
    U, sv, Vt = np.linalg.svd(M)
    inv = lambda Q: np.linalg.solve(M, (Q - C[2]).T).T
    return M, C, float(sv[0] / sv[1]), (lambda P: np.c_[P, np.ones(len(P))] @ C), inv


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()
