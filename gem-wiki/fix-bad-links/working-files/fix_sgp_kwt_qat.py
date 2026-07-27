#!/usr/bin/env python3
"""Fix run: Singapore, Kuwait, Qatar LNG terminal pages (working file).

Usage: python3 fix_sgp_kwt_qat.py [--save]
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
#   ("raw", old_text, new_text, n)  exact string replace, expects n hits,
#                                   replaces occurrence index n_idx (0-based)
# raw is used for dedupes where duplicate refs have identical wikitext.

SIGHTLINE = ('<ref>[http://www.sightline.org/2017/06/07/bcs-carbon-pollution-'
             'could-double-with-lng-plants/ "BC’S Carbon Pollution Could '
             'Double with LNG Plants"] Tarika Powell, Sightline Institute, '
             'June 7, 2017.</ref>')

ORBIT = ('<ref>{{cite web|url=https://www.theorbitdesk.com/notes/lng-strait-'
         'of-hormuz|title=Qatar\'s LNG restart, one train at a time|'
         'publisher=The Orbit Desk|access-date=2026-07-17}}</ref>')

FIXES = {
 "Singapore LNG Terminal": (
  "repair dead background citations (archive/relocated links, giignl standard format)", [
  ("bit.ly operations -> archived slng terminal layout", "bit.ly/2mIBzH4",
   ("swap", "http://bit.ly/2mIBzH4",
    WB + "20160423025450/http://www.slng.com.sg/website/content.aspx?wpi=Terminal+Layout&mmi=85&smi=112")),
  ("dead binarystream press release -> relocated live copy", "binarystream_processor",
   ("swap",
    "https://www.slng.com.sg/website/binarystream_processor.aspx?T=oHrZIePy%2F%2FIsmOw4n0HfkA%3D%3D&C=3nZ502kqfj3GSxT9GjBmJQ%3D%3D&PK=EqN%2FrJJFStw%3D&K=9DD319&SC=1",
    "https://www.slng.com.sg/samsung-ct-corporation-awarded-epc-contract-phase-3-expansion-singapore-lng-terminal")),
  ("lngworldnews fifth tank dead -> archive", "slng-tests-the-market",
   ("swap", "https://www.lngworldnews.com/slng-tests-the-market-demand-for-fifth-lng-storage-tank/",
    WB + "20190916141017/https://www.lngworldnews.com/slng-tests-the-market-demand-for-fifth-lng-storage-tank/")),
  ("malformed giignl 2021 ref -> standard format", "giignl 2021 annual report apr27",
   ("full", fixlib.giignl(fixlib.G2021, 2021))),
 ]),

 "Singapore Offshore LNG Terminal": (
  "repair dead background citations (archive links)", [
  ("ema eoi pdf dead -> archive", "Expression%20of%20Interest",
   ("swap", "https://www.ema.gov.sg/cmsmedia/Expression%20of%20Interest%20for%20OLT_final.pdf",
    WB + "20220119004645/https://www.ema.gov.sg/cmsmedia/Expression%20of%20Interest%20for%20OLT_final.pdf")),
  ("zawya story dead -> archive", "Singapore_drafting_regulatory_framework",
   ("swap", "https://www.zawya.com/mena/en/story/Singapore_drafting_regulatory_framework_for_2nd_LNG_terminal_minister_says-TR20201027nL1N2HI097X1",
    WB + "20201028150155/https://www.zawya.com/mena/en/story/Singapore_drafting_regulatory_framework_for_2nd_LNG_terminal_minister_says-TR20201027nL1N2HI097X1/")),
 ]),

 "Al Zour LNG Terminal": (
  "repair dead background citations (giignl standard format, dedupe)", [
  ("giignl 2022 dead -> standard format", "GIIGNL2022_Annual_Report_May24",
   ("full", fixlib.giignl(fixlib.G2022, 2022, name=":4"))),
  ("dedupe duplicate hydrocarbons-technology named ref", None,
   ("raw",
    '<ref name=s1>[https://www.hydrocarbons-technology.com/projects/al-zour-lng-import-terminal-project/ Al-Zour LNG Import Terminal Project] Hydrocarbons Technology, accessed July 19, 2019</ref>',
    '<ref name=s1/>', 2, 1)),
 ]),

 "Mina Al-Ahmadi LNG Terminal": (
  "repair dead background citations (archive links, giignl standard format, dedupe)", [
  ("igu 2019 report dead -> archive", "IGU%20Annual%20Report%202019",
   ("swap", "https://www.igu.org/sites/default/files/node-news_item-field_file/IGU%20Annual%20Report%202019_23%20loresfinal.pdf",
    WB + "20191215013015/https://www.igu.org/sites/default/files/node-news_item-field_file/IGU%20Annual%20Report%202019_23%20loresfinal.pdf")),
  ("giignl 2022 dead -> standard format", "GIIGNL2022_Annual_Report_May24",
   ("full", fixlib.giignl(fixlib.G2022, 2022, name=":3"))),
  ("hellenic shipping dead -> archive", "qatar-shipping-company-moves-hub",
   ("swap", "http://www.hellenicshippingnews.com/qatar-shipping-company-moves-hub-from-uae-to-oman/",
    WB + "20180215210624/http://www.hellenicshippingnews.com/qatar-shipping-company-moves-hub-from-uae-to-oman/")),
  ("dedupe bare gnlglobal ref -> named reuse", "<ref>https://gnlglobal.com",
   ("full", '<ref name=":4" />')),
  ("dedupe bare linkedin ref -> named reuse", "<ref>https://www.linkedin.com/posts",
   ("full", '<ref name=":2" />')),
 ]),

 "Qatar North Field LNG Terminal": (
  "repair dead background citations (archive links, giignl standard format)", [
  ("giignl 2021 dead -> standard format", "giignl_2021_annual_report_may4",
   ("full", fixlib.giignl(fixlib.G2021, 2021, name="GIIGNL", page=40))),
  ("cnbc dead -> archive", "reuters-america-update-2-qatar-plans",
   ("swap", "https://www.cnbc.com/2019/11/25/reuters-america-update-2-qatar-plans-to-boost-lng-production-to-126-mln-t-by-2027.html",
    WB + "20200211135956/https://www.cnbc.com/2019/11/25/reuters-america-update-2-qatar-plans-to-boost-lng-production-to-126-mln-t-by-2027.html")),
  ("clydeco insight dead -> archive", "qatar-s-north-field-east-lng-liquefaction",
   ("swap", "https://www.clydeco.com/en/insights/2021/03/qatar-s-north-field-east-lng-liquefaction-project",
    WB + "20210513053142/https://www.clydeco.com/en/insights/2021/03/qatar-s-north-field-east-lng-liquefaction-project")),
 ]),

 "QatarEnergy LNG (N)": (
  "repair dead background citations (archive links, giignl standard format, dedupes)", [
  ("qatargas history dead -> relocated successor page", "english/aboutus/history",
   ("full", '<ref name=":1">{{Cite web|url=https://www.qatarenergylng.qa/'
    'english/About-Us/Our-History|title=QatarEnergy LNG - Our History|'
    'website=www.qatarenergylng.qa|language=en-US|'
    'access-date=July 21, 2026}}</ref>')),
  ("qatargas venture portfolio pdf dead -> archive", "Venture%20Portfolio_Final",
   ("swap", "https://www.qatargas.com/english/aboutus/Documents/Venture%20Portfolio_Final.pdf",
    WB + "20230829134547/https://www.qatargas.com/english/aboutus/Documents/Venture%20Portfolio_Final.pdf")),
  ("qatargas corporate structure dead -> archive (1)", "Corporate Gas]",
   ("swap", "https://www.qatargas.com/english/aboutus/corporate-structure",
    WB + "20230829134622/https://www.qatargas.com/english/aboutus/corporate-structure")),
  ("qatargas corporate structure dead -> archive (2)", "Corporate Structure]",
   ("swap", "https://www.qatargas.com/english/aboutus/corporate-structure",
    WB + "20230829134622/https://www.qatargas.com/english/aboutus/corporate-structure")),
  ("qatargas lng-trains dead -> archive (unnamed)", "access-date=2023-06-26}}",
   ("swap", "https://www.qatargas.com/english/operations/lng-trains",
    WB + "20230829134625/https://www.qatargas.com/english/operations/lng-trains")),
  ("qatargas lng-trains dead -> archive (:02)", ':02">{{Cite web|url=https://www.qatargas.com',
   ("swap", "https://www.qatargas.com/english/operations/lng-trains",
    WB + "20230829134625/https://www.qatargas.com/english/operations/lng-trains")),
  ("qatargas lng-trains dead -> archive (:04)", ':04">{{Cite web|url=https://www.qatargas.com',
   ("swap", "https://www.qatargas.com/english/operations/lng-trains",
    WB + "20230829134625/https://www.qatargas.com/english/operations/lng-trains")),
  ("mechademy dead -> archive", "mechademy.com/lng_plant",
   ("swap", "https://www.mechademy.com/lng_plant/qatargas-2-trains-4-5/",
    WB + "20230307103850/https://www.mechademy.com/lng_plant/qatargas-2-trains-4-5/")),
  ("agsiw dead -> archive", "qatar-moves-ensure-lng-dominance",
   ("swap", "http://www.agsiw.org/qatar-moves-ensure-lng-dominance/",
    WB + "20250215170326/http://www.agsiw.org/qatar-moves-ensure-lng-dominance/")),
  ("giignl 2023 dead -> standard format", "GIIGNL_2023_Annual_Report_July14",
   ("full", fixlib.giignl(fixlib.G2023, 2023))),
  ("dedupe business times ref (2)", 'name="business2"',
   ("full", '<ref name="business" />')),
  ("dedupe business times ref (3)", 'name="business3"',
   ("full", '<ref name="business" />')),
  ("dedupe business times ref (4)", 'name="business4"',
   ("full", '<ref name="business" />')),
  ("dedupe reuters splitter ref def", 'name="ReutersStaff3">',
   ("full", '<ref name="ReutersStaff" />')),
  ("dedupe reuters splitter ref reuse", '<ref name="ReutersStaff3" />',
   ("full", '<ref name="ReutersStaff" />')),
  ("dedupe sightline ref (name first)", None,
   ("raw", SIGHTLINE,
    SIGHTLINE.replace("<ref>", '<ref name="sightline">'), 2, 0)),
  ("dedupe sightline ref (reuse second)", None,
   ("raw", SIGHTLINE, '<ref name="sightline" />', 1, 0)),
  ("dedupe orbitdesk ref (name first)", None,
   ("raw", ORBIT, ORBIT.replace("<ref>", '<ref name="orbitdesk">'), 2, 0)),
  ("dedupe orbitdesk ref (reuse second)", None,
   ("raw", ORBIT, '<ref name="orbitdesk" />', 1, 0)),
 ]),

 "QatarEnergy LNG (S)": (
  "dedupe duplicate qatarenergylng citation", [
  ("dedupe lng-trains template -> named reuse", "access-date=2025-07-15",
   ("full", '<ref name=":1" />')),
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
