"""Step 7: blog post and meta, README, LICENSE, Reddit post text, Zenodo metadata and the data and code zip."""
import zipfile, glob, re
from common import *

R = jload(f"{DATA}/results.json"); F = jload(f"{DATA}/fits.json")
c, t, sc, g, go, n, sh = R["counts"], R["turn"], R["scale"], R["general"], R["gough"], R["county"], R["shared"]
PORT = "https://maps.tristanhotham.com/portolan-charts/"
B = f"{ROOT}/release/blog"


def P(x): return f"<!-- wp:paragraph -->\n<p>{x}</p>\n<!-- /wp:paragraph -->\n\n"
def H(x): return f"<!-- wp:heading -->\n<h2 class=\"wp-block-heading\">{x}</h2>\n<!-- /wp:heading -->\n\n"
def BTN(items):
    s = "<!-- wp:buttons -->\n<div class=\"wp-block-buttons\">"
    s += "".join(f"<!-- wp:button -->\n<div class=\"wp-block-button\"><a class=\"wp-block-button__link wp-element-button\" href=\"{u}\">{l}</a></div>\n<!-- /wp:button -->\n" for l, u in items)
    return s.rstrip("\n") + "</div>\n<!-- /wp:buttons -->\n\n"
def IMG(f, alt, cap): return f"{{{{IMG|{f}|{alt}|{cap}}}}}\n\n"
def QUOTE(x): return f"<!-- wp:pullquote -->\n<figure class=\"wp-block-pullquote\"><blockquote><p>{x}</p></blockquote></figure>\n<!-- /wp:pullquote -->\n\n"
def LI(items): return "<!-- wp:list -->\n<ul class=\"wp-block-list\">" + "".join(f"<!-- wp:list-item -->\n<li>{i}</li>\n<!-- /wp:list-item -->\n" for i in items).rstrip("\n") + "</ul>\n<!-- /wp:list -->\n"

