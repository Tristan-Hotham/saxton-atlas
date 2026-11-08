# NOTES (working log, saxton-atlas)

- Sheets identified (BnF ark btv1b55007148q, Commons pages): p014 general map Anglia 1579; p017 Kent/Sussex/Surrey/Middx;
  p020 Hampshire; p023 Dorset; p026 Wiltshire; p029 Somerset; p032 Devon; p035 Cornwall; p038 Essex; p041 Herts;
  p044 Oxon/Bucks/Berks; p047 Glos; p050 Suffolk; p053 Norfolk; p056 Northants+Beds+Cambs+Hunts+Rutland; p059 Warwick+Leics;
  p062 Staffs; p065 Worcs; p068 Shropshire; p071 Herefs; p074 Lincs+Notts; p077 Derbys; p080 Cheshire; p083 Yorkshire;
  p086 Lancashire; p089 Durham; p092 Westmorland+Cumberland; p095 Northumberland; p098 Monmouth; p101 Glamorgan;
  p104 Radnor/Brecon/Cardigan/Carmarthen; p107 Pembroke; p110 Montgomery+Merioneth; p113 Denbigh+Flint; p116 Caernarfon+Anglesey;
  p119 Scotiae Tabula (not Saxton, not used). Five non-BnF files duplicate p032 Devon, p023 Dorset, p035 Cornwall, p026 Wilts, p029 Somerset.
- Reading tool: code/00_reading_aid.py (overview, crops around predicted positions, ingest picks). Anchors in WORK/anchors.csv
  (only to steer predictions; never used in fits). Readings in data/readings.csv.
- Progress: 21 sheets read (south, east, midlands, Yorks, Lancs, Cheshire), 608 readings by p086.
- Done: 732 readings (686 county on 29 sheets + 46 general map); 2 outliers dropped. Not read: p098 Monmouth, p104 mid/south Wales,
  p110 Montgomery/Merioneth, p113 Denbigh/Flint, p116 Caernarfon/Anglesey.
- Pipeline: 01_images, 02_fit, 03_results, 04_figures, 05_build_site, 06_paper, reddit/collage.py, 07_release. QA: code/qa.js
  (needs ML_DIST pointing at a local maplibre-gl 4.7.1 dist because jsDelivr is blocked in the container).
- Citations verified by web search: Borough 1581 (DNB, EEBO A68509); EB1911 "Magnetism, Terrestrial" gives 11 deg 14' E at Limehouse Oct 1580;
  Evans and Lawrence 1979 (library catalogues).
- Independent review: 48 random readings checked on crops; fixed Winchcombe, Kingsland, Arnold, Neston, Ashton (p080), Blyth (river mouth)
  pixel positions; Stocksfield -> Corbridge (engraved Corbridge); Bradford was the Devon village (now Bradford city centre); Kenilworth
  pixel was in the border (now the castle symbol). No outliers remain. Pipeline rerun 02 to 07; Cornwall exclusion from the turn median now stated.
