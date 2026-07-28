#!/usr/bin/env python3
"""Spain (2026-07-28): Background-citation repairs across the Spanish terminals.

Almost every dead citation here is a `bit.ly` shortlink laid down around 2017.
The shortener itself still resolves, which is why these look healthy from the
outside -- follow the redirect and the destination is a 404. Repairing them
de-shortens as a side effect: the ref ends up naming the document it actually
cites instead of an opaque five-character token that only bit.ly can resolve.

Order of preference, as in the Italy and Germany passes:

  * relocation -- the Finnish Gas Association moved its seminar slide decks from
    `/sites/default/files/pdf/esitykset/...` to `/wp-content/uploads/...`; that
    is the same Reganosa presentation, so it is cited live.
  * archive -- a content-verified Wayback snapshot. `{{Cite web}}` MERGES (the
    original stays in `url=`, the snapshot goes to `archive-url`/`archive-date`,
    `url-status` flips to `dead`); a bare `[url text]` link has nowhere to put a
    snapshot, so the URL is replaced.
  * re-sourcing -- last resort, for the four cases where nothing survives: the
    Bunkerspot Gijón story (snapshot is a 73-character stub), the Trade Winds
    Reganosa court piece (paywalled), the Loadstar Tenerife grant story, and
    GIIGNL's own news post about El Musel.

Two of those re-sourcings improve on what they replace. The El Musel start-date
claim now also carries Enagás's own Q3-2022 results release, which states the
January 2023 date directly, rather than resting solely on GIIGNL's news post
about it. The Mugardos zoning ruling now cites INAP's report of the Supreme
Court decision, which names the 22 April 2008 TSJ Galicia judgment the sentence
refers to.

`A Barrel Full` is banned project-wide and comes out wherever it appears. On
Mugardos the sentence keeps two other citations, so the ref is simply dropped.
On Cartagena and Huelva it was the sentence's only support, so it is replaced
with real sources -- and in Cartagena's case the replacement is markedly better
than what it removes: a CNMC regulatory report that states the 1989
commissioning and lists all five tank capacities in a single footnote, plus the
BOE environmental declaration for the fifth tank, which lists the other four.

Huelva is the one place where the replacement does not cover everything the
banned source was carrying. AIQBE's Enagás profile confirms the 1988 start (and
the five tanks and 619,500 m3 that the next sentence asserts), but nothing found
supports the "expansions completed in 1992, 2002, 2004, 2006, and 2013" list.
Enagás's own 2005 release describes a fourth tank due in 2006, and the 2004 BOE
filing is that same tank's environmental approval -- so at least two of those
five years may be one project counted twice. The years are left in place and
flagged for human review rather than quietly deleted.

Gascan's English "Projects" page has no snapshot, but its Spanish twin does, and
the Spanish page carries the exact specification the wiki cites -- one 150,000
m3 tank, three primary pumps, three secondary pumps, two vaporizer lines and a
backup submerged-combustion vaporizer. That is the same document in the other
language, so it is used in place of the vanished English version.

Not touched, deliberately: refs that scan as `CHECK 401/403`. Bilbao's two
bit.ly links, the Cabildo de Gran Canaria page (Incapsula) and El Economista
(Akamai) are all bot walls, not dead links -- they load fine for a reader, and
replacing a live citation with an archive would be a downgrade.
"""
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

A = "https://web.archive.org/web/"

# ---------------------------------------------------------------- replacements

# The Bunkerspot original is gone and its snapshot replays as a 73-character
# stub. Bunker Index reported the same 6 March 2017 board decision.
# NOTE: the sentence's "opposition from local political groups" clause is NOT
# supported by this replacement -- logged for human review.
EL_MUSEL_BUNKERING = (
    "<ref>[https://www.bunkerindex.com/articles/article.php?a=18781&h=spains-"
    "official-gazette-confirms-approval-of-lng-bunkering-in-gijon Spain's "
    "official gazette confirms approval of LNG bunkering in Gijon], "
    "''Bunker Index'', 8 Mar. 2017.</ref>")