post = P(f"<em>In the 1570s Christopher Saxton mapped every county of England and Wales. I read {c['readings']} towns on his maps and checked each against where it really is. A typical town is about {n['med_km']:.1f} km out, and on almost every sheet north leans the same way, by about as much as a compass did in Elizabethan London.</em>")
post += BTN([("Explore the interactive version", PAGE), ("Read the paper", "https://doi.org/10.5281/zenodo.24052723")])
post += P(f"Saxton's atlas is one of the great objects of English mapping. Between 1574 and 1579 he surveyed the counties, and his plates were engraved in London and bound in 1579 with a general map of England and Wales. Thirty five maps in all, each crowded with church towers, parks ringed by fences, hills like molehills and rivers like veins. For two hundred years most county maps in England were copies of his.")
post += P(f"I wanted to know how good they are, in numbers. Earlier this year I measured the <a href=\"{GOUGH_PAGE}\">Gough Map</a>, drawn about two centuries before Saxton, and the medieval <a href=\"{PORT}\">portolan charts</a>. Saxton is the obvious next step: the first maps of England made from a real survey.")
post += IMG("b_sheets.png", "Eight sheets from Saxton's atlas in a grid: the general map of England and Wales, Devon, Yorkshire, Hertfordshire, Lancashire, Norfolk, Cornwall and Glamorgan, each hand coloured with decorative cartouches", "Eight of the 35 maps in the Bibliothèque nationale de France copy of Saxton's atlas.")
post += H("Reading the maps")
post += P(f"The Bibliothèque nationale de France copy of the atlas is on Wikimedia Commons as high resolution scans. I went through all {c['sheets_county_read']} county maps and the general map, zooming into each town symbol, reading the engraved name (Hytchin, Hartforde, Kedermister) and matching it to the town's position today. That gave {c['readings']} readings, from {c['per_sheet_min']} on Pembrokeshire to {c['per_sheet_max']} on Yorkshire. {c['conf1_pct']}% of them are certain; the rest are probable, usually because the name is worn or tucked behind a hill.")
post += IMG("b_reading.png", "A close up of the Worcestershire sheet with blue rings on town symbols such as Worcester, Droitwich, Bromsgrove and Pershore and short red arrows from each", "Worcestershire, 1577. Each red arrow runs from the town I read to where the real town falls, at the sheet's own scale and turn. Most arrows are tiny.")
post += H("A town within a mile or so")
post += P(f"Each county is drawn at its own scale (Hertfordshire is {sc['ratio']:.1f} times larger than Yorkshire), so I fitted each sheet to the ground separately, with one scale, one turn and one shift. Then I asked how far each town is from where it should be. The median answer across {c['used_county']} towns is {n['med_km']:.2f} km. {n['within1_pct']}% of towns are within 1 km and all but {n['over5']} within 5 km.")
post += P(f"The best sheet is {n['best_name']}, with a median of {n['best_km']:.2f} km; the weakest is {n['worst_name']} at {n['worst_km']:.2f} km. Letting each sheet stretch and shear barely helps (the median drops to {n['med_aff_km']:.2f} km), because the shapes are true. And where the same town appears on two neighbouring sheets, the two sheets agree on where it is to within {sh['med_km']:.1f} km, as a rule.")
post += IMG("b_errors.png", f"Bar chart of median misplacement for {c['sheets_county_read']} county sheets, from about {n['best_km']:.2f} km for {n['best_name']} to about {n['worst_km']:.2f} km for {n['worst_name']}", "Median misplacement on each county sheet, coloured by region.")
post += IMG("b_map.png", "Map of England and Wales with several hundred dots, mostly blue and pale blue for under 2 km, with a few orange and red ones scattered in Devon and the fens", "Every town I read, coloured by how far its own sheet puts it from the truth.")
post += H("North leans west")
post += P(f"The fits also say which way each sheet is turned. I expected a jumble. Instead, on {t['n_pos']} of {t['n']} county sheets true north is turned anticlockwise: the top of the paper points a little east of true north. Leaving Cornwall aside, the median lean is {t['median_deg']:.1f}°, and the middle half of sheets sit between {t['q1_deg']:.1f}° and {t['q3_deg']:.1f}°.")
post += QUOTE(f"On {t['n_pos']} of {t['n']} county sheets, north leans west by a median of {t['median_deg']:.1f}° (Cornwall excluded): about what a compass needle did in London in 1580.")
post += P(f"That number has a likely explanation. A compass needle does not point to true north, and in 1580 the navigator William Borough measured the difference at Limehouse as about 11¼° east. If Saxton took his bearings by compass and drew magnetic north at the top of the plate, the sheets would lean exactly this way, by roughly this much. The same tilt turns up on the <a href=\"{PORT}\">portolan charts</a>, made with compasses two centuries earlier. The general map of 1579 is different: it is turned only {abs(t['general_deg']):.1f}°, and the other way, as if whoever assembled it set it to true north. Cornwall is the odd one out, turned {abs(t['cornwall_deg']):.0f}° the other way; one possibility is that the long peninsula was turned to fit the plate.")
post += IMG("b_turns.png", "Dot plot of the turn of north on each sheet: most dots between 5 and 16 degrees, Cornwall at minus 24, with a dashed line at Borough's 11¼ degrees", "How far true north is turned on each sheet. The dashed line is the compass variation Borough measured in London in 1580.")
post += IMG("b_grid.png", "The Cornwall sheet with a red and blue grid of true north to south and east to west lines bent across it, clearly tilted", f"Cornwall, 1576, with the true 5 km grid bent onto it. The sheet is turned {abs(t['cornwall_deg']):.0f}° the other way from the rest, perhaps to fit the peninsula on the plate.")
post += H("Two centuries after the Gough Map")
post += P(f"The general map squeezes the whole country onto one sheet, at about a seventh of the scale of a typical county map. Its median town is {g['med_km']:.1f} km out. The Gough Map of about 1360, measured the same way, misplaces its median town by {go['med_km']:.1f} km: Saxton's general map is about {go['ratio_general']:.0f} times as accurate, and his county maps, at their larger scale, far better still.")
post += IMG("b_general.png", "Map of England and Wales with short red arrows from 46 towns, exaggerated five times, mostly small and pointing in mixed directions", "The general map of 1579. Arrows from each real town towards where Saxton puts it, five times longer than life.")
post += H("How I did this")
post += P(f"I read every position by eye on zoomed crops of the scans, guided by a prediction from the towns already read, and matched each name to a Wikidata settlement point. True positions were put on a flat grid in kilometres centred on each sheet. For each sheet I fitted a similarity (scale, turn, shift) and an affine transformation by least squares, and a thin plate spline to bend the true grid onto the sheet. " + (f"{c['outliers']} readings that sat far off their sheet's fit were dropped as probable misreadings." if c['outliers'] else "I then checked every reading a second time on a zoomed crop, moved symbols I had placed off target and dropped identifications I could not confirm; after that no reading sat far enough off its sheet's fit (more than 5 km and four times the sheet's median) to be dropped as a misreading.") + f" Wikidata points mark modern town centres, so a few hundred metres of each error are mine, not Saxton's. The code, the readings and the fits are all on GitHub.")
post += BTN([("Explore the interactive version", PAGE), ("Read the paper", "https://doi.org/10.5281/zenodo.24052723"), ("Data and code", REPO)])
post += "<!-- wp:heading {\"level\":3} -->\n<h3 class=\"wp-block-heading\">Notes and sources</h3>\n<!-- /wp:heading -->\n\n"
post += LI([f"Christopher Saxton, atlas of England and Wales, 1574 to 1579, Bibliothèque nationale de France (<a href=\"{BNF}\">ark:/12148/btv1b55007148q</a>), public domain scans on Wikimedia Commons.",
            "Town positions: Wikidata (CC0). Coastlines: Natural Earth (public domain). Base map on the interactive page: OpenFreeMap, © OpenStreetMap contributors.",
            "William Borough, A Discours of the Variation of the Cumpas (1581); the 1580 Limehouse value as given in the Encyclopaedia Britannica (1911), article Magnetism, Terrestrial.",
            "Background: Ifor M. Evans and Heather Lawrence, Christopher Saxton, Elizabethan Map-maker (1979).",
            f"Comparison: my study of <a href=\"{GOUGH_PAGE}\">the Gough Map</a>.", AI])
