#!/usr/bin/env python3
"""Mexico batch (2026-07-27) Background-citation repairs + Andrés Argus recovery.

Archive-first / live-CDN URL swaps only. NFE ir.newfortressenergy.com and
investor.sempra.com refs are edge-bot-blocked (HTTP/2 RST) but alive for
readers -> left as-is, like 401/403 bot-walls. Genuinely-dead refs with no
archive (nasdaq/Reuters, ngvjournal 2016) go to HUMAN-REVIEW instead.
"""
import sys
sys.path[:0] = [".", "../.."]
import fixlib, gemwiki as gw

G2021 = fixlib.G2021
G2023 = fixlib.G2023
G2024 = fixlib.G2024

A = "https://web.archive.org/web/"  # brevity

fixes = {
 "AMIGO FLNG Terminal": ("giignl 2021 report: dead giignl.org pdf -> live cdn copy", [
   ("giignl 2021 -> cdn", "GIIGNL_Annual_Report_November2021",
    ("swap",
     "https://giignl.org/wp-content/uploads/2021/11/GIIGNL_Annual_Report_November2021.pdf",
     G2021)),
 ]),
 "Costa Azul LNG Terminal": ("background refs: giignl 2024 -> live cdn; naturalgasintel dead -> wayback", [
   ("giignl 2024 -> cdn", "GIIGNL-2024-Annual-Report-1",
    ("swap",
     "https://giignl.org/wp-content/uploads/2024/06/GIIGNL-2024-Annual-Report-1.pdf",
     G2024)),
   ("naturalgasintel dead -> wayback", "121779-energ",
    ("swap",
     "https://www.naturalgasintel.com/articles/121779-energ%C3%ADa-costa-azul-fid-still-set-for-second-quarter-pending-export-approval",
     A + "20200508200701/https://www.naturalgasintel.com/articles/121779-energ%C3%ADa-costa-azul-fid-still-set-for-second-quarter-pending-export-approval")),
 ]),
 "Vista Pacifico LNG Terminal": ("background refs: giignl 2023 -> live cdn; semprainfrastructure dead -> wayback", [
   ("giignl 2023 -> cdn", "GIIGNL_2023_Annual_Report_July14",
    ("swap",
     "https://giignl.org/wp-content/uploads/2023/07/GIIGNL_2023_Annual_Report_July14.pdf",
     G2023)),
   ("semprainfrastructure 404 -> wayback", "semprainfrastructure.com/what-we-do",
    ("swap",
     "https://semprainfrastructure.com/what-we-do/lng-net-zero-solutions/vista-pacifico-lng",
     A + "20241204111314/https://semprainfrastructure.com/what-we-do/lng-net-zero-solutions/vista-pacifico-lng")),
 ]),
 "Pichilingue LNG Terminal": ("giignl 2019 report: dead giignl.org pdf -> wayback archive", [
   ("giignl 2019 -> wayback", "giignl_annual_report_2019-compressed",
    ("swap",
     "https://giignl.org/sites/default/files/PUBLIC_AREA/Publications/giignl_annual_report_2019-compressed.pdf",
     A + "20210813084554/https://giignl.org/sites/default/files/PUBLIC_AREA/Publications/giignl_annual_report_2019-compressed.pdf")),
 ]),
 "Coatzacoalcos LNG Terminal (CFE)": ("cfenergia call-for-interest pdf dead -> wayback archive", [
   ("cfenergia 404 -> wayback", "Call-to-know-the-interest-liquefaction-plant-_3",
    ("swap",
     "https://www.cfenergia.com/wp-content/uploads/2022/11/Call-to-know-the-interest-liquefaction-plant-_30112022_English_FINAL.pdf",
     A + "20240908154339/https://www.cfenergia.com/wp-content/uploads/2022/11/Call-to-know-the-interest-liquefaction-plant-_30112022_English_FINAL.pdf")),
 ]),
 "Lakach Field FLNG Terminal": ("oil&gas magazine dead -> wayback archive", [
   ("oilandgas 404 -> wayback", "producion-en-lakach-arrancaria-en-2021",
    ("swap",
     "https://oilandgasmagazine.com.mx/2022/11/producion-en-lakach-arrancaria-en-2021/",
     A + "20260130012529/https://oilandgasmagazine.com.mx/2022/11/producion-en-lakach-arrancaria-en-2021/")),
 ]),
 "Saguaro Energía LNG Terminal": ("gem lng-timelines briefing (410) -> wayback archive", [
   ("gem briefing 410 -> wayback", "GEM-Briefing-LNG-Terminal-Development-Timelines",
    ("swap",
     "https://globalenergymonitor.org/wp-content/uploads/2022/04/GEM-Briefing-LNG-Terminal-Development-Timelines.pdf",
     A + "20260325212339/https://globalenergymonitor.org/wp-content/uploads/2022/04/GEM-Briefing-LNG-Terminal-Development-Timelines.pdf")),
 ]),
 "Salina Cruz LNG Terminal (CFE)": ("background refs: oil&gas magazine + cfenergia + salinacruz dead -> wayback archives", [
   ("oilandgas texas-tuxpan 404 -> wayback", "gasoducto-texas-tuxpan-conectaria-con-dos-bocas",
    ("swap",
     "https://oilandgasmagazine.com.mx/2022/06/gasoducto-texas-tuxpan-conectaria-con-dos-bocas/",
     A + "20220621134109/https://oilandgasmagazine.com.mx/2022/06/gasoducto-texas-tuxpan-conectaria-con-dos-bocas/")),
   ("oilandgas sener-consulta 404 -> wayback", "sener-prepara-consulta-indigena-en-oaxaca",
    ("swap",
     "https://oilandgasmagazine.com.mx/2022/06/sener-prepara-consulta-indigena-en-oaxaca-por-gasoducto/",
     A + "20220713203107/https://oilandgasmagazine.com.mx/2022/06/sener-prepara-consulta-indigena-en-oaxaca-por-gasoducto/")),
   ("cfenergia convocatoria 404 -> wayback", "Convocatoria-Versio",
    ("swap",
     "https://www.cfenergia.com/wp-content/uploads/2021/08/Convocatoria-Versio%CC%81n-Final-30082021.pdf",
     A + "20260414095316/https://www.cfenergia.com/wp-content/uploads/2021/08/Convocatoria-Versio%CC%81n-Final-30082021.pdf")),
   ("salinacruzlng dns-gone -> wayback", "salinacruzlng.com",
    ("swap",
     "https://www.salinacruzlng.com/",
     A + "20260519221836/https://www.salinacruzlng.com/")),
 ]),
 "Salina Cruz LNG Terminal (Pilot/GFI)": ("salinacruzlng.com (dns gone) -> wayback archive", [
   ("salinacruzlng dns-gone -> wayback", "salinacruzlng.com",
    ("swap",
     "https://www.salinacruzlng.com/",
     A + "20260519221836/https://www.salinacruzlng.com/")),
 ]),
 "Gato Negro Manzanillo LNG Terminal": ("oil&gas magazine dead + malformed doubled url -> single wayback archive", [
   ("gato negro 404 + doubled url -> wayback", "gato-negro-solicita-permiso",
    ("swap",
     "https://oilandgasmagazine.com.mx/2024/05/gato-negro-solicita-permiso-para-exportar-gas-natural-a-mexico-y-reexportar-gnl/,%20https://oilandgasmagazine.com.mx/2024/05/gato-negro-solicita-permiso-para-exportar-gas-natural-a-mexico-y-reexportar-gnl/",
     A + "20250524070219/https://oilandgasmagazine.com.mx/2024/05/gato-negro-solicita-permiso-para-exportar-gas-natural-a-mexico-y-reexportar-gnl/")),
 ]),
 "Andrés LNG Terminal": ("argus domrep ref: dead url -> live argusmedia article (relocated)", [
   ("argus domrep dead -> live relocated", "domrep-converts",
    ("swap",
     "https://www.argusmedia.com/en/news/2158007-domrep-converts-oilbased-power-to-gas",
     "https://www.argusmedia.com/en/news-and-insights/latest-market-news/2123188-domrep-converts-oil-based-power-to-gas-update")),
 ]),
}

s = gw.session()
diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}
import pickle
pickle.dump(diffs, open("diffs_mexico.pkl", "wb"))
print("\n\nALL DIFFS BUILT OK ->", len(diffs), "pages")
