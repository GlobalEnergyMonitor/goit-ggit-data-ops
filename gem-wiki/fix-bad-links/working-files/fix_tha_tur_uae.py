#!/usr/bin/env python3
"""Fix run: Thailand, Turkiye, UAE LNG terminal pages (working file).

Usage: python3 fix_tha_tur_uae.py [--save]
Without --save: builds diffs only (writes *_old.wiki / *_new.wiki).
"""
import re
import sys

import fixlib
import gemwiki as gw

WB = "https://web.archive.org/web/"

# ---------------------------------------------------------------- fixes ---
# action types:
#   ("swap", old_url, new_url)      via fixlib
#   ("full", new_ref_text)          via fixlib
#   ("raw", old_text, new_text, n, n_idx)  exact string replace, expects n
#                                   hits, replaces occurrence n_idx (0-based)
# raw is used for dedupes where duplicate refs have identical wikitext.

IGU_OLD = ("http://www.igu.org/sites/default/files/node-document-field_file/"
           "103419-World_IGU_Report_FINAL_LR.PDF")
IGU_NEW = (WB + "20191028040840/https://www.igu.org/sites/default/files/"
           "node-document-field_file/103419-World_IGU_Report_FINAL_LR.PDF")

MARINELINK = ('<ref name="delay">[https://www.marinelink.com/news/'
              'fujairah-terminal-dhabi409224 Abu Dhabi Puts Fujairah LNG '
              'Terminal On Hold] Maritime Link, May 5, 2016.</ref>')

GIIGNL2026 = ("https://files.elfsightcdn.com/eafe4a4d-3436-495d-b748-"
              "5bdce62d911d/ee1bebf9-7dfc-4c6a-8134-b8214c8302a0/"
              "GIIGNL-2026-Annual-Report-0521.pdf")