for bad in ("—", "–", "--"):
    assert bad not in re.sub(r"<!--.*?-->", "", post), bad
open(f"{B}/post.html", "w").write(post)
for m in re.findall(r"\{\{IMG\|([^|]+)\|", post):
    assert os.path.exists(f"{B}/{m}"), m
jsave({"title": "Saxton's atlas, measured", "slug": SLUG,
       "excerpt": f"I read {c['readings']} towns on Christopher Saxton's maps of England and Wales (1574 to 1579). A typical town is {n['med_km']:.1f} km out, and on {t['n_pos']} of {t['n']} county sheets north leans west by about {t['median_deg']:.0f} degrees (Cornwall excluded), close to the compass variation of the day.",
       "seo_description": f"Saxton's 1579 atlas measured: towns a median {n['med_km']:.1f} km out and north leaning {t['median_deg']:.0f} degrees west (Cornwall aside), like a compass.",
       "tags": ["maps", "history", "Christopher Saxton", "history of cartography", "Tudor England", "old maps", "data visualisation"],
       "header_alt": f"Title card on parchment reading Saxton's atlas, measured, in black and red, beside a detail of Saxton's hand coloured Worcestershire map, with the line {c['readings']} towns read on {c['sheets_county_read'] + 1} maps of 1574 to 1579."},
      f"{B}/meta.json", indent=1)
assert len(jload(f"{B}/meta.json")["seo_description"]) < 160