# GIIGNL's news post is dead but replays cleanly; Enagás's own results release
# of the same date states the January 2023 start directly, so it is added as the
# primary rather than leaving the claim on an archived secondary alone.
EL_MUSEL_START = (
    "<ref>[" + A + "20250611150833/https://giignl.org/el-musel-terminal-to-start-"
    "in-early-2023/ El Musel terminal to start in early 2023]. GIIGNL. October 25, "
    "2022.</ref>"
    "<ref>[https://www.enagas.es/en/press-room/news-room/press-releases/2022-10-25-"
    "np-resultados-3t-2022/ Enagás obtains a net profit of 279.9 million euros in "
    "the first nine months of 2022] (\"The El Musel Terminal (Gijón) is scheduled "
    "to start operating as a logistics terminal in January 2023 and will be able "
    "to supply up to 8 bcm of LNG per year to Europe\"), Enagás press release, "
    "25 Oct. 2022.</ref>")

# Trade Winds' report of the Reganosa court fight is paywalled and unarchived.
# INAP's public-administration bulletin reports the same Supreme Court ruling and
# names the 22 April 2008 TSJ Galicia judgment the sentence is about.
MUGARDOS_COURT = (
    "<ref name=tradewinds>[https://laadministracionaldia.inap.es/noticia.asp?"
    "id=1101614 El Supremo anula el cambio del plan urbanístico que permitió "
    "construir una planta de gas en Mugardos (A Coruña)], INAP, 7 Jun. 2012.</ref>")

# CNMC's report on the Cartagena loading-arms authorisation states the 1989
# commissioning in prose and itemises all five tanks in footnote 8; the BOE
# environmental declaration for the fifth tank independently lists the other
# four with their plant tag numbers.
CARTAGENA_TANKS = (
    "<ref>[https://www.cnmc.es/sites/default/files/5068735.pdf Informe sobre la "
    "propuesta de resolución de la DGPEM por la que se otorga a Enagás Transporte "
    "S.A.U. autorización administrativa del proyecto básico \"Proyecto 069L - "
    "Nuevos brazos de carga en el pantalán pequeño\" en la planta de "
    "regasificación de Cartagena (Murcia)] (expediente INF/DE/496/23: \"entró en "
    "funcionamiento a finales de 1989\"; \"Dos tanques de 150.000 m3, un tanque de "
    "127.000 m3, uno de 105.000 m3 y otro de 55.000 m3\"), CNMC, 15 Dec. 2023."
    "</ref>"
    "<ref>[https://boe.es/diario_boe/txt.php?id=BOE-A-2008-15191 Resolución de 24 "
    "de julio de 2008, de la Secretaría de Estado de Cambio Climático, por la que "
    "se formula declaración de impacto ambiental del proyecto 5.º Tanque de "
    "almacenamiento de GNL en la planta de recepción, almacenamiento y "
    "regasificación de GNL de ENAGAS S.A., término municipal de Cartagena "
    "(Murcia)], ''Boletín Oficial del Estado'', 12 Sept. 2008.</ref>")

# AIQBE's member profile for Enagás covers the 1988 start and the plant's
# current configuration. It does NOT cover the list of expansion years.
HUELVA_START = (
    "<ref>[https://aiqbe.es/asociado.php/enagas/8 Enagás - Planta de Huelva] "
    "(\"Su construcción se inició en 1985 y la primera descarga de GNL en junio de "
    "1988... La planta tiene cinco tanques y una capacidad de almacenamiento de "
    "619.500 m3 de GNL\"), AIQBE (Asociación de Industrias Químicas, Básicas y "
    "Energéticas de Huelva), accessed July 28, 2026.</ref>")

# The English "Projects" page was never archived; its Spanish twin was, and
# carries the same specification the wiki cites.
GASCAN_PROJECTS = (
    "<ref name=gascan>[" + A + "20160525053426/http://www.gascan.es/web-es/"
    "proyectos Proyectos], Gascan (Spanish-language original of the since-removed "
    "English \"Projects\" page), archived 25 May 2016.</ref>"
    "<ref>[https://www.enagas.es/en/press-room/news-room/"
    "press-releases/2011-09-16_gascan/ Enagas acquires 60% of Gascan], Enagas "
    "press release, 16 Sept. 2011.</ref>")

