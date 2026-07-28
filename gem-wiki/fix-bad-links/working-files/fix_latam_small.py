#!/usr/bin/env python3
"""Background-citation fixes for the 16 small Latin America / Caribbean countries.

Usage:
  python3 fix_latam_small.py            # dry run: build and print every diff
  python3 fix_latam_small.py --save     # guarded-save each page, then cite-check

Two sources of fixes, merged per page:

  MANUAL   - hand-authored and individually content-verified: GIIGNL/IGU
             standard-format and relocation fixes, refs recovered by research
             (with the evidence quoted in the comment), and same-URL dedupes.
  AUTO     - Wayback swaps for refs that are confirmed dead and whose snapshot
             passed content verification in verify_latam_snaps.py (result
             PASS). Loaded from verify_latam.json; any (page, n) that MANUAL
             already handles is skipped so the two never collide.

Action forms:
  ("swap", old_url, new_url)          replace a URL inside the located ref
  ("full", new_ref_text)              replace the whole located ref
  ("archive", url, snapshot)          keep url= and record the snapshot in
                                      archive-url/archive-date/url-status
  ("raw", old_sub, new_sub, n, idx)   page-level substring surgery, for
                                      dedupes where duplicate refs share
                                      byte-identical wikitext
"""
import json
import re
import sys

import fixlib
import gemwiki as gw
from scan_background_refs import URL_RE, norm_url

WB = "https://web.archive.org/web/"
G = fixlib.giignl

# --------------------------------------------------------------------------
# IGU restructured /resources/<slug> -> /igu-reports/<slug>, same slug, same
# document. Verified 2026-07-27: both new URLs return 200 with the matching
# report title; both old URLs 404.
IGU24_OLD = "https://www.igu.org/resources/2024-world-lng-report/"
IGU24_NEW = "https://www.igu.org/igu-reports/2024-world-lng-report"
IGU21_NEW = "https://www.igu.org/igu-reports/world-lng-report-2021"

