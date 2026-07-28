#!/usr/bin/env python3
"""HUMAN-REVIEW section 3 dead-ref repairs (2026-07-27, inline research pass).

Eight Background refs previously queued as "dead, no archive" turned out to be
recoverable via a live relocated URL, a live syndication/wire copy, or the same
article on a live host. Two others (Tergás sema.rs.gov.br, Terminal Gás Sul
itajainaval) stay flagged: confirmed 404 + never archived, and the only live
candidates report a different figure/event than the wiki text. Peru $350m is a
factual question, left to the researcher.
"""
import sys, pickle
sys.path[:0] = [".", "../.."]
import fixlib, gemwiki as gw

SEMPRA_NEW = ('<ref name=":5">{{Cite web|url=https://www.naturalgasworld.com/'
    'u.s.-permits-sempra-to-re-export-lng-from-mexico-102750|title=U.S. allows '
    'Sempra to re-export LNG from Mexico|date=December 20, 2022|website=Natural '
    'Gas World (Reuters)|url-status=live}}</ref>')

BAHIA_NEW = ("<ref>[https://jpt.spe.org/petrobras-disqualifies-excelerates-bid-"
    "on-lng-terminal Petrobras Disqualifies Excelerate's Bid on LNG Terminal], "
    "Journal of Petroleum Technology (JPT), June 22, 2021 (reporting Reuters).</ref>")

PROGRESO_NEW = ('<ref>{{Cite web|url=https://www.offshore-energy.biz/'
    'kogas-plans-mexico-lng-import-terminal/|title=Kogas plans Mexico LNG import '
    'terminal|date=August 12, 2016|website=Offshore Energy|url-status=live}}</ref>')

CRONISTA_NEW = ('<ref name=":2">{{Cite web|url=https://www.cronista.com/negocios/'
    'gnl-excelerate-se-aleja-de-su-proyecto-con-tgs-y-suena-con-el-negocio-que-'
    'abrira-la-planta-de-ypf/|title=GNL: Excelerate se aleja de su proyecto con '
    'TGS y sueña con el negocio que abrirá la planta de YPF|date=May 31, 2024|'
    'website=El Cronista|url-status=live}}</ref>')

BLOOMBERG_NEW = ('<ref>{{Cite web|url=https://www.bloomberglinea.com/latinoamerica/'
    'argentina/tgs-paraliza-proyecto-de-gnl-en-argentina-mientras-ypf-busca-'
    'patrocinadores/|title=TGS pone "a la espera" proyecto de GNL en Argentina '
    'mientras YPF busca patrocinadores|date=May 8, 2024|website=Bloomberg Línea|'
    'url-status=live}}</ref>')

CANAL9_NEW = ('<ref>{{Cite web|url=https://olca.cl/articulo/nota.php?id=109072|'
    'title=GNL Talcahuano irá a la Corte Suprema para salvar proyecto de gas '
    'natural|date=November 19, 2021|website=Canal 9 Bío Bío Televisión (vía OLCA)'
    '|url-status=live}}</ref>')

ABOL_OLD = "https://abolbrasil.org.br/posts/polimix-planeja-iniciar-obra-de-us-650-milhoes-em-porto-no-es/"
ABOL_NEW = "https://abolbrasil.org.br/noticias/noticias/polimix-planeja-iniciar-obra-de-us-650-milhoes-em-porto-no-es"
GNLG_OLD = "https://gnlglobal.com/mercados/america-latina-y-el-caribe/corte-suprema-de-chile-obliga-a-gasoducto-del-pacifico-a-dar-respuesta-fundada-a-gnl-talcahuano-para-no-aceptar-conexion/"
GNLG_NEW = "https://gnlglobal.com/corte-suprema-de-chile-obliga-a-gasoducto-del-pacifico-a-dar-respuesta-fundada-a-gnl-talcahuano-para-no-aceptar-conexion/"

fixes = {
 "Costa Azul LNG Terminal": (
   "background ref: dead nasdaq/reuters sempra re-export -> live natural gas world copy",
   [("sempra re-export dead -> natural gas world",
     "u.s.-allows-sempra-to-re-export-lng-from-mexico", ("full", SEMPRA_NEW))]),
 "Vista Pacifico LNG Terminal": (
   "background ref: dead nasdaq/reuters sempra re-export -> live natural gas world copy",
   [("sempra re-export dead -> natural gas world",
     "u.s.-allows-sempra-to-re-export-lng-from-mexico", ("full", SEMPRA_NEW))]),
 "Progreso LNG Terminal": (
   "background ref: dead ngv journal -> live offshore energy (kogas) copy",
   [("ngv journal dead -> offshore energy",
     "korean-energy-company-will-build-lng-terminal-in-yucatan", ("full", PROGRESO_NEW))]),
 "Bahia FSRU": (
   "background ref: dead nasdaq/reuters -> live jpt copy (petrobras disqualifies excelerate)",
   [("nasdaq/reuters dead -> jpt",
     "brazils-petrobras-disqualifies-excelerate", ("full", BAHIA_NEW))]),
 "Presidente Kennedy FSRU": (
   "background ref: dead abol url -> relocated live abol article",
   [("abol relocated url",
     "polimix-planeja-iniciar-obra-de-us-650", ("swap", ABOL_OLD, ABOL_NEW))]),
 "TGS Puerto Galván LNG Terminal": (
   "background refs: dead petrolnews -> el cronista; dead financial post -> bloomberg línea",
   [("petrolnews dead -> el cronista",
     "noticia.php?r=46829", ("full", CRONISTA_NEW)),
    ("financial post dead -> bloomberg línea",
     "tgs-halts-argentina-lng-plant-as-state-run-project-seeks-backers", ("full", BLOOMBERG_NEW))]),
 "Talcahuano FSRU": (
   "background refs: dead gnl global -> relocated url; dead canal 9 -> olca syndication",
   [("gnl global relocated url",
     "corte-suprema-de-chile-obliga-a-gasoducto", ("swap", GNLG_OLD, GNLG_NEW)),
    ("canal 9 dead -> olca syndication",
     "gnl-talcahuano-ira-a-la-corte-suprema-para-salvar", ("full", CANAL9_NEW))]),
}

s = gw.session()
diffs = {}
for t, (summ, fx) in fixes.items():
    diffs[t] = fixlib.build(s, t, fx)
pickle.dump((fixes, diffs), open("diffs_hr3.pkl", "wb"))
print(f"\n\nALL DIFFS BUILT OK -> {len(diffs)} pages")