GASCAN_EPC = (
    "<ref>[https://www.laprovincia.es/economia/2008/12/17/"
    "acciona-tecnicas-reunidas-construiran-terminales-10948194.html Acciona y "
    "Tecnicas Reunidas construiran las terminales de gas de Canarias], "
    "''La Provincia'' (Europa Press), 17 Dec. 2008.</ref>"
    "<ref>[https://cincodias.elpais.com/cincodias/2008/12/17/empresas/"
    "1229684344_850215.html Acciona y Tecnicas Reunidas construiran dos "
    "terminales de gas por 500 millones], ''Cinco Dias'' (EFE), "
    "17 Dec. 2008.</ref>")

TENERIFE_GRANT = (
    "<ref>[https://theloadstar.com/port-tenerife-container-shipping-west-africa/ "
    "EU grant a boost to Tenerife ambitions to become top regional box shipping "
    "hub], ''The Loadstar'', 11 Dec. 2014.</ref>")

# ---------------------------------------------------------------------- fixes

BAN = "banned source (a barrel full) removed"
BAN_SUB = "banned source (a barrel full) replaced with primary sources"

fixes = {
    "Barcelona LNG Terminal": (
        "background refs: dead lng world news shortlink -> wayback archive", [
            ("bit.ly -> dead lngworldnews -> wayback", "2iOwdNu", ("swap",
             "http://bit.ly/2iOwdNu",
             A + "20191112234620/https://www.lngworldnews.com/enagas-port-of-"
             "barcelona-to-set-up-lng-distribution-hub/")),
        ]),
    "Cartagena LNG Terminal (Spain)": (
        "background refs: " + BAN_SUB + "; dead lng world news shortlink -> "
        "wayback archive", [
            ("abarrelfull -> cnmc report + boe declaration", "2epN83S",
             ("full", CARTAGENA_TANKS)),
            ("bit.ly -> dead lngworldnews -> wayback", "2eqh2VQ", ("swap",
             "http://bit.ly/2eqh2VQ",
             A + "20191211170739/https://www.lngworldnews.com/enagas-boosts-loading-"
             "ops-at-cartagena-lng-terminal/")),
        ]),
    "El Musel LNG Terminal": (
        "background refs: dead shortlinks + fluor soft-404 -> wayback; bunkerspot "
        "and giignl news post re-sourced", [
            ("bit.ly -> fluor soft-404 -> wayback", "2epGLgP", ("swap",
             "http://bit.ly/2epGLgP",
             A + "20260412162754/https://www.fluor.com/projects/el-musel-lng-"
             "terminal-epcm")),
            ("bit.ly -> dead lngworldnews -> wayback", "2epIdQn", ("swap",
             "http://bit.ly/2epIdQn",
             A + "20171227123044/https://www.lngworldnews.com/enagas-musel-lng-"
             "terminal-to-be-mothballed-after-completion-spain/")),
            ("bunkerspot dead, snapshot is a stub -> bunker index",
             "bunkerspot.com/europe/43634", ("full", EL_MUSEL_BUNKERING)),
            ("giignl news post 404 -> wayback + enagas primary",
             "giignl.org/el-musel-terminal-to-start", ("full", EL_MUSEL_START)),
            # marker is the Cite-web title, not the URL: the first fix above
            # rewrites a bare link to a wayback URL that also contains the
            # fluor.com path, which would make a URL marker ambiguous.
            ("fluor soft-404 -> wayback merge", "Fluor EPCM Project",
             ("full",
              "<ref>{{Cite web|url=https://www.fluor.com/projects/el-musel-lng-"
              "terminal-epcm|title=Enagás El Musel LNG Terminal: Fluor EPCM Project "
              "in Spain|date=2023-12-07|website=www.fluor.com|url-status=dead"
              "|archive-url=" + A + "20260412162754/https://www.fluor.com/projects/"
              "el-musel-lng-terminal-epcm|archive-date=2026-04-12|access-date="
              "2026-07-20}}</ref>")),
        ]),
    "Gran Canaria LNG Terminal": (
        "background refs: vanished gascan and tecnicas reunidas pages -> "
        "archived spanish original and the europa press/efe wires", [
            ("tecnicas reunidas pdf dead and unarchived -> two 2008 wire reports",
             "tecnicasreunidas.es", ("full", GASCAN_EPC)),
            ("gascan english page dead and unarchived -> archived spanish twin",
             "gascan.es/web-en/projects", ("full", GASCAN_PROJECTS)),
        ]),
    "Huelva LNG Terminal": (
        "background refs: " + BAN_SUB + "; dead lng world news shortlink -> "
        "wayback archive", [
            ("abarrelfull -> aiqbe (covers 1988 start, not the expansion years)",
             "2xyHq8d", ("full", HUELVA_START)),
            ("bit.ly -> dead lngworldnews -> wayback", "2xyTmab", ("swap",
             "http://bit.ly/2xyTmab",
             A + "20170224133812/http://www.lngworldnews.com/spain-huelva-lng-"
             "terminal-celebrates-25th-anniversary/")),
        ]),
    "Mugardos LNG Terminal": (
        "background refs: " + BAN + "; dead shortlinks -> wayback/relocation; "
        "paywalled trade winds piece re-sourced", [
            ("bit.ly -> dead reganosa page -> wayback", "2wj5mOb", ("swap",
             "http://bit.ly/2wj5mOb",
             A + "20250808234416/https://mugardos.reganosa.com/en/lng-terminal-0")),
            ("abarrelfull -> drop", "2wj9u0y", ("full", "")),
            ("bit.ly -> relocated finnish gas association deck", "2wjf5E6", ("swap",
             "http://bit.ly/2wjf5E6",
             "https://www.kaasuyhdistys.fi/wp-content/uploads/2018/12/LNG-market-in-"
             "Spain-Reganosa-Rodrigo-Diaz-Ibarra.pdf")),
            ("bit.ly -> dead lngworldnews -> wayback", "2wj4aKQ", ("swap",
             "http://bit.ly/2wj4aKQ",
             A + "20191017051141/https://www.lngworldnews.com/mugardos-lng-terminal-"
             "to-receive-first-q-flex-carrier/")),
            ("bit.ly -> paywalled trade winds -> inap report of the ruling",
             "2xyDQeh", ("full", MUGARDOS_COURT)),
        ]),
    "Sagunto LNG Terminal": (
        "background refs: dead lng world news shortlink -> wayback archive", [
            ("bit.ly -> dead lngworldnews -> wayback", "2wiH0E8", ("swap",
             "http://bit.ly/2wiH0E8",
             A + "20190822115644/https://www.lngworldnews.com/enagas-increases-stake-"
             "in-two-lng-facilities/")),
        ]),
    "Tenerife LNG Terminal": (
        "background refs: dead shortlinks and vanished gascan page -> live "
        "loadstar copy, wayback, the 2008 wires and the archived spanish twin", [
            ("bit.ly -> dead tecnicas reunidas pdf -> two 2008 wire reports",
             "2xy8XXu", ("full", GASCAN_EPC)),
            ("gascan english page dead and unarchived -> archived spanish twin",
             "gascan.es/web-en/projects", ("full", GASCAN_PROJECTS)),
            ("bit.ly -> dead loadstar url -> live loadstar article", "2xyfCB1",
             ("full", TENERIFE_GRANT)),
            ("bit.ly -> dead eldia -> wayback", "2xxUA5r", ("swap",
             "http://bit.ly/2xxUA5r",
             A + "20170214155716/http://eldia.es/tenerife/2017-02-14/1-Enagas-preve-"
             "invertir-millones-euros-terminal-Tenerife.htm")),
        ]),
}

if __name__ == "__main__":
    s = gw.session()
    diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}
    import pickle
    pickle.dump(diffs, open("diffs_spain.pkl", "wb"))
    print("\n\nALL DIFFS BUILT OK ->", len(diffs), "pages")