MANUAL = {
    # ---------------------------------------------------------------- Andrés
    "Andrés LNG Terminal": ("background: repair dead giignl/igu/aes refs, restore recovered lng world news source, dedupe ijglobal", [
        # [11] MALFORMED: an internal wikilink, not a URL -> standard format
        ("giignl 2021 malformed wikilink -> standard format",
         "giignl 2021 annual report apr27",
         ("full", G(fixlib.G2021, 2021, name=":1"))),
        ("giignl 2024 dead -> standard format",
         "GIIGNL Annual Report 2024 (pp 45-46)",
         ("full", G(fixlib.G2024, 2024, name=":322", page="45-46"))),
        ("igu 2024 report relocated",
         "2024 World LNG Report (p 154)",
         ("swap", IGU24_OLD, IGU24_NEW)),
        # [5] dead bit.ly. lngworldnews.com folded into offshore-energy.biz;
        # no content snapshot of the original exists (only a 302 capture), so
        # this is the relocated live copy. Verified 2026-07-27: byline "LNG
        # World News", datePublished 2015-08-13, body has "LNG reloads onto
        # vessels between 10,000 cbm-60,000 cbm" and the bunkering language.
        ("dead bit.ly -> relocated lng world news copy",
         "bit.ly/2esD4qR",
         ("full", "<ref name=lngwn>[https://www.offshore-energy.biz/"
                  "aes-andres-lng-terminal-to-offer-trans-shipment-bunkering/ "
                  "AES Andres LNG terminal to offer trans-shipment, bunkering,] "
                  "LNG World News (Offshore Energy), 13 Aug. 2015</ref>")),
        # [1]/[2] cite the same ijglobal case study; [1] already defines
        # name=":0", so it stays the definition and [2] becomes a reuse.
        ("dedupe ijglobal case study", None,
         ("dedupe", "https://ijglobal.com/articles/14464/aes-andres-project-in-dominican-republic",
          "ijglobal-andres")),
    ]),
    # -------------------------------------------------------------- Acajutla
    "Acajutla FSRU": ("background: cite giignl 2024 in standard format", [
        ("giignl 2024 dead -> standard format",
         "GIIGNL Annual Report 2024 (p 46)",
         ("full", G(fixlib.G2024, 2024, name=":322", page="46"))),
    ]),
    # ----------------------------------------------------------- Old Harbour
    "Old Harbour FSRU": ("background: cite giignl 2021 and 2024 in standard format", [
        ("giignl 2021 dead -> standard format",
         "GIIGNL_Annual_Report_November2021.pdf",
         ("full", G(fixlib.G2021, 2021))),
        ("giignl 2024 dead -> standard format",
         "GIIGNL Annual Report 2024 (p 46)",
         ("full", G(fixlib.G2024, 2024, name=":32", page="46"))),
    ]),
    # -------------------------------------------------------- Puerto Sandino
    "Puerto Sandino FSRU": ("background: repair dead giignl/igu refs and nfe q2 2024 release", [
        ("igu 2021 report relocated, empty title filled in",
         "igu.org/resources/world-lng-report-2021",
         ("full", f"<ref>{{{{Cite web|url={IGU21_NEW}|title=World LNG Report "
                  f"2021|website=IGU|url-status=live}}}}</ref>")),
        ("giignl 2021 malformed wikilink -> standard format",
         "giignl 2021 annual report apr27",
         ("full", G(fixlib.G2021, 2021))),
        ("giignl 2024 dead -> standard format",
         "GIIGNL Annual Report 2024 (p 45)",
         ("full", G(fixlib.G2024, 2024, name=":322", page="45"))),
        # [17] ir.newfortressenergy.com is gone (connection error, not a bot
        # wall). Verified 2026-07-27: the Mar 2025 snapshot is a full 388 KB
        # page titled "New Fortress Energy Announces Second Quarter 2024
        # Results" and says growth "is expected to further accelerate upon the
        # completion of our Nicaragua terminal and power asset in the fourth
        # quarter of 2024" -- exactly the cited claim.
        ("dead nfe ir release -> wayback snapshot",
         "new-fortress-energy-announces-second-quarter-2024-results",
         ("full",
          "<ref name=\":5\">{{Cite web|url=https://ir.newfortressenergy.com/"
          "news-releases/news-release-details/new-fortress-energy-announces-"
          "second-quarter-2024-results|title=New Fortress Energy Announces "
          "Second Quarter 2024 Results, August 9, 2024 at 7:00 AM EDT"
          "|date=2024-08-09|website=New Fortress Energy|archive-url="
          + WB + "20250319234654/https://ir.newfortressenergy.com/"
          "news-releases/news-release-details/new-fortress-energy-announces-"
          "second-quarter-2024-results|archive-date=2025-03-19"
          "|url-status=dead}}</ref>")),
    ]),
    # --------------------------------------------------------- Costa Norte
    "Costa Norte LNG Terminal": ("background: cite giignl 2024 in standard format, igu report relocated", [
        ("giignl 2024 dead -> standard format",
         "GIIGNL Annual Report 2024 (pp 45, 47)",
         ("full", G(fixlib.G2024, 2024, name=":322", page="45, 47"))),
        ("igu 2024 report relocated",
         "2024 World LNG Report (p 157)",
         ("swap", IGU24_OLD, IGU24_NEW)),
    ]),
    # ------------------------------------------------------------- Sinolam
    # [1] was flagged SOFT404, but its archive-url is a healthy 200 capture
    # titled "LNG shipping firm Gaslog strikes tanker deal with Panama power
    # project" and naming Sinolam (verified 2026-07-27); the live reuters.com
    # URL 401s to bots only. No repair needed.
    "Sinolam LNG Terminal": ("background: cite giignl 2022 in standard format", [
        ("giignl 2022 dead -> standard format",
         "GIIGNL2022_Annual_Report_May24.pdf",
         ("full", G(fixlib.G2022, 2022, name=":2", page="55"))),
    ]),
    # ----------------------------------------------------------- Ocean Cay
    # All four Background sources were dead bit.ly shortlinks. Each shortlink
    # still 301s, so the original target URL is recoverable from it, and every
    # target was then run down individually.
    "Ocean Cay LNG Terminal": ("background: restore all four dead bit.ly refs from their original targets", [
        # bit.ly/2nxJYhG -> giignl.org/system/files/Q-FlexQ-Max_acceptability
        # _database_-_March_.pdf. Verified 2026-07-27: the archived PDF (10 pp,
        # application/pdf) is GIIGNL's regas-terminal/Q-Flex-Q-Max
        # acceptability database and carries the row "AES Ocean Cay | North
        # America | Atlantic | Bahamas | Ocean Cay | Cancelled | 2014".
        # Retitled: the old ref title implied a page about Ocean Cay, but the
        # document is a global terminal database that merely lists it.
        ("dead bit.ly -> archived giignl acceptability database",
         "bit.ly/2nxJYhG",
         ("full", "<ref>[" + WB + "20160818011142/http://giignl.org/system/"
                  "files/q-flexq-max_acceptability_database_-_march_.pdf "
                  "Q-Flex/Q-Max Acceptability Database (regasification "
                  "terminal overview),] GIIGNL, accessed April 2017</ref>")),
        # bit.ly/2esTqQg -> hydrocarbons-technology.com/projects/
        # oceancaylngterminala/, which now 301s to the same path on
        # offshore-technology.com (GlobalData folded the two titles together).
        # offshore-technology.com 403s to bots, so verified via its Dec 2024
        # Wayback capture, 2026-07-27: title "Ocean Cay LNG Terminal and
        # Pipeline - Offshore Technology", body has the 840mmcfd undersea
        # pipeline and the Broward County, Florida delivery point.
        # name=hydrocarbons must survive -- six reuses point at it.
        ("dead bit.ly -> relocated offshore technology project page",
         "bit.ly/2esTqQg",
         ("full", "<ref name=hydrocarbons>[https://www.offshore-technology.com/"
                  "projects/oceancaylngterminala/ Ocean Cay LNG Terminal and "
                  "Pipeline, Bahamas,] Offshore Technology (formerly "
                  "Hydrocarbons Technology), accessed September 2017</ref>")),
        # bit.ly/2etikiS -> bahamasb2b.com/news/wmview.php?ArtID=5034, whose
        # old CMS view script now 500s; the site relocated its archive to
        # dated paths. Verified live 2026-07-27: title "LNG Opposition Mounts",
        # dated April 12, 2005 (matching the ref), with ReEarth's petition and
        # Sam Duncombe's objections.
        ("dead bit.ly -> relocated bahamas b2b article",
         "bit.ly/2etikiS",
         ("full", "<ref name=b2b>[https://www.bahamasb2b.com/news/2005/04/"
                  "lng-opposition-mounts LNG Opposition Mounts,] Bahamas B2B, "
                  "12 Apr. 2005</ref>")),
        # bit.ly/2esB1CY -> thenassauguardian.com Joomla URL (id=11181), now
        # 404 after the paper's site migration. Verified 2026-07-27: the Nov
        # 2011 snapshot carries "Failed diplomacy in LNG bid", byline Candia
        # Dames, and the WikiLeaks embassy-cable material the sentence cites.
        ("dead bit.ly -> archived nassau guardian original",
         "bit.ly/2esB1CY",
         ("full", "<ref name=guardian>[" + WB + "20111105085908/http://www."
                  "thenassauguardian.com/index.php?option=com_content&view="
                  "article&id=11181&Itemid=100 Failed diplomacy in LNG bid,] "
                  "The Nassau Guardian, 24 Jun. 2011</ref>")),
    ]),
    # ------------------------------------------------------------- Peru LNG
    "Peru LNG Terminal": ("background: replace dead docplayer deck with the ijglobal project case study", [
        # The dead ref was a docplayer scrape of a 2008 Peru LNG conference
        # deck; no Wayback capture of the docplayer URL exists and the deck
        # itself is nowhere online. Swapped to IJGlobal's project case study
        # (now hosted on Green Street Infrastructure after a domain move).
        # Verified live 2026-07-27: it states the IFC US$300m loan, the IDB
        # US$400m A-loan and US$400m B-loan, K-Exim US$300m, and Sace US$250m.
        # CAVEAT for review: it documents a planned US$200m Banco de Credito
        # local-bond tranche, not the "upwards of $350 million" the wiki
        # sentence claims -- that figure is unsourced here and queued in
        # HUMAN-REVIEW.md as a factual question, not a citation problem.
        ("dead docplayer deck -> ijglobal case study",
         "docplayer.net/31684090",
         ("full", "<ref>{{Cite web|url=https://infrastructure.greenstreet.com/"
                  "articles/53755/peru-us-38bn-peru-lng-project|title=Peru: "
                  "US$3.8bn Peru LNG Project|date=January 29, 2009"
                  "|website=IJGlobal (Green Street Infrastructure)"
                  "|url-status=live}}</ref>")),
    ]),
    # -------------------------------------------------- San Pedro de Macoris
    "San Pedro de Macoris LNG Terminal": ("background: restore two dead bit.ly refs from archived originals", [
        # Verified 2026-07-27: snapshot of the original laht.com article id
        # 460768 reads "BW Gas and InterEnergy Holdings will invest $350
        # million to build a Liquefied Natural Gas terminal in San Pedro de
        # Macoris ... set for completion in 2014."
        ("dead bit.ly -> archived latin american herald tribune original",
         "bit.ly/2eK9OMe",
         ("full", "<ref>[" + WB + "20180703040810/http://www.laht.com/"
                  "article.asp?ArticleId=460768&CategoryId=14092 Firms to "
                  "Build $350 Million LNG Terminal in Dominican Republic,] "
                  "Latin American Herald Tribune, accessed September 2017</ref>")),
        # Verified 2026-07-27: snapshot four days after publication carries
        # minister Castillo's opposition and "the cheapest and most efficient
        # option for the government is to build a pipeline from Andres to San
        # Pedro".
        ("dead bit.ly -> archived dominican today original",
         "bit.ly/2eKHzgz",
         ("full", "<ref>[" + WB + "20150328042346/http://dominicantoday.com:80/"
                  "dr/economy/2015/3/24/54601/Dominican-Republics-north-coast-"
                  "needs-a-natural-gas-terminal-Official Dominican Republic's "
                  "north coast needs a natural gas terminal: Official,] "
                  "Dominican Today, 24 Mar. 2015</ref>")),
    ]),
    # ----------------------------------------------------------- Montego Bay
    "Montego Bay LNG Terminal": ("background: cite nfe form s-1/a from sec edgar instead of the retired marketwatch mirror", [
        # MarketWatch blanket-401s all automation, so the status alone proves
        # nothing -- but Wayback has no capture of the whole
        # marketwatch.com/investing/stock/*/SecArticle* pattern for any ticker
        # ever, and that legacy URL form is gone from the current site. The
        # underlying document is NFE's Form S-1/A; EDGAR is the durable copy.
        # Verified 2026-07-27 on EDGAR (CIK 1749723, acc 0001140361-18-045661):
        # "The Montego Bay Terminal also consists of an ISO loading facility
        # that can transport LNG to all of our industrial and manufacturing
        # ("small-scale") sales across the island." Amendment No. 1 is the
        # 2018-12-24 filing; NFE filed no S-1 in March 2019, so the wiki's
        # "Mar 26, 2019" was MarketWatch's repost date, not the filing date.
        ("retired marketwatch sec mirror -> sec edgar primary",
         "SecArticle?countryCode=US&guid=13123046",
         ("full", "<ref>[https://www.sec.gov/Archives/edgar/data/1749723/"
                  "000114036118045661/s002392x8_s1a.htm Amendment No. 1 to "
                  "Form S-1: New Fortress Energy LLC,] U.S. Securities and "
                  "Exchange Commission (EDGAR), filed December 24, 2018.</ref>")),
    ]),
    # -------------------------------------------------------- Island Power
    "Island Power Producers LNG Terminal": ("background: dedupe repeated economic times ref", [
        ("dedupe economic times ref", None,
         ("dedupe", "https://energy.economictimes.indiatimes.com/news/oil-and-gas/"
                    "inox-bags-contract-to-build-bahamas-first-mini-lng-terminal-"
                    "for-cruise-ship-power/115168906", "et-inox")),
    ]),
    # ---------------------------------------------------------- Manzanillo DR
    "Manzanillo (Dominican Republic) LNG Terminal": ("background: repair dead dominican today refs, dedupe ion analytics", [
        ("dedupe ion analytics", None,
         ("dedupe", "https://ionanalytics.com/insights/infralogic/"
                    "twelve-banks-helped-finance-mgp-project/", "ion-mgp")),
    ]),
    # ------------------------------------------------------------------- Ilo
    "Ilo LNG Terminal": ("background: repair dead citations with archived copies, dedupe repeated refs", [
        # [4] cited eldiario.net's mobile-redirect wrapper (movil/index.php),
        # which is dead and was never captured. The underlying desktop article
        # was: verified 2026-07-27, the Jul 22 2019 snapshot is titled
        # "El Diario - Escenario complicado en mercado de gas para Bolivia"
        # (exact title match) and says the Engie plant at Ilo already has an
        # arrangement to import Bolivian gas, per the June 25 2019 accord.
        ("dead eldiario mobile wrapper -> archived desktop article",
         "eldiario.net/movil/index.php?n=17&a=2019",
         ("full", "<ref>{{Cite news|url=" + WB + "20190722150755/https://www."
                  "eldiario.net/noticias/2019/2019_07/nt190722/economia.php"
                  "?n=17&-escenario-complicado-en-mercado-de-gas-para-bolivia"
                  "|title=Escenario complicado en mercado de gas para Bolivia"
                  "|date=July 22, 2019|work=El Diario|language=es}}</ref>")),
        ("dedupe minem/bolivia gas announcement", None,
         ("dedupe", "https://www.gob.pe/jp/institucion/minem/noticias/550547-"
                    "gobierno-agilizara-la-masificacion-del-gas-natural-con-la-"
                    "cooperacion-de-bolivia", "minem-bolivia")),
        ("dedupe diario correo ilo gas story", None,
         ("dedupe", "https://diariocorreo.pe/politica/bolivia-busca-sacar-gas-"
                    "por-puerto-de-ilo-noticia/?ref=dcr", "correo-ilo")),
    ]),
    # -------------------------------------------------------------- Atlantic
    "Atlantic LNG Terminal": ("background: cite giignl in standard format, relocate igu and repsol pages, dedupe trinidad express", [
        # [7] repsol.energy was retired in favour of repsol.com; every Wayback
        # capture of the old URL is a 301 to the identical path on repsol.com.
        # Verified live 2026-07-27: title "Repsol sells LNG assets to Shell for
        # $6.7 billion", body names Atlantic LNG among the divested stakes.
        ("repsol.energy retired -> same release on repsol.com",
         "repsol.energy/en/press-room/press-releases/2013/02/26",
         ("swap", "https://www.repsol.energy/", "https://www.repsol.com/")),
        ("giignl 2024 dead -> standard format",
         "GIIGNL Annual Report 2024 (p 36)",
         ("full", G(fixlib.G2024, 2024, name=":322", page="36"))),
        ("giignl 2025 dead -> standard format",
         "GIIGNL-Annual-Report-2025.pdf",
         ("full", G(fixlib.G2025, 2025))),
        ("igu 2024 report relocated",
         "2024 World LNG Report (p 112)",
         ("swap", IGU24_OLD, IGU24_NEW)),
        # [19]/[36] cite the same live Trinidad Express article ([36] defines
        # name=":10"). The scan called it SOFT404 on a boilerplate "no longer
        # available" string, but the article loads fine -- dedupe only, no URL
        # change.
        ("dedupe trinidad express train 1 story", None,
         ("dedupe", "https://trinidadexpress.com/business/local/bp-confirms-"
                    "plans-to-decommission-train-1/article_c75ca9d6-fee8-11ef-"
                    "a61b-f398b8e86619.html", "express-train1")),
    ]),
}