# README
tab = "\n".join(f"| {s['short']} | {s['year']} | {s['n']} | {s['med_km']:.2f} | {s['turn_deg']:+.1f} | {s['aniso']:.2f} |" for s in R["sheets"])
readme = f"""# Saxton's atlas, measured

Christopher Saxton's atlas of England and Wales (engraved 1574 to 1579) set against the real ground: {c['readings']} towns read by eye on all {c['sheets_county_read']} county maps and the general map in the Bibliothèque nationale de France copy, each sheet fitted to true positions.

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24052723}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/saxton-atlas/}}
Code and data: {REPO}

## Headline results

- Accuracy: across {c['used_county']} county readings the median town is {n['med_km']:.2f} km from where its sheet puts it (each sheet at its own scale and turn); {n['within1_pct']}% within 1 km, all but {n['over5']} within 5 km. Sheet medians run from {n['best_km']:.2f} km ({n['best_name']}) to {n['worst_km']:.2f} km ({n['worst_name']}).
- Shape: an affine fit only brings the median to {n['med_aff_km']:.2f} km; median stretch {sc['aniso_median']:.2f}. Scales differ by a factor of {sc['ratio']:.1f} ({sc['max_sheet']} to {sc['min_sheet']}).
- North: true north is turned anticlockwise on {t['n_pos']} of {t['n']} county sheets, median {t['median_deg']:.1f}° leaving Cornwall aside (middle half {t['q1_deg']:.1f}° to {t['q3_deg']:.1f}°), close to the compass variation of about 11¼° east measured in London in 1580 (Borough). Cornwall is turned {t['cornwall_deg']:+.1f}°, perhaps to fit the plate; the general map {t['general_deg']:+.1f}°.
- Sheet to sheet: {sh['n']} towns read on two sheets agree to a median {sh['med_km']:.2f} km.
- General map: median {g['med_km']:.1f} km over {g['n']} towns, against {go['med_km']:.1f} km for the Gough Map (about 1360) measured the same way.

## Fits by sheet

| Map | Year | Towns | Median km | Turn ° | Stretch |
|:-|-:|-:|-:|-:|-:|
{tab}

## Files

| File | What it is |
|:-|:-|
| `index.html` | The interactive page (MapLibre GL JS 4.7.1; OpenFreeMap base map in the modern view). |
| `header.png` | Social card, 1200 x 630. |
| `img/sheets/`, `img/thumbs/` | The 35 BnF sheets at 2,000 px and 480 px (public domain). |
| `data/readings.csv` | My input: each place read (sheet, name, engraved spelling, Wikidata item, true lon/lat, full-size scan pixel x, y, confidence 1 certain, 2 probable, 3 doubtful point). |
| `data/located.csv` | The readings used, with the ground position each sheet gives, misplacement under similarity and affine fits, leave-one-out spline check and fitted pixels. |
| `data/outliers.csv` | Readings dropped as probable misreadings. |
| `data/fits.json`, `data/results.json`, `data/site.json`, `data/images.json` | Per-sheet fits; every number quoted; page data; image sizes. |
| `data/grid/<sheet>.json` | The true 5 km grid (25 km on the general map) bent onto each sheet, in web image pixels. |
| `code/` | Scripts, run in order, and the page template. `00_reading_aid.py` makes the crops I read from. |
| `release/` | Paper, blog post and figures, Zenodo files. |
| `reddit/` | Collage and post text. |

## Method in brief

- Sheets identified from their cartouches; the BnF files are pages 014 (general map) to 116 of 131; page 119 is a map of Scotland not by Saxton. Five further single sheets from other copies duplicate Devon, Dorset, Cornwall, Wiltshire and Somerset and were not used.
- Readings by eye on crops of the 3,840 px scans, predicted from towns already read; true positions from Wikidata (a few typed by hand).
- Per sheet: azimuthal equidistant frame in km about the readings' centre; similarity and affine least squares; misplacement = ground distance between the true place and the sheet position taken back through the inverse similarity. Outliers beyond max(5 km, 4 x median) dropped ({c['outliers']}). Thin plate spline (smoothing = n) for the bent grid and a leave-one-out check.
- Caveats: one reader; modern settlement points rather than historic churches; scan skew of perhaps a degree; scale bars not measured.

## How to rerun

Needs Python 3 with numpy, pandas, geopandas, shapely, pyproj, scipy, matplotlib and Pillow; xelatex (TeX Gyre Pagella); node with Playwright for `code/qa.js`. Raw paths are in `code/common.py`.

```
python3 code/01_images.py
python3 code/02_fit.py
python3 code/03_results.py
python3 code/04_figures.py
python3 code/05_build_site.py
python3 code/06_paper.py
python3 reddit/collage.py
python3 code/07_release.py
```

## Sources and licences

- Christopher Saxton, atlas of England and Wales, BnF {BNF}, scans via Wikimedia Commons, public domain.
- Wikidata (CC0); Natural Earth (public domain); OpenFreeMap and © OpenStreetMap contributors (ODbL) for the page's base map.
- Borough, W. (1581) A Discours of the Variation of the Cumpas; Encyclopaedia Britannica (1911) Magnetism, Terrestrial; Evans, I. M. and Lawrence, H. (1979) Christopher Saxton, Elizabethan Map-maker.
- Code MIT; text, figures and derived data CC BY 4.0.

## Citation

Hotham, T. (2026) Saxton's atlas, measured. Zenodo. {{https://doi.org/10.5281/zenodo.24052723}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(f"{ROOT}/README.md", "w").write(readme)
open(f"{ROOT}/LICENSE", "w").write("""Code: MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text, figures and derived data: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
The scans of Saxton's atlas are public domain (BnF via Wikimedia Commons). Wikidata content is CC0.
""")

# Reddit post
open(f"{ROOT}/reddit/post.md", "w").write(f"""# [OC] I measured Saxton's 1579 atlas of England and Wales: {c['readings']} towns, a median error of {n['med_km']:.1f} km, and north leans {t['median_deg']:.0f}° west on {t['n_pos']} of {t['n']} county maps (Cornwall excluded from the median), like a compass