FIXES = {
 # ------------------------------------------------------------- thailand --
 "Map Ta Phut LNG Terminal 1": (
  "repair dead background citations (archive links, giignl standard format)", [
  ("pttlng composition dead -> archive", "pj_composition",
   ("swap", "http://www.pttlng.com/en/pj_composition.aspx",
    WB + "20171031022834/http://www.pttlng.com/en/pj_composition.aspx")),
  ("pttlng milestones dead -> archive", "pj_mile",
   ("swap", "http://www.pttlng.com/en/pj_mile.aspx",
    WB + "20171105162738/http://www.pttlng.com/en/pj_mile.aspx")),
  ("malformed giignl 2021 ref -> standard format",
   "giignl 2021 annual report apr27",
   ("full", fixlib.giignl(fixlib.G2021, 2021))),
 ]),

 "Map Ta Phut LNG Terminal 2": (
  "repair dead background citations (archive link, giignl standard format)", [
  ("lngworldnews second terminal dead -> archive",
   "ptt-upping-lng-import-capacity",
   ("swap",
    "http://www.lngworldnews.com/ptt-upping-lng-import-capacity-second-import-terminal-approved/",
    WB + "20190517003942/https://www.lngworldnews.com/ptt-upping-lng-import-capacity-second-import-terminal-approved/")),
  ("malformed giignl 2021 ref -> standard format",
   "giignl 2021 annual report apr27",
   ("full", fixlib.giignl(fixlib.G2021, 2021))),
 ]),

 # -------------------------------------------------------------- turkiye --
 "Etki FSRU": (
  "repair dead background citations (archive links, giignl standard format)", [
  ("bit.ly lngworldnews inauguration dead -> archived original", "bit.ly/2nQQRds",
   ("swap", "http://bit.ly/2nQQRds",
    WB + "20161224143256/http://www.lngworldnews.com/engie-turkeys-first-fsru-inaugurated/")),
  ("bit.ly etkiliman news dead -> archived original", "bit.ly/2wghekf",
   ("swap", "http://bit.ly/2wghekf",
    WB + "20170704194350/http://www.etkiliman.com.tr/EN/news/Turkey-inaugurates-its-first-FSRU-at-Aliaga.html")),
  ("giignl 2022 dead -> standard format", "GIIGNL2022_Annual_Report_May24",
   ("full", fixlib.giignl(fixlib.G2022, 2022, name=":0"))),
  ("etkiliman fsru page dead -> archive", "en/FSRU/FSRU.html",
   ("swap", "http://www.etkiliman.com.tr/en/FSRU/FSRU.html",
    WB + "20241214214632/http://etkiliman.com.tr/en/FSRU/FSRU.html")),
 ]),

 "Izmir Aliaga LNG Terminal": (
  "repair dead background citation (archive link)", [
  ("bit.ly egegaz terminal dead -> archived original", "bit.ly/2xvfCBI",
   ("swap", "http://bit.ly/2xvfCBI",
    WB + "20160507215725/http://www.egegaz.com.tr/en/terminal.aspx")),
 ]),

 "Dörtyol FSRU": (
  "repair bare-domain background citations (full sources, giignl standard format)", [
  ("bare turkiyetoday domain -> full article citation", "turkiyetoday.com",
   ("full", '<ref>[https://www.turkiyetoday.com/business/turkiye-plans-new-'
    'fsru-deployment-at-dortyol-terminal-minister-3213860 Türkiye plans new '
    'FSRU deployment at Dortyol Terminal], Türkiye Today, February 1, 2026. '
    'Accessed July 21, 2026.</ref>')),
  ("bare ceenergynews domain -> giignl news article", "ceenergynews.com",
   ("full", '<ref>GIIGNL. [https://www.giignl.org/news/egypt-scales-up-regas-'
    'capacity-with-fsru-deployments-from-botas-sefe-and-hoegh-lng Egypt '
    'Scales Up Regas Capacity with FSRU Deployments from BOTAŞ, SEFE, and '
    'Höegh LNG], July 2, 2025. Accessed July 21, 2026.</ref>')),
  ("bare elfsightcdn giignl 2026 pdf -> standard format", "elfsightcdn.com",
   ("full", fixlib.giignl(GIIGNL2026, 2026))),
 ]),

 # ------------------------------------------------------------------ uae --
 "Das Island LNG Terminal": (
  "repair dead background citations (archive links)", [
  ("lngworldnews adgas maintenance dead -> archive",
   "adgas-to-shut-down-two-lng-trains",
   ("swap",
    "https://www.lngworldnews.com/adgas-to-shut-down-two-lng-trains-for-scheduled-maintenance/",
    WB + "20171121232403/http://www.lngworldnews.com/adgas-to-shut-down-two-lng-trains-for-scheduled-maintenance/")),
  ("igu 2017 world lng report dead -> archive", "103419-World_IGU_Report",
   ("swap", IGU_OLD, IGU_NEW)),
 ]),

 "Fujairah LNG Terminal": (
  "repair dead background citations (archive links, dedupe)", [
  ("dedupe duplicate marinelink named ref", None,
   ("raw", MARINELINK, '<ref name="delay" />', 2, 1)),
  ("platts ship-to-ship drifted -> archive",
   "port-of-fujairah-plans-lng-ship-to-ship",
   ("swap",
    "https://www.platts.com/latest-news/shipping/singapore/port-of-fujairah-plans-lng-ship-to-ship-transfers-27832334",
    WB + "20170629114543/https://www.platts.com/latest-news/shipping/singapore/port-of-fujairah-plans-lng-ship-to-ship-transfers-27832334")),
  ("igu 2017 world lng report dead -> archive", "103419-World_IGU_Report",
   ("swap", IGU_OLD, IGU_NEW)),
 ]),

 "Jebel Ali FLNG Terminal": (
  "repair dead background citations (archive links, dedupes)", [
  ("dedupe aljazeera template ref -> named reuse", "title=The energy factor",
   ("full", '<ref name=Susan />')),
  ("dedupe igu template ref -> named reuse", "title=2017 World LNG Report",
   ("full", '<ref name=igu />')),
  ("igu 2017 world lng report dead -> archive", "103419-World_IGU_Report",
   ("swap", IGU_OLD, IGU_NEW)),
  ("hellenic shipping dead -> archive", "qatar-shipping-company-moves-hub",
   ("swap", "http://www.hellenicshippingnews.com/qatar-shipping-company-moves-hub-from-uae-to-oman/",
    WB + "20180215210624/http://www.hellenicshippingnews.com/qatar-shipping-company-moves-hub-from-uae-to-oman/")),
 ]),

 "Ruwais FSRU": (
  "repair dead background citations (archive links, giignl standard format)", [
  ("bit.ly lngworldnews dead -> archived original", "bit.ly/2oNLI6f",
   ("full", '<ref>[' + WB + '20160623144718/http://www.lngworldnews.com/'
    'report-uae-plans-another-lng-fsru/ Report: UAE plans another LNG FSRU,] '
    'LNG World News, February 5, 2016. Accessed July 21, 2026.</ref>')),
  ("igu 2017 world lng report dead -> archive", "103419-World_IGU_Report",
   ("swap", IGU_OLD, IGU_NEW)),
  ("giignl 2023 dead -> standard format", "GIIGNL_2023_Annual_Report_July14",
   ("full", fixlib.giignl(fixlib.G2023, 2023))),
 ]),

 "Ruwais LNG Terminal": (
  "repair dead background citations (archive links, relocated source)", [
  ("wam hoa article drifted -> archive with real title", "b31snxc",
   ("full", '<ref name=":4">{{Cite web|url=' + WB + '20240508114638/'
    'https://www.wam.ae/en/article/b31snxc-adnoc-signs-third-long-term-heads-'
    'agreement-for|title=ADNOC signs third long-term Heads of Agreement for '
    'Ruwais LNG project|website=www.wam.ae|access-date=July 21, 2026}}</ref>')),
  ("sefe press release dead -> archive", "sefe-signs-a-long-term",
   ("swap",
    "https://www.sefe-group.com/en/newsroom/press-releases/sefe-signs-a-long-term-heads-of-agreement-with-adnoc-to-buy-1-million-tonnes-per-annum-of-lng",
    WB + "20240318130654/https://www.sefe-group.com/en/newsroom/press-releases/sefe-signs-a-long-term-heads-of-agreement-with-adnoc-to-buy-1-million-tonnes-per-annum-of-lng")),
  ("enterprise.news homepage ref -> nmdc epc press release", "enterprise.news",
   ("full", '<ref name=":9">{{Cite web|url=https://www.nmdc-group.com/en/'
    'media/press-releases/nmdc-energy-formerly-npcc-technip-energies-and-jgc-'
    'awarded-a-major-contract-worth-us-5-5-billion-for-adnoc-s-ruwais-lng-'
    'project-in-the-uae/|title=NMDC Energy (formerly NPCC), Technip Energies, '
    'and JGC awarded a major contract worth US$5.5 billion for ADNOC’s '
    'Ruwais LNG project in the UAE|website=NMDC Group|date=June 13, 2024|'
    'access-date=July 21, 2026}}</ref>')),
 ]),

 "Sharjah FSRU": (
  "repair dead background citations (replacement sources, no archive of original)", [
  ("zawya def dead with no archive -> the national 2017 article",
   "Sharjah_takes_full_ownership",
   ("full", '<ref name=delay>[https://www.thenationalnews.com/business/'
    'energy/sharjah-national-oil-corporation-unveils-plans-to-tackle-gas-'
    'shortages-1.675759 Sharjah National Oil Corporation unveils plans to '
    'tackle gas shortages], The National, November 14, 2017. Accessed '
    'July 21, 2026.</ref>')),
  ("2019 reuse of zawya ref -> meed 2019 article", None,
   ("raw", '<ref name=delay/>',
    '<ref>[https://www.meed.com/sharjah-energy-firm-lng-project/ Sharjah '
    'energy firm moves ahead with LNG project], MEED, June 24, 2019. '
    'Accessed July 21, 2026.</ref>', 1, 0)),
 ]),
}