# (page, ref-number) pairs MANUAL owns; AUTO must not touch them.
MANUAL_OWNS = {
    ("Andrés LNG Terminal", n) for n in (1, 2, 5, 11, 14, 19)
} | {
    ("Acajutla FSRU", 12),
    ("Old Harbour FSRU", 7), ("Old Harbour FSRU", 8),
    ("Puerto Sandino FSRU", 1), ("Puerto Sandino FSRU", 2),
    ("Puerto Sandino FSRU", 10), ("Puerto Sandino FSRU", 17),
    ("Costa Norte LNG Terminal", 16), ("Costa Norte LNG Terminal", 17),
    ("Sinolam LNG Terminal", 7),
    ("San Pedro de Macoris LNG Terminal", 1),
    ("San Pedro de Macoris LNG Terminal", 4),
    ("Montego Bay LNG Terminal", 2),
    ("Island Power Producers LNG Terminal", 1),
    ("Island Power Producers LNG Terminal", 11),
    ("Manzanillo (Dominican Republic) LNG Terminal", 15),
    ("Manzanillo (Dominican Republic) LNG Terminal", 16),
    ("Ilo LNG Terminal", 4),
    ("Ilo LNG Terminal", 9), ("Ilo LNG Terminal", 10),
    ("Ilo LNG Terminal", 12), ("Ilo LNG Terminal", 13),
    ("Peru LNG Terminal", 13),
} | {
    ("Ocean Cay LNG Terminal", n) for n in (1, 2, 9, 11)
} | {
    ("Atlantic LNG Terminal", n) for n in (7, 12, 13, 17, 19, 36, 37)
}

