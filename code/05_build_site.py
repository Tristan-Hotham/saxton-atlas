"""Step 5: index.html from page_template.html, results.json and site.json; per-sheet bent grids (data/grid/<id>.json,
web pixels, loaded when a sheet is opened)."""
import re
from common import *

R = jload(f"{DATA}/results.json"); site = jload(f"{DATA}/site.json"); G = jload(f"{WORK}/grids.json"); IMI = jload(f"{DATA}/images.json")
os.makedirs(f"{DATA}/grid", exist_ok=True)
for s, g in G.items():
    k = IMI[s]["k"]
    jsave([{"d": l["d"], "c": [[round(x * k, 1), round(y * k, 1)] for x, y in l["c"][::2] + [l["c"][-1]]]} for l in g["lines"]], f"{DATA}/grid/{s}.json")


def sub(t, R):
    def f(m):
        path, _, form = m.group(1).partition("|")
        v = get(R, path)
        if form == "f0": return f"{abs(float(v)):.0f}" if path.endswith("cornwall_deg") else f"{float(v):.0f}"
        return fmt(v, form or None)
    return re.sub(r"\{\{([a-z_0-9.]+(?:\|[a-z0-9]+)?)\}\}", f, t)


t = open(f"{ROOT}/code/page_template.html", encoding="utf-8").read()
rows = "".join(f"<tr><td>{s['short']} ({s['year']})</td><td class=r>{s['n']}</td><td class=r>{s['med_km']:.2f}</td><td class=r>{s['turn_deg']:+.1f}</td><td class=r>{s['aniso']:.2f}</td></tr>" for s in R["sheets"])
t = t.replace("{{TABLE}}", rows).replace("{{UNREAD}}", "; ".join(R["unread"]))
t = t.replace("{{SITE}}", json.dumps(site, separators=(",", ":"), ensure_ascii=False))
t = sub(t, R)
assert "{{" not in t.replace("https://doi.org/10.5281/zenodo.24052723", "").replace("https://blog.tristanhotham.com/2026/10/31/saxton-atlas/", "").replace("10.5281/zenodo.24052723", ""), re.findall(r"\{\{[^}]+\}\}", t)[:5]
for bad in ("—", "–", "DSIT", "DCMS"):
    assert bad not in t, bad
open(f"{ROOT}/index.html", "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
