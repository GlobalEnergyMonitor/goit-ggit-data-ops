#!/usr/bin/env python3
"""Argentina / Chile / Venezuela batch (2026-07-27) Background-citation repairs.

Archive-first swaps for genuinely-dead refs (bit.ly shortlinks swapped at their
resolved targets); dead GIIGNL annual-report PDFs -> live Webflow CDN. All
archive snapshots content-validated. Left as-is: 401/403 bot-walls (reuters,
spglobal, argenports, hydrocarbons-technology, mcdermott, sec.gov, gnlt.cl,
iamericas, bloomberg, nytimes), ICIS subscriber pages (DRIFT-200), YPF investor
PDFs + marpatagonico/oxfordenergy/tgn PDFs (200), energyintel/gnlglobal SOFT404
false-pos. Dead + no usable archive (petrolnews, financialpost 403-only,
gnlglobal deep article, canal9) -> HUMAN-REVIEW.
"""
import sys, pickle, json
sys.path[:0] = [".", "../.."]
import fixlib, gemwiki as gw
CDNMAP = {"G2021": fixlib.G2021, "G2024": fixlib.G2024}

plan = pickle.load(open("plan_acv.pkl", "rb"))
snaps = json.load(open("wb_acv.json"))
snaps.update(json.load(open("wb_acv_retry.json")))
# manual additions found via CDX
EXTRA = {
 "https://www.lngworldnews.com/exmar-completes-commissioning-of-tango-flng/":
 "https://web.archive.org/web/20190610110616/https://www.lngworldnews.com/exmar-completes-commissioning-of-tango-flng/",
}
snaps.update(EXTRA)

SUMM = {
 "Argentina LNG Terminal": "background refs: dead naturalgasintel/gecf/harbourenergy/anred -> wayback archives",
 "Bahia Blanca GasPort FSRU": "background refs: dead bit.ly shortlinks + excelerate -> wayback; giignl 2024 -> cdn",
 "Bahía Blanca FLNG Terminal": "background refs: dead lngworldnews -> wayback; giignl 2021 -> cdn",
 "Dock Sud LNG Terminal": "background ref: dead bit.ly -> wayback archive of lngworldnews original",
 "Escobar FSRU": "giignl 2021/2024 reports: dead giignl.org pdfs -> live cdn copies",
 "Mejillones LNG Terminal": "background refs: dead engie.cl / engie-energia.cl -> wayback archives",
 "Penco Lirquén FSRU": "background refs: 6 dead refs (uc.cl, lngworldnews, revistaei, igu, gnlpenco, issuu) -> wayback archives",
 "Quintero LNG Terminal": "background refs: dead lngworldnews/gnlquintero/fch -> wayback; giignl 2021/2024 -> cdn",
 "Talcahuano FSRU": "background refs: dead revistaei / terram -> wayback archives",
 "Venezuela Offshore LNG Terminal": "background refs: dead lngworldnews / worldoil -> wayback archives",
}

# group plan by page, skip refs with no snapshot (giignl always has cdn)
from collections import defaultdict
bypage = defaultdict(list)
noarch = []
for c, page, refn, typ, oldurl, lookup, cdn in plan:
    if typ == "giignl":
        bypage[page].append((refn, oldurl, ("swap", oldurl, CDNMAP[cdn])))
    else:
        key = lookup or oldurl
        snap = snaps.get(key)
        if not snap:
            noarch.append((c, page, refn, oldurl)); continue
        bypage[page].append((refn, oldurl, ("swap", oldurl, snap)))

fixes = {}
for page, items in bypage.items():
    fx = [(f"repair #{refn}", marker, action) for refn, marker, action in sorted(items)]
    fixes[page] = (SUMM[page], fx)

print("NO ARCHIVE -> HUMAN-REVIEW:")
for c, p, r, u in noarch: print(f"   {p} #{r}  {u}")
print()
s = gw.session()
diffs = {}
for t, (summ, fx) in fixes.items():
    diffs[t] = fixlib.build(s, t, fx)
pickle.dump((fixes, diffs), open("diffs_acv.pkl", "wb"))
print(f"\n\nALL DIFFS BUILT OK -> {len(diffs)} pages, {sum(len(fx) for _,fx in fixes.values())} fixes")