# Pages excluded from the AUTO pass entirely (none at present).
DEFER = set()


def load_auto(path="verify_latam_cache.jsonl"):
    """Wayback swaps for confirmed-dead refs whose snapshot passed content
    verification. Reads the verifier's incremental JSONL cache (valid
    line-by-line even mid-run, unlike its final JSON).
    Returns {page: [(label, marker, action), ...]}."""
    rows = []
    try:
        for line in open(path):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    except FileNotFoundError:
        print(f"note: {path} not found -- MANUAL fixes only", file=sys.stderr)
        return {}
    out = {}
    for r in rows:
        key = (r["page"], r["n"])
        if r.get("result") != "PASS" or key in MANUAL_OWNS or r["page"] in DEFER:
            continue
        # Only repair refs that are actually dead:
        #  - CHECK (401/403/429) means bot-blocked; README says leave alone.
        #  - SOFT404 is excluded entirely. Checked all 6 by hand 2026-07-27 and
        #    5 were false positives: the scan's pattern matched CSS ('404 */
        #    .error' in gnlglobal stylesheets) or site boilerplate ('no longer
        #    available' on trinidadexpress), while the articles were live with
        #    the right titles. Soft-404 detection needs eyes, not automation.
        #  - a URL that returned 200 on the live recheck is alive; the original
        #    failure was transient (e.g. Andrés [4] aesmcac.com, 503 -> 200).
        #  - a 3xx is a redirect, not a death certificate. Bot/JS challenges
        #    answer 307 to scripts and 200 to browsers: every atlanticlng.com
        #    ref in this batch was flagged 307 BROKEN yet loads fine with the
        #    right title (verified 2026-07-27). Redirects need eyes.
        if r["verdict"] != "BROKEN":
            continue
        if str(r.get("recheck", "")).startswith("200"):
            continue
        if r["status"] and 300 <= int(r["status"]) < 400:
            print(f"skip (3xx, needs eyes): {r['page']} [{r['n']}] {r['url']}",
                  file=sys.stderr)
            continue
        out.setdefault(r["page"], []).append(
            (f"dead ({r['verdict']} {r['status']}) -> archive the wayback snapshot",
             ("url", r["url"]), ("archive", r["url"], r["snapshot"])))
    return out