I read {c['readings']} towns on Christopher Saxton's county maps (the first county atlas of England and Wales, engraved 1574 to 1579) and fitted each sheet to the real positions. Each county is drawn at its own scale, but within a sheet the median town is only {n['med_km']:.2f} km from where it should be. The surprise: true north is turned anticlockwise on almost every sheet, by a median {t['median_deg']:.1f}° (Cornwall excluded: it is turned the other way, perhaps to fit the plate), close to the ~11¼° east compass variation measured in London in 1580. The general map is not turned ({t['general_deg']:+.1f}°).

Interactive version (pick a county, see the true grid bent over it, fade to the modern map): {PAGE}

**Source comment:** Data: BnF copy of Saxton's atlas (scans on Wikimedia Commons, public domain); town positions from Wikidata (CC0). Tools: Python (numpy, scipy, matplotlib), MapLibre. Positions read by hand on zoomed scans; similarity, affine and thin plate spline fits per sheet. Code and data: {REPO}
""")

# Zenodo
Z = f"{ROOT}/release/zenodo"
shutil = __import__("shutil")
shutil.copy(f"{ROOT}/release/paper/Hotham_Saxton_Atlas.pdf", Z)
with zipfile.ZipFile(f"{Z}/{SLUG}_data_and_code.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for f in glob.glob(f"{DATA}/**/*", recursive=True) + glob.glob(f"{ROOT}/code/*.*") + [f"{ROOT}/README.md", f"{ROOT}/LICENSE", f"{ROOT}/reddit/collage.py"]:
        if os.path.isfile(f) and "__pycache__" not in f: zf.write(f, os.path.relpath(f, ROOT))
jsave({"title": "Saxton's Atlas, Measured: The Accuracy, Scale and Orientation of the First County Atlas of England and Wales (1574 to 1579)",
       "upload_type": "publication", "publication_type": "workingpaper",
       "description": f"<p>I read {c['readings']} positions on all {c['sheets_county_read']} county maps and on the general map of Christopher Saxton's atlas of England and Wales (BnF copy), matched them to Wikidata settlement points and fitted each sheet with similarity, affine and thin plate spline transformations. The median town is misplaced by {n['med_km']:.2f} km at its sheet's own scale and orientation ({n['within2_pct']}% within 2 km); sheet medians range from {n['best_km']:.2f} to {n['worst_km']:.2f} km and shapes are barely stretched (median {sc['aniso_median']:.2f}). True north is turned anticlockwise on {t['n_pos']} of {t['n']} county sheets by a median of {t['median_deg']:.1f} degrees (Cornwall excluded), close to the magnetic variation of about 11.25 degrees east measured in London in 1580, while the general map is turned {t['general_deg']:.1f} degrees. On the general map the median town is misplaced by {g['med_km']:.1f} km, against {go['med_km']:.1f} km for the Gough Map measured the same way.</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>.</p>",
       "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
       "keywords": ["Christopher Saxton", "history of cartography", "map accuracy", "early modern maps", "England", "Wales", "magnetic declination", "thin plate spline", "bidimensional regression"],
       "license": "cc-by-4.0", "language": "eng",
       "related_identifiers": [{"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"}, {"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"}]},
      f"{Z}/metadata.json", indent=1)
print("release done", os.path.getsize(f"{Z}/{SLUG}_data_and_code.zip") // 1024, "KB zip")
