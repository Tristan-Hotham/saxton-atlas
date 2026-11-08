# [OC] I measured Saxton's 1579 atlas of England and Wales: 857 towns, a median error of 1.4 km, and north leans 8° west on 31 of 34 county maps (Cornwall excluded from the median), like a compass

I read 857 towns on Christopher Saxton's county maps (the first county atlas of England and Wales, engraved 1574 to 1579) and fitted each sheet to the real positions. Each county is drawn at its own scale, but within a sheet the median town is only 1.37 km from where it should be. The surprise: true north is turned anticlockwise on almost every sheet, by a median 8.4° (Cornwall excluded: it is turned the other way, perhaps to fit the plate), close to the ~11¼° east compass variation measured in London in 1580. The general map is not turned (-0.9°).

Interactive version (pick a county, see the true grid bent over it, fade to the modern map): https://maps.tristanhotham.com/saxton-atlas/

**Source comment:** Data: BnF copy of Saxton's atlas (scans on Wikimedia Commons, public domain); town positions from Wikidata (CC0). Tools: Python (numpy, scipy, matplotlib), MapLibre. Positions read by hand on zoomed scans; similarity, affine and thin plate spline fits per sheet. Code and data: https://github.com/Tristan-Hotham/saxton-atlas