ARCHIVE_URL_RE = re.compile(r"(\|\s*archive-url\s*=\s*)([^|}\n]*)", re.I)
ARCHIVE_DATE_RE = re.compile(r"(\|\s*archive-date\s*=\s*)([^|}\n]*)", re.I)
URL_STATUS_RE = re.compile(r"(\|\s*url-status\s*=\s*)([^|}\n]*)", re.I)
CITE_RE = re.compile(r"\{\{\s*cite\b", re.I)


def apply_archive(ref, url, snapshot):
    """Record `snapshot` as the archive of a dead `url` without discarding it.

    The standing rule is that a ref edit merges rather than replaces: a URL we
    believe dead today may come back, and the original is the citation's
    provenance. So for {{cite}} templates the original stays in url= and the
    snapshot goes into archive-url/archive-date/url-status=dead -- which is
    also what renders correctly on the wiki. Bare [url text] links have no
    field to put it in, so there the URL is replaced outright; nothing is lost
    because a Wayback URL embeds the original it captured.

    Returns None when the ref already carries a populated archive-url -- those
    are already repaired (and two in this batch resolve 200), so leave them be.
    """
    date = re.search(r"/web/(\d{4})(\d{2})(\d{2})", snapshot)
    date = "-".join(date.groups()) if date else ""
    if not CITE_RE.search(ref):
        return ref.replace(url, snapshot)
    m = ARCHIVE_URL_RE.search(ref)
    if m and m.group(2).strip():
        return None
    if m:
        ref = ref[:m.start()] + m.group(1) + snapshot + ref[m.end():]
    else:
        ref = re.sub(r"\}\}(?=\s*</ref>\s*$)",
                     f"|archive-url={snapshot}}}}}", ref, count=1)
    d = ARCHIVE_DATE_RE.search(ref)
    if d and not d.group(2).strip():
        ref = ref[:d.start()] + d.group(1) + date + ref[d.end():]
    elif not d:
        ref = re.sub(r"\}\}(?=\s*</ref>\s*$)",
                     f"|archive-date={date}}}}}", ref, count=1)
    st = URL_STATUS_RE.search(ref)
    if st:
        ref = ref[:st.start()] + st.group(1) + "dead" + ref[st.end():]
    else:
        ref = re.sub(r"\}\}(?=\s*</ref>\s*$)", "|url-status=dead}}", ref,
                     count=1)
    return ref


