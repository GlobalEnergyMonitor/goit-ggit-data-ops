#!/usr/bin/env python3
"""Brazil batch (2026-07-27) Background-citation repairs.

Archive-first URL swaps for genuinely-dead refs; dead GIIGNL annual-report
PDFs -> live Webflow CDN. Left as-is (alive for readers, edge/bot-blocked):
epbr.com.br (Cloudflare 522 to datacenter IPs), ir.newfortressenergy.com,
reuters/spglobal/hydrocarbons-technology/power-technology (401/403 bot-walls),
esg.portodoacu.com.br (200), gnlglobal SOFT404 false-pos, and an existing
web.archive.org reuters snapshot that soft-404s on page chrome. Dead + no
archive (nasdaq, abolbrasil, sema.rs.gov.br, itajainaval) -> HUMAN-REVIEW.
All archive snapshots content-validated (no maintenance/404/403 captures).
"""
import sys, pickle
sys.path[:0] = [".", "../.."]
import fixlib, gemwiki as gw

CDNMAP = {"G2021": fixlib.G2021, "G2023": fixlib.G2023, "G2024": fixlib.G2024}
bypage, noarch = pickle.load(open("brazil_plan.pkl", "rb"))

# content-validation override: availability-API snapshot was a maintenance page
OVERRIDE = {
 "https://lnglatinamerica.com/brazil-prepares-for-a-new-phase-of-investments-in-lng-terminals/":
 "https://web.archive.org/web/20221209200028/https://lnglatinamerica.com/brazil-prepares-for-a-new-phase-of-investments-in-lng-terminals/",
}

SUMM = {
 "Bahia FSRU": "background refs: dead lnglatinamerica/argus/petrobras -> wayback archives",
 "Cosan FSRU": "background refs: dead lnglatinamerica -> wayback; giignl 2023/2024 pdfs -> live cdn",
 "Geramar FSRU": "background ref: dead lnglatinamerica -> wayback archive",
 "Guanabara Bay FSRU": "background refs: dead petrobras/lngworldnews/igu/argus -> wayback archives",
 "Imetame LNG Terminal": "background refs: dead lnglatinamerica/brainmarket -> wayback archives",
 "New Fortress Barcarena FSRU": "giignl 2024 report: dead pdf -> live cdn copy",
 "Nimofast Antonina LNG Terminal": "background ref: dead nimofast post -> wayback archive",
 "Paraná FSRU": "background ref: dead lnglatinamerica -> wayback archive",
 "Pecém FSRU": "background ref: seinfra.ce.gov.br (expired cert) -> wayback archive",
 "Porto Norte Fluminense FSRU": "background ref: dead inea.rj.gov.br pdf -> wayback archive",
 "Porto do Açu FSRU": "background refs: dead lnglatinamerica/hellenicshipping/igu -> wayback; giignl 2021/2023 -> cdn",
 "Presidente Kennedy FSRU": "background ref: dead lnglatinamerica -> wayback archive",
 "Sepetiba Bay FSRU": "giignl 2024 report: dead pdf -> live cdn copy",
 "Sergipe FSRU": "background ref: dead eneva news -> wayback archive",
 "Suape FSRU": "background refs: dead giignl news + suape.pe.gov.br -> wayback; giignl 2023 pdf -> cdn",
 "São Marcos Bay FSRU": "background ref: dead brainmarket -> wayback archive",
 "TGNL São Luis FSRU": "background refs: dead fiema/tgnlsaoluis -> wayback archives",
 "Tepor Macaé FSRU": "background refs: dead inea/odebateon/lnglatinamerica/diariodoporto/rj.gov.br -> wayback archives",
 "Tergás Rio Grande LNG Terminal": "background ref: dead riogrande.rs.gov.br -> wayback archive",
 "Terminal Gás Sul FSRU": "background ref: dead jornalocorreiosc -> wayback; giignl 2023/2024 -> cdn",
}

fixes = {}
for page, items in bypage.items():
    fx = []
    for refn, typ, url, new in sorted(items):
        if typ == "giignl":
            fx.append((f"giignl -> cdn (#{refn})", url, ("swap", url, CDNMAP[new])))
        else:
            snap = OVERRIDE.get(url, new).replace("http://web.archive.org", "https://web.archive.org")
            fx.append((f"dead -> wayback (#{refn})", url, ("swap", url, snap)))
    fixes[page] = (SUMM[page], fx)

s = gw.session()
diffs = {}
for t, (summ, fx) in fixes.items():
    diffs[t] = fixlib.build(s, t, fx)
pickle.dump((fixes, diffs), open("diffs_brazil.pkl", "wb"))
print(f"\n\nALL DIFFS BUILT OK -> {len(diffs)} pages")