- Full verification pass (every reading, every sheet, zoomed crops; county check of true coordinates): 183 changes =
  165 symbol positions corrected (80 by 30 px or more), 16 readings dropped (unconfirmed or no symbol), 2 general-map readings set to doubtful.
  Per-reading log:
    p014 Bridgwater: moved 41 px
    p014 Derby: confidence 3
    p014 Taunton: confidence 3
    p014 Witney: moved 38 px
    p014 Lichfield: moved 26 px
    p014 Liverpool: moved 39 px
    p017 Croydon: moved 41 px, conf 2
    p017 Ashford: moved 17 px
    p017 Woolwich: moved 22 px
    p017 Reigate: moved 34 px
    p020 Basingstoke: moved 59 px, conf 2
    p020 Gosport: moved 34 px
    p020 Lymington: moved 44 px
    p020 Tadley: moved 52 px, conf 2
    p020 Bishop's Waltham: moved 56 px
    p023 Wyke Regis: moved 35 px, conf 2
    p026 Chippenham: moved 37 px
    p026 Corsham: moved 58 px, conf 2
    p026 Pewsey: moved 13 px
    p029 Burnham-on-Sea  and Highbridge: dropped
    p032 Ashburton: dropped
    p032 Holsworthy: moved 52 px
    p032 Barnstaple: moved 52 px
    p032 Totnes: moved 22 px
    p035 St Austell: moved 52 px
    p038 Saffron Walden: moved 26 px
    p038 Harlow: moved 26 px
    p038 Stanford-le-Hope: moved 44 px
    p038 Witham: moved 76 px, conf 2
    p038 South Ockendon: moved 71 px
    p044 Henley-on-Thames: moved 65 px
    p047 Chipping Campden: moved 25 px
    p047 Yate: moved 25 px
    p047 Stonehouse: moved 24 px
    p050 Newmarket: moved 35 px
    p050 Halesworth: moved 28 px
    p050 Needham Market: moved 17 px
    p050 Hadleigh: moved 39 px
    p050 Leiston: moved 13 px
    p050 Aldeburgh: moved 23 px
    p050 Martlesham: moved 58 px, conf 2
    p050 Elmswell: moved 45 px
    p050 Haverhill: moved 22 px
    p050 Mildenhall: moved 106 px
    p050 Kessingland: moved 30 px
    p050 Long Melford: moved 53 px, conf 2
    p050 Glemsford: moved 103 px
    p050 Rendlesham: moved 51 px, conf 2
    p050 Beccles: moved 65 px, conf 2
    p053 Dereham: moved 26 px
    p053 Attleborough: moved 34 px
    p053 Sheringham: moved 37 px, conf 2
    p053 Holt: moved 33 px
    p053 Diss: dropped
    p053 Long Stratton: moved 18 px, conf 2
    p053 Hemsby: moved 53 px
    p053 Loddon: moved 40 px
    p056 Bedford: moved 46 px, conf 2
    p056 Hitchin: moved 23 px
    p056 Kettering: moved 9 px
    p056 Huntingdon: moved 13 px
    p056 Whittlesey: moved 15 px
    p056 Chatteris: moved 40 px
    p056 Ramsey: moved 22 px
    p056 Shefford: moved 22 px
    p056 Sandy: moved 28 px
    p056 Rothwell: moved 25 px
    p056 Uppingham: moved 53 px
    p056 Leighton Buzzard: dropped
    p056 Kempston: moved 34 px
    p056 Houghton Regis: moved 62 px
    p056 Flitwick: moved 22 px
    p056 Soham: moved 33 px
    p059 Solihull: moved 67 px
    p059 Warwick: moved 67 px
    p059 Ashby-de-la-Zouch: moved 71 px
    p059 Lutterworth: moved 43 px, conf 2
    p059 Atherstone: moved 28 px
    p059 Southam: moved 35 px
    p059 Sutton Coldfield: moved 31 px
    p059 Alcester: moved 50 px
    p059 Nuneaton: moved 100 px
    p059 Bedworth: dropped
    p059 Loughborough: moved 48 px, conf 2
    p059 Melton Mowbray: moved 20 px
    p062 Stafford: moved 23 px
    p062 Lichfield: moved 31 px
    p062 Leek: moved 17 px
    p062 Uttoxeter: moved 21 px
    p062 Cheadle: moved 16 px
    p062 Dudley: dropped
    p062 Tamworth: moved 67 px, conf 2
    p062 Cannock: dropped
    p062 Halesowen: moved 51 px, conf 2
    p062 Biddulph: moved 21 px
    p065 Kings Norton: moved 19 px
    p065 Claines: moved 21 px
    p065 Hagley: moved 23 px
    p068 Tong: moved 21 px
    p068 Shifnal: dropped
    p068 Oswestry: moved 41 px
    p068 Church Stretton: moved 41 px
    p068 Broseley: moved 20 px
    p068 Clun: moved 52 px, conf 2
    p068 Albrighton: moved 33 px
    p068 Highley: moved 28 px
    p071 Clehonger: moved 65 px
    p071 Walford: moved 62 px
    p071 Bodenham: moved 29 px
    p071 Credenhill: moved 20 px
    p071 Kingstone: moved 21 px
    p071 Whitchurch: moved 26 px
    p071 Llangarron: moved 17 px
    p071 Pembridge: moved 34 px
    p071 Weston under Penyard: moved 21 px, conf 2
    p074 Lincoln: moved 38 px
    p074 Boston: moved 25 px
    p074 Worksop: moved 27 px
    p074 Hucknall: moved 16 px
    p074 Grantham: moved 62 px
    p074 Spalding: moved 37 px
    p074 Mansfield: moved 18 px
    p074 Sleaford: moved 33 px
    p074 Bourne: moved 12 px
    p074 Louth: moved 22 px
    p074 Bingham: moved 44 px
    p074 Brigg: moved 16 px
    p074 Long Sutton: moved 17 px
    p074 Wilford: moved 28 px, conf 2
    p074 Sutton in Ashfield: moved 13 px
    p074 Winthorpe: moved 17 px
    p077 Ashbourne: moved 17 px
    p077 Melbourne: dropped
    p077 Ilkeston: moved 12 px
    p077 Swadlincote: moved 39 px, conf 2
    p077 Buxton: moved 18 px
    p077 Matlock: moved 12 px
    p077 Bolsover: moved 59 px
    p077 Chapel-en-le-Frith: moved 34 px
    p080 Chester: moved 25 px
    p080 Frodsham: moved 23 px
    p080 Winsford: moved 11 px
    p080 Middlewich: moved 42 px
    p080 Knutsford: moved 35 px
    p080 Lymm: moved 25 px
    p080 Poynton: moved 31 px, conf 2
    p083 Dewsbury: moved 19 px
    p083 Pontefract: moved 22 px
    p083 Beverley: moved 21 px
    p083 Snaith: moved 16 px
    p083 Wetherby: moved 30 px
    p083 Aberford: moved 13 px
    p083 Drax: dropped
    p083 Cawood: moved 30 px, conf 2
    p083 Heptonstall: moved 14 px, conf 2
    p083 Otley: moved 20 px
    p083 Sowerby Bridge: moved 18 px
    p083 Pickering: moved 27 px
    p083 Easingwold: moved 13 px
    p083 Leyburn: moved 21 px, conf 2
    p083 Redcar: dropped
    p083 Ilkley: moved 10 px
    p083 Calverley: moved 13 px
    p083 Helmsley: moved 11 px
    p086 Salford: dropped
    p086 Ashton-under-Lyne: moved 35 px, conf 2
    p086 Blackburn: moved 22 px
    p086 Poulton-le-Fylde: moved 44 px
    p086 Oldham: moved 14 px
    p086 Broughton in Furness: moved 24 px, conf 2
    p092 Milnthorpe: moved 18 px
    p092 Whitehaven: moved 4 px
    p092 Aspatria: moved 22 px
    p095 Morpeth: moved 56 px
    p095 Whitley Bay: dropped
    p095 Cramlington: moved 49 px
    p095 Ashington: moved 33 px, conf 2
    p095 Prudhoe: moved 38 px
    p095 Newbiggin-by-the-Sea: moved 33 px, conf 2
    p095 Ponteland: dropped
    p095 Seaton Delaval: dropped
    p095 Corbridge: moved 19 px, conf 2
    p107 Llanwnda: dropped- Welsh sheets p098, p104, p110, p113, p116 still not read.
- Wording: Cornwall excluded from the turn median stated wherever it appears; plate-fitting offered only as a possibility; Borough 11¼° E (1581 Discours).
- Welsh sheets read (same crop-and-verify standard): p098 25, p104 48, p110 25, p113 25, p116 18 readings; Dolgellau, Harlech, Caernarfon hand-typed (not in gazetteer). All 34 county sheets now read; unread caveats removed.