def find_ref_by_url(text, url):
    """Locate the unique non-autoref ref citing exactly `url`.

    Plain substring matching is wrong here: one cited URL is often a prefix of
    another (eaglelng.com/aruba vs eaglelng.com/aruba/news/...), which matches
    two refs. Compare extracted URLs for equality instead."""
    hits = []
    for m in fixlib.REF_RE.finditer(text):
        ref = m.group(0)
        if "autoref_" in ref[:40]:
            continue
        urls = [u.rstrip(".,);") for u in URL_RE.findall(ref)]
        if url in urls:
            hits.append(ref)
    if len(hits) != 1:
        raise SystemExit(f"url not unique ({len(hits)} refs cite it): {url}")
    return hits[0]


NAME_RE = re.compile(r'<ref\s+name\s*=\s*("([^"]+)"|\'([^\']+)\'|([^\s>/]+))',
                     re.IGNORECASE)


def apply_dedupe(text, label, url, fallback_name):
    """Collapse every non-autoref ref citing `url` into one named definition
    plus `<ref name=... />` reuses.

    Locating by exact URL (not hardcoded wikitext) keeps this robust against
    curly quotes and template differences between the duplicates. If one of the
    duplicates is already named, that one stays as the definition and its name
    wins; otherwise the first becomes the definition using fallback_name."""
    want = norm_url(url)
    hits = []
    for m in fixlib.REF_RE.finditer(text):
        ref = m.group(0)
        if "autoref_" in ref[:40] or ref.endswith("/>"):
            continue
        # Compare normalized (the duplicates often differ only by a "www."
        # prefix or a trailing slash, e.g. Andrés's two ijglobal refs).
        if want in [norm_url(u) for u in URL_RE.findall(ref)]:
            hits.append((m.start(), m.end(), ref))
    if len(hits) < 2:
        raise SystemExit(f"dedupe {label!r}: found {len(hits)} refs citing "
                         f"{url} (need >= 2)")
    named = [h for h in hits if NAME_RE.match(h[2])]
    if len(named) > 1:
        raise SystemExit(f"dedupe {label!r}: {len(named)} of the duplicates "
                         f"are already named -- resolve by hand")
    if named:
        keep = named[0]
        m = NAME_RE.match(keep[2])
        name = next(g for g in m.groups()[1:] if g)
        definition = keep[2]
    else:
        keep = hits[0]
        name = fallback_name
        definition = keep[2].replace("<ref", f'<ref name="{name}"', 1)
    reuse = f'<ref name="{name}" />'
    print(f"\n--- {label}\n  KEEP as name=\"{name}\": {definition[:220]}")
    # Rewrite back-to-front so earlier offsets stay valid.
    for start, end, ref in sorted(hits, key=lambda h: -h[0]):
        repl = definition if (start, end) == (keep[0], keep[1]) else reuse
        if repl != ref:
            print(f"  {ref[:150]}\n    -> {repl}")
        text = text[:start] + repl + text[end:]
    return text


