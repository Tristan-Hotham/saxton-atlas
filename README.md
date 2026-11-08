# Saxton's atlas, measured

Christopher Saxton's atlas of England and Wales (engraved 1574 to 1579) set against the real ground: 857 towns read by eye on all 34 county maps and the general map in the Bibliothèque nationale de France copy, each sheet fitted to true positions.

Interactive page: https://maps.tristanhotham.com/saxton-atlas/
Paper: {https://doi.org/10.5281/zenodo.24052723}
Blog post: {https://blog.tristanhotham.com/2026/10/31/saxton-atlas/}
Code and data: https://github.com/Tristan-Hotham/saxton-atlas

## Headline results

- Accuracy: across 811 county readings the median town is 1.37 km from where its sheet puts it (each sheet at its own scale and turn); 32% within 1 km, all but 5 within 5 km. Sheet medians run from 0.68 km (Worcestershire) to 2.66 km (Devon).
- Shape: an affine fit only brings the median to 1.28 km; median stretch 1.05. Scales differ by a factor of 2.6 (Hertfordshire to Yorkshire).
- North: true north is turned anticlockwise on 31 of 34 county sheets, median 8.4° leaving Cornwall aside (middle half 7.6° to 10.0°), close to the compass variation of about 11¼° east measured in London in 1580 (Borough). Cornwall is turned -24.0°, perhaps to fit the plate; the general map -0.9°.
- Sheet to sheet: 16 towns read on two sheets agree to a median 2.30 km.
- General map: median 4.2 km over 46 towns, against 17.6 km for the Gough Map (about 1360) measured the same way.

## Fits by sheet

| Map | Year | Towns | Median km | Turn ° | Stretch |
|:-|-:|-:|-:|-:|-:|
| General map | 1579 | 46 | 4.23 | -0.9 | 1.02 |
| Kent and Sussex | 1575 | 28 | 1.34 | +7.8 | 1.01 |
| Hampshire | 1575 | 21 | 1.62 | +7.8 | 1.08 |
| Dorset | 1575 | 19 | 0.97 | +6.5 | 1.05 |
| Wiltshire | 1576 | 28 | 1.15 | +4.2 | 1.10 |
| Somerset | 1575 | 22 | 1.29 | +1.2 | 1.02 |
| Devon | 1575 | 22 | 2.66 | -3.1 | 1.14 |
| Cornwall | 1576 | 20 | 1.60 | -24.0 | 1.02 |
| Essex | 1576 | 17 | 1.97 | +12.4 | 1.05 |
| Hertfordshire | 1577 | 24 | 1.27 | +12.7 | 1.09 |
| Oxon, Bucks, Berks | 1574 | 28 | 0.93 | +10.1 | 1.02 |
| Gloucestershire | 1577 | 24 | 1.34 | +9.2 | 1.07 |
| Suffolk | 1575 | 24 | 1.76 | +6.5 | 1.09 |
| Norfolk | 1574 | 24 | 2.01 | +9.8 | 1.03 |
| Northants and Cambs | 1576 | 36 | 2.00 | +6.9 | 1.04 |
| Warwick and Leicester | 1576 | 19 | 1.58 | -9.7 | 1.07 |
| Staffordshire | 1577 | 18 | 1.14 | +11.2 | 1.02 |
| Worcestershire | 1577 | 21 | 0.68 | +9.4 | 1.01 |
| Shropshire | 1577 | 19 | 1.07 | +15.6 | 1.03 |
| Herefordshire | 1577 | 26 | 0.81 | +15.5 | 1.08 |
| Lincs and Notts | 1576 | 28 | 1.65 | +8.4 | 1.00 |
| Derbyshire | 1577 | 20 | 0.69 | +10.2 | 1.02 |
| Cheshire | 1577 | 22 | 1.29 | +7.7 | 1.05 |
| Yorkshire | 1577 | 62 | 1.77 | +7.6 | 1.05 |
| Lancashire | 1577 | 24 | 1.40 | +7.7 | 1.02 |
| Durham | 1576 | 19 | 1.70 | +4.9 | 1.14 |
| Cumberland | 1576 | 16 | 1.63 | +8.6 | 1.05 |
| Northumberland | 1576 | 17 | 1.34 | +8.1 | 1.04 |
| Monmouthshire | 1577 | 25 | 1.16 | +9.9 | 1.14 |
| Glamorgan | 1578 | 15 | 1.12 | +8.0 | 1.10 |
| Mid and south Wales | 1578 | 48 | 2.17 | +8.5 | 1.07 |
| Pembrokeshire | 1578 | 7 | 1.04 | +10.0 | 1.05 |
| Montgomery | 1578 | 25 | 1.57 | +8.8 | 1.06 |
| Denbigh and Flint | 1577 | 25 | 1.38 | +11.3 | 1.16 |
| Caernarfon and Anglesey | 1578 | 18 | 1.83 | +7.9 | 1.08 |

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
- Per sheet: azimuthal equidistant frame in km about the readings' centre; similarity and affine least squares; misplacement = ground distance between the true place and the sheet position taken back through the inverse similarity. Outliers beyond max(5 km, 4 x median) dropped (0). Thin plate spline (smoothing = n) for the bent grid and a leave-one-out check.
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

- Christopher Saxton, atlas of England and Wales, BnF https://gallica.bnf.fr/ark:/12148/btv1b55007148q, scans via Wikimedia Commons, public domain.
- Wikidata (CC0); Natural Earth (public domain); OpenFreeMap and © OpenStreetMap contributors (ODbL) for the page's base map.
- Borough, W. (1581) A Discours of the Variation of the Cumpas; Encyclopaedia Britannica (1911) Magnetism, Terrestrial; Evans, I. M. and Lawrence, H. (1979) Christopher Saxton, Elizabethan Map-maker.
- Code MIT; text, figures and derived data CC BY 4.0.

## Citation

Hotham, T. (2026) Saxton's atlas, measured. Zenodo. {https://doi.org/10.5281/zenodo.24052723}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