def apply_raw(new, label, old_sub, new_sub, expect, idx):
    n = new.count(old_sub)
    if n != expect:
        raise SystemExit(f"raw count mismatch ({n} != {expect}): {label}")
    parts = new.split(old_sub)
    # rejoin, replacing only occurrence idx
    out = parts[0]
    for i in range(1, len(parts)):
        out += (new_sub if i - 1 == idx else old_sub) + parts[i]
    print(f"\n--- {label}\n  OLD: {old_sub[:200]}\n  NEW: {new_sub[:200]}")
    return out


def build_page(s, title, fixes):
    slug = re.sub(r"[ \-()]", "_", title)
    old = gw.page_text(s, title)
    new = old
    print("=" * 70)
    print(f"PAGE: {title}  ({len(fixes)} fixes)")
    for fix in fixes:
        label, marker, action = fix
        if action[0] == "raw":
            _, old_sub, new_sub, expect, idx = action
            new = apply_raw(new, label, old_sub, new_sub, expect, idx)
            continue
        ref = fixlib.find_ref(new, marker)
        if action[0] == "swap":
            _, u_old, u_new = action
            if u_old not in ref:
                raise SystemExit(f"url not in ref: {label}")
            new_ref = ref.replace(u_old, u_new)
        else:
            new_ref = action[1]
        if new.count(ref) != 1:
            raise SystemExit(f"ref text not unique in page: {label}")
        new = new.replace(ref, new_ref, 1)
        print(f"\n--- {label}\n  OLD: {ref[:300]}\n  NEW: {new_ref[:300]}")
    with open(f"{slug}_old.wiki", "w") as f:
        f.write(old)
    with open(f"{slug}_new.wiki", "w") as f:
        f.write(new)
    print()
    return old, new


def main():
    save = "--save" in sys.argv
    s = gw.session()
    diffs = {}
    for title, (summ, fx) in FIXES.items():
        diffs[title] = build_page(s, title, fx)
    if not save:
        print("dry run complete (no --save)")
        return
    s = gw.session(login=True)
    for title, (summ, fx) in FIXES.items():
        fixlib.guarded_save(s, title, *diffs[title], summary=summ)
    for title in FIXES:
        n = fixlib.cite_errors(s, title)
        print(f"cite errors {title}: {n}")


if __name__ == "__main__":
    main()