def apply_raw(text, label, old_sub, new_sub, expect, idx):
    n = text.count(old_sub)
    if n != expect:
        raise SystemExit(f"raw count mismatch for {label!r}: "
                         f"found {n}, expected {expect}")
    pos = -1
    for _ in range(idx + 1):
        pos = text.find(old_sub, pos + 1)
    print(f"\n--- {label}\n  OLD: {old_sub[:300]}\n  NEW: {new_sub[:300]}")
    return text[:pos] + new_sub + text[pos + len(old_sub):]


def build_page(s, title, fixes):
    """Apply a page's fixes; write <slug>_old/_new.wiki; return (old, new)."""
    slug = re.sub(r"[ \-()]", "_", title)
    old = gw.page_text(s, title)
    new = old
    skipped = []
    print("=" * 72)
    print(f"PAGE: {title}  ({len(fixes)} fixes)")
    for label, marker, action in fixes:
        if action[0] == "raw":
            new = apply_raw(new, label, action[1], action[2],
                            action[3], action[4])
            continue
        if action[0] == "dedupe":
            new = apply_dedupe(new, label, action[1], action[2])
            continue
        # AUTO passes ("url", u) so the ref is located by exact URL match;
        # MANUAL passes a plain wikitext fragment.
        if isinstance(marker, tuple) and marker[0] == "url":
            ref = find_ref_by_url(new, marker[1])
        else:
            ref = fixlib.find_ref(new, marker)
        if action[0] == "swap":
            _, u_old, u_new = action
            if u_old not in ref:
                raise SystemExit(f"url not in located ref: {label}")
            new_ref = ref.replace(u_old, u_new)
        elif action[0] == "archive":
            new_ref = apply_archive(ref, action[1], action[2])
            if new_ref is None:
                print(f"\n--- {label}\n  SKIP: archive-url already populated")
                skipped.append(label)
                continue
        else:
            new_ref = action[1]
        if new.count(ref) != 1:
            raise SystemExit(f"located ref is not unique in page: {label}")
        new = new.replace(ref, new_ref, 1)
        print(f"\n--- {label}\n  OLD: {ref[:300]}\n  NEW: {new_ref[:300]}")
    with open(f"{slug}_old.wiki", "w") as f:
        f.write(old)
    with open(f"{slug}_new.wiki", "w") as f:
        f.write(new)
    print(f"\n  ({len(fixes) - len(skipped)} applied, {len(skipped)} skipped)")
    return old, new, len(fixes) - len(skipped)


def main():
    save = "--save" in sys.argv
    auto = load_auto()
    plan = {}
    for title, (summary, fixes) in MANUAL.items():
        plan[title] = (summary, list(fixes) + auto.pop(title, []))
    for title, fixes in auto.items():
        plan[title] = ("background: repair dead citations with archived copies",
                       fixes)

    s = gw.session()
    diffs, applied = {}, 0
    for title, (summary, fixes) in sorted(plan.items()):
        old, new, n = build_page(s, title, fixes)
        applied += n
        # A page whose every fix was skipped needs no edit at all.
        if n:
            diffs[title] = (old, new)

    print(f"### {len(diffs)} pages, {applied} fixes staged")
    if not save:
        print("dry run -- rerun with --save to write")
        return

    s = gw.session(login=True)
    saved = {}
    for title in sorted(diffs):
        summary = plan[title][0]
        res = fixlib.guarded_save(s, title, *diffs[title], summary=summary)
        if res:
            saved[title] = res.get("newrevid")
    print("\n### cite-error check")
    for title in sorted(saved):
        print(f"  {fixlib.cite_errors(s, title):>3} errors  {title} "
              f"(rev {saved[title]})")
    print("\nrevisions:", json.dumps(saved, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
