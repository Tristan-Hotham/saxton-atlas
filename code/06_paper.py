"""Step 6: the paper (release/paper/Hotham_Saxton_Atlas.tex and .pdf), built from results.json."""
import subprocess, shutil
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json"); F = jload(f"{DATA}/fits.json")
c, t, sc, g, go, n, sh = R["counts"], R["turn"], R["scale"], R["general"], R["gough"], R["county"], R["shared"]
def e(s): return str(s).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
rows = "\n".join(f"{e(s['short'])} & {s['year']} & {s['n']} & {s['px_per_km']:.1f} & {s['med_km']:.2f} & {s['med_aff_km']:.2f} & {s['loo_tps_med_km']:.2f} & {s['turn_deg']:+.1f} & {s['aniso']:.2f} \\\\" for s in R["sheets"])
regs = "; ".join(f"{k} {v['med_km']:.2f} km ({v['n']} readings)" for k, v in R["regions"].items())
big = ", ".join(f"{b['name']} on {b['sheet']} ({b['km']:.1f} km)" for b in n["biggest"][:4])
neg = ", ".join(f"{x['sheet']} ({x['deg']:+.1f}°)" for x in t["neg"])
tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\setmainfont{TeX Gyre Pagella}
\usepackage[a4paper,margin=2.3cm]{geometry}
\usepackage{graphicx,booktabs,float,caption,array,xcolor,longtable}
\usepackage{xurl}
\usepackage[hidelinks]{hyperref}
\usepackage[round]{natbib}
\usepackage{setspace}
\setstretch{1.05}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em}
\captionsetup{font=small,labelfont=bf}
\hypersetup{pdftitle={Saxton's Atlas, Measured},pdfauthor={Tristan Hotham}}
\begin{document}
\begin{center}
{\Large\bfseries Saxton's Atlas, Measured\par}
\vspace{0.4em}
{\large The accuracy, scale and orientation of the first county atlas of England and Wales (1574 to 1579)\par}
\vspace{1.2em}
{\large Tristan Hotham\par}
\vspace{0.3em}
{\small Independent researcher\\ ORCID: 0000-0003-4931-9349\\ DOI: \url{https://doi.org/10.5281/zenodo.24052723}\par}
\vspace{0.8em}
2026
\end{center}
\begin{quote}\small\textbf{Abstract.} Christopher Saxton's county maps of England and Wales, engraved between 1574 and 1579, are the foundation of English county cartography. I read """ + f"{c['readings']:,}" + r""" positions (town and church symbols, castles and bridges) on all """ + str(c['sheets_county_read']) + r""" county sheets and on the general map in the Biblioth\`eque nationale de France copy, matched them to Wikidata settlement points and fitted each sheet to the ground with similarity, affine and thin-plate spline transformations. At each sheet's own scale and orientation, the median place is misplaced by """ + f"{n['med_km']:.2f}" + r""" km; """ + str(n['within2_pct']) + r"""\% are within 2 km. Sheets differ in quality (median """ + f"{n['best_km']:.2f}" + r""" to """ + f"{n['worst_km']:.2f}" + r""" km) but hardly at all in shape (median stretch """ + f"{sc['aniso_median']:.2f}" + r"""). True north is turned anticlockwise on """ + f"{t['n_pos']}" + r""" of """ + f"{t['n']}" + r""" county sheets, by a median of """ + f"{t['median_deg']:.1f}" + r"""$^\circ$ (Cornwall excluded), close to the magnetic variation of about 11\textonequarter$^\circ$ east measured in London in 1580, while the general map is turned only """ + f"{t['general_deg']:.1f}" + r"""$^\circ$. On the general map the median town is misplaced by """ + f"{g['med_km']:.1f}" + r""" km, against """ + f"{go['med_km']:.1f}" + r""" km for the Gough Map of about 1360 measured in the same way.\end{quote}

\section{Introduction}
Saxton's atlas, published in 1579 with a general map of England and Wales and 34 county maps, was the first set of maps of the whole country at county scale drawn from a new survey \citep{evans}. Its sheets were copied, re-engraved and reissued for two centuries. This paper asks three plain questions that a modern reader can test with digital scans and a gazetteer: how close to their true places are the towns; how consistent are the sheets with one another in scale and shape; and which way is north. It follows the method of an earlier study of the Gough Map \citep{gough}, so that the two can be compared.

\section{Data}
The scans are the Wikimedia Commons images of the BnF copy (ark:/12148/btv1b55007148q), 3,840 pixels wide. Of """ + str(c['scans']) + r""" files supplied, 35 are the general map and the 34 county maps, one is a map of Scotland bound with the atlas that is not Saxton's, and """ + str(c['files_dup']) + r""" are single sheets from other copies duplicating Devon, Dorset, Cornwall, Wiltshire and Somerset; these were identified and set aside. True positions are Wikidata settlement points (CC0), with a handful typed by hand where Wikidata had no settlement item of the right type. Coastlines for figures are from Natural Earth \citep{ne}.

\section{Methods}
\subsection{Reading the sheets}
For each sheet I placed a few anchor towns by eye on an overview, then worked through candidate settlements in the county (cities and market towns first, then towns and villages), each shown as a zoomed crop of the full scan centred on its predicted position (a similarity, then an affine, then a thin-plate spline fit to the towns already read). I accepted a reading only when an engraved symbol and a legible or nearly legible name agreed with the place, and recorded the pixel position of the symbol. Each reading is flagged certain (""" + str(c['conf1']) + r"""), probable (""" + str(c['conf2']) + r""") or doubtful in its exact point (""" + str(c['conf3']) + r"""). Readings per county sheet range from """ + str(c['per_sheet_min']) + r""" to """ + str(c['per_sheet_max']) + r""" (median """ + str(c['per_sheet_median']) + r"""). Every county sheet was read.

\subsection{Fitting}
True positions are projected onto an azimuthal equidistant plane centred on the mean of each sheet's readings, in kilometres, so that up is true north. Pixel positions have $y$ turned upwards. A similarity transformation (one scale, one rotation, a shift) and an affine transformation are fitted by least squares \citep{tobler}. A place's misplacement is the ground distance between its true position and the sheet position taken back through the inverse of the sheet's own similarity; the same for the affine. Readings misplaced by more than the larger of 5 km and four times the sheet median (25 km on the general map) are treated as misreadings and dropped (""" + str(c['outliers']) + r""" in all). A thin-plate spline \citep{bookstein} with smoothing equal to the number of readings bends a true 5 km grid onto each sheet and gives a leave-one-out check. The turn is the angle of the similarity's rotation: positive when true north points to the left of the sheet's top. Places read on two county sheets give a sheet-to-sheet check.

\section{Results}
\begin{figure}[H]\centering\includegraphics[width=.92\linewidth]{f_reading.jpg}\caption{Readings on the Worcestershire sheet (1577). Arrows run from each reading to where the true town falls under the sheet's similarity fit.}\end{figure}
\subsection{Accuracy}
Across """ + f"{c['used_county']}" + r""" readings on county sheets, the median misplacement is """ + f"{n['med_km']:.2f}" + r""" km (mean """ + f"{n['mean_km']:.2f}" + r""" km); """ + str(n['within1_pct']) + r"""\% are within 1 km and """ + r"""all but """ + str(n['over5']) + r""" within 5 km. The affine fit lowers the median only to """ + f"{n['med_aff_km']:.2f}" + r""" km, and the thin-plate spline's leave-one-out median is """ + f"{n['loo_tps_med_km']:.2f}" + r""" km. Certain readings give """ + f"{n['med_conf1_km']:.2f}" + r""" km, probable ones """ + f"{n['med_conf2_km']:.2f}" + r""" km. By region: """ + regs + r""". The largest misplacements are """ + e(big) + r""". Part of every figure is the gap between a modern Wikidata point and the sixteenth century church symbol, typically a few hundred metres.
\begin{figure}[H]\centering\includegraphics[width=.8\linewidth]{f_errors.png}\caption{Median misplacement per county sheet.}\end{figure}
\begin{figure}[H]\centering\includegraphics[width=.72\linewidth]{f_map.png}\caption{Every reading on a county sheet, coloured by misplacement.}\end{figure}

\subsection{Scale and shape}
Scales range from """ + f"{sc['min_px_km']:.1f}" + r""" scan pixels per km (""" + e(sc['min_sheet']) + r""") to """ + f"{sc['max_px_km']:.1f}" + r""" (""" + e(sc['max_sheet']) + r"""), a factor of """ + f"{sc['ratio']:.1f}" + r""": Saxton fitted each county to the plate rather than keeping one scale. The median affine stretch is """ + f"{sc['aniso_median']:.2f}" + r""" and the largest """ + f"{sc['aniso_max']:.2f}" + r""" (""" + e(sc['aniso_max_name']) + r"""). """ + str(sh['n']) + r""" places read on two sheets fall a median """ + f"{sh['med_km']:.2f}" + r""" km apart when each is taken to the ground through its own sheet (largest """ + e(sh['max_name']) + r""", """ + f"{sh['max_km']:.1f}" + r""" km).
\begin{figure}[H]\centering\includegraphics[width=.8\linewidth]{f_grid.jpg}\caption{The Cornwall sheet with the true 5 km grid bent onto it by the thin-plate spline.}\end{figure}

\subsection{Orientation}
True north is turned anticlockwise on """ + str(t['n_pos']) + r""" of """ + str(t['n']) + r""" county sheets; leaving aside Cornwall (""" + f"{t['cornwall_deg']:+.1f}" + r"""$^\circ$; possibly turned so the long peninsula fits the plate), the median is """ + f"{t['median_deg']:.1f}" + r"""$^\circ$ and the middle half lies between """ + f"{t['q1_deg']:.1f}" + r"""$^\circ$ and """ + f"{t['q3_deg']:.1f}" + r"""$^\circ$; """ + str(t['n_5_to_16']) + r""" sheets lie between 5$^\circ$ and 16$^\circ$. The exceptions are """ + e(neg) + r""". William Borough measured the variation of the compass at Limehouse in October 1580 as about 11\textonequarter$^\circ$ east \citep{borough, eb1911}. If Saxton's surveys were oriented by magnetic compass and the plates drawn with magnetic north at the top, true north would appear turned anticlockwise by about that amount, as observed. The general map, compiled from the county sheets, is turned only """ + f"{t['general_deg']:.1f}" + r"""$^\circ$, which suggests it was set to true north when it was put together. The scans themselves may be skewed by a degree or so; this does not change the pattern. The explanation is offered as a reading of the evidence, not a proof.
\begin{figure}[H]\centering\includegraphics[width=.8\linewidth]{f_turns.png}\caption{Turn of true north on each county sheet, with Borough's 1580 value.}\end{figure}

\subsection{The general map and the Gough Map}
On the general map (""" + str(g['n']) + r""" towns) the median misplacement is """ + f"{g['med_km']:.2f}" + r""" km (affine """ + f"{g['med_aff_km']:.2f}" + r""" km; """ + str(g['within10_pct']) + r"""\% within 10 km; largest """ + e(g['worst']) + r""", """ + f"{g['max_km']:.1f}" + r""" km), with a stretch of """ + f"{g['aniso']:.2f}" + r""". The Gough Map of about 1360, measured with the same similarity fit, misplaces its median way station by """ + f"{go['med_km']:.1f}" + r""" km \citep{gough}, """ + f"{go['ratio_general']:.1f}" + r""" times as much. The comparison is rough: the samples of towns differ and the Gough Map includes Scotland's edge only through control points.
\begin{figure}[H]\centering\includegraphics[width=.7\linewidth]{f_general.png}\caption{The general map of 1579: arrows from each true town towards its position on the map, five times exaggerated.}\end{figure}

\section{Limitations}
Readings are by eye and by one reader; names were matched to modern settlement points, not to historic church sites. Welsh sheets carry fewer places than most English ones. Small samples on some sheets (Pembrokeshire """ + str(F['p107']['n']) + r""") make their medians uncertain. The scale bars on the sheets were not measured, so scales are given in scan pixels; the five duplicate sheets from other copies were not compared with the BnF impressions.

\section{Conclusion}
Saxton's county maps place towns typically within about one and a half kilometres of where an accurate map at the same scale and orientation would, with true shapes and consistent joins between neighbouring sheets. Their most striking systematic feature is the westward lean of north, of the size of the magnetic variation of the day, which the general map does not share. Two centuries after the Gough Map, the general map is about four times as accurate.

\section*{Data and code availability}
Data, code and the interactive page are at \url{""" + REPO + r"""} and \url{""" + PAGE + r"""}. Code MIT; text, figures and derived data CC BY 4.0. Wikidata is CC0; the scans are public domain.

\section*{AI statement}
""" + AI + r"""

\begin{thebibliography}{9}
\bibitem[Bookstein(1989)]{bookstein} Bookstein, F. L. (1989) Principal warps: thin-plate splines and the decomposition of deformations. \emph{IEEE Transactions on Pattern Analysis and Machine Intelligence} 11(6), 567-585.
\bibitem[Borough(1581)]{borough} Borough, W. (1581) \emph{A Discours of the Variation of the Cumpas, or Magneticall Needle}. London.
\bibitem[Encyclopaedia Britannica(1911)]{eb1911} Encyclopaedia Britannica (1911) Magnetism, Terrestrial. 11th edn, vol. 17.
\bibitem[Evans and Lawrence(1979)]{evans} Evans, I. M. and Lawrence, H. (1979) \emph{Christopher Saxton, Elizabethan Map-maker}. Wakefield: Wakefield Historical Publications and Holland Press.
\bibitem[Hotham(2026)]{gough} Hotham, T. (2026) The Gough Map: Britain's oldest road map, measured. Zenodo. \url{https://doi.org/10.5281/zenodo.24043678}.
\bibitem[Natural Earth(n.d.)]{ne} Natural Earth. Free vector and raster map data. \url{https://www.naturalearthdata.com/}. Public domain.
\bibitem[Tobler(1994)]{tobler} Tobler, W. R. (1994) Bidimensional regression. \emph{Geographical Analysis} 26(3), 187-212.
\end{thebibliography}

\clearpage
\section*{Appendix: fits by sheet}
{\small\begin{longtable}{lrrrrrrrr}\toprule
Map & Year & $n$ & px/km & Sim. km & Aff. km & LOO km & Turn$^\circ$ & Stretch\\\midrule\endhead
""" + rows + r"""
\bottomrule\end{longtable}}
\end{document}
"""
out = f"{ROOT}/release/paper"
open(f"{out}/Hotham_Saxton_Atlas.tex", "w").write(tex)
for _ in range(2):
    p = subprocess.run(["xelatex", "-interaction=nonstopmode", "Hotham_Saxton_Atlas.tex"], cwd=out, capture_output=True, text=True)
assert os.path.exists(f"{out}/Hotham_Saxton_Atlas.pdf"), p.stdout[-2000:]
for x in ("aux", "log", "out"):
    if os.path.exists(f"{out}/Hotham_Saxton_Atlas.{x}"): os.remove(f"{out}/Hotham_Saxton_Atlas.{x}")
print(subprocess.run(["pdfinfo", f"{out}/Hotham_Saxton_Atlas.pdf"], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0], "pages")
