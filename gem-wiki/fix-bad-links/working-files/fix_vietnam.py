#!/usr/bin/env python3
"""Fix run: Vietnam LNG terminal pages (working file).

Usage: python3 fix_vietnam.py [--save]
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

JCCP_OLD = "http://www.jccp.or.jp/country/docs/4_CPJ-5-18_MOIT.pdf"
JCCP_NEW = WB + "20220119223434/http://www.jccp.or.jp/country/docs/4_CPJ-5-18_MOIT.pdf"

EI_OLD = "https://www.energyintel.com/00000188-9e31-dfa7-aded-9ffb3ab90000"
EI_NEW = WB + "20250723145420/https://www.energyintel.com/00000188-9e31-dfa7-aded-9ffb3ab90000"

FIXES = {
 "Bac Lieu LNG Terminal": (
  "repair malformed giignl 2021 background citation (standard format)", [
  ("malformed giignl 2021 ref -> standard format",
   "giignl 2021 annual report apr27",
   ("full", fixlib.giignl(fixlib.G2021, 2021))),
 ]),

 "Cai Mep LNG Terminal": (
  "repair dead background citation (archive link)", [
  ("ustda press release dead -> archive", "ustda-supports-historic",
   ("swap", "https://ustda.gov/news/press-releases/2019/ustda-supports-historic-lng-development-vietnam",
    WB + "20191210042622/https://ustda.gov/news/press-releases/2019/ustda-supports-historic-lng-development-vietnam")),
 ]),

 "Cat Hai FSRU": (
  "repair dead background citations (archive links)", [
  ("exxonmobil lng page dead -> archive",
   "integrated-lng-to-power-project-in-vietnam",
   ("swap", "https://www.exxonmobillng.com/en/about-us/trending-topics/integrated-lng-to-power-project-in-vietnam",
    WB + "20250424012551/https://www.exxonmobillng.com/en/about-us/trending-topics/integrated-lng-to-power-project-in-vietnam")),
  ("energyintel article js-walled -> archive", "energyintel.com/00000188",
   ("swap", EI_OLD, EI_NEW)),
 ]),

 "Son My LNG Terminal": (
  "repair dead background citations (archive links, relocated source, dedupe)", [
  ("usembassy fact sheet dead -> archive", "fact-sheet-2019-indo-pacific",
   ("swap", "https://vn.usembassy.gov/fact-sheet-2019-indo-pacific-business-forum-showcases-high-standard-u-s-investment/",
    WB + "20230605231503/https://vn.usembassy.gov/fact-sheet-2019-indo-pacific-business-forum-showcases-high-standard-u-s-investment/")),
  ("powerengineeringint dead -> archived relocated copy",
   "edf-to-build-new-gas-fired",
   ("swap", "http://www.powerengineeringint.com/articles/2018/03/edf-to-build-new-gas-fired-power-plant-in-vietnam.html",
    WB + "20210727205750/https://www.powerengineeringint.com/gas-oil-fired/edf-to-build-new-gas-fired-power-plant-in-vietnam/")),
  ("dredgingandports drifted -> archive", "dredgingandports.com/news/2019",
   ("swap", "https://dredgingandports.com/news/2019/vietnam-builds-first-lng-terminal/",
    WB + "20191230191235/https://dredgingandports.com/news/2019/vietnam-builds-first-lng-terminal/")),
  ("bnews conn-dead -> archive", "bnews.vn/pv-gas",
   ("swap", "https://bnews.vn/pv-gas-va-tap-doan-aes-cong-bo-nhan-su-cong-ty-tnhh-kho-cang-lng-son-my/242059.html",
    WB + "20260716064417/https://bnews.vn/pv-gas-va-tap-doan-aes-cong-bo-nhan-su-cong-ty-tnhh-kho-cang-lng-son-my/242059.html")),
  ("hanoitimes conn-dead -> archive", "aes-petrovietnam-set-up-joint-venture",
   ("swap", "http://hanoitimes.vn/aes-petrovietnam-set-up-joint-venture-for-us14-billion-lng-terminal-314645.html",
    WB + "20211130084118/http://hanoitimes.vn/aes-petrovietnam-set-up-joint-venture-for-us14-billion-lng-terminal-314645.html")),
  ("dedupe duplicate marketscreener template ref -> named reuse",
   "website=MarketScreener",
   ("full", '<ref name="yr" />')),
 ]),

 "South East LNG Terminal": (
  "repair dead background citation (archive link)", [
  ("jccp gas master plan pdf dead -> archive", "4_CPJ-5-18_MOIT.pdf",
   ("swap", JCCP_OLD, JCCP_NEW)),
 ]),

 "South West FSRU": (
  "repair dead background citation (archive link)", [
  ("jccp gas master plan pdf dead -> archive", "4_CPJ-5-18_MOIT.pdf",
   ("swap", JCCP_OLD, JCCP_NEW)),
 ]),

 "Tien Giang LNG Terminal": (
  "repair dead background citation (archive link)", [
  ("jccp gas master plan pdf dead -> archive", "4_CPJ-5-18_MOIT.pdf",
   ("swap", JCCP_OLD, JCCP_NEW)),
 ]),

 "Thai Binh FSRU": (
  "repair dead background citation (replacement source), dedupe", [
  ("marinecurrents dead with no archive -> ttvn group article",
   "thai-binh-lng-power-plant-vietnam-proposal",
   ("full", '<ref name=":0">{{Cite web|url=https://ttvngroup.vn/en/'
    'appraisal-of-4500-mw-thai-binh-lng-power-centre/|title=Appraisal of '
    '4,500 MW Thai Binh LNG Power Centre|website=Truong Thanh Viet Nam '
    'Group|access-date=July 21, 2026}}</ref>')),
  ("dedupe duplicate kyuden template ref -> named reuse",
   "website=www.kyuden-intl.co.jp",
   ("full", '<ref name=":2" />')),
 ]),

 "Nghi Son LNG Terminal": (
  "dedupe duplicate vietnamnews citation", [
  ("dedupe vietnamnews template ref -> named reuse",
   "vietnamnews.vn|access-date=2026-07-09",
   ("full", '<ref name=":1" />')),
 ]),

 "Thi Vai LNG Terminal": (
  "repair dead background citations (giignl standard format)", [
  ("malformed giignl 2021 ref -> standard format",
   "giignl 2021 annual report apr27",
   ("full", fixlib.giignl(fixlib.G2021, 2021))),
  ("giignl 2024 dead -> standard format", "GIIGNL-2024-Annual-Report-1",
   ("full", fixlib.giignl(fixlib.G2024, 2024, name=":2"))),
 ]),

 "Tien Lang FSRU": (
  "repair dead background citations (archive links)", [
  ("marinecurrents drifted -> archive", "two-hai-phong-lng-to-power-projects",
   ("swap", "https://www.marinecurrents.com/two-hai-phong-lng-to-power-projects-ensure-clean-energy-resource-for-vietnam/",
    WB + "20221005115805/https://www.marinecurrents.com/two-hai-phong-lng-to-power-projects-ensure-clean-energy-resource-for-vietnam/")),
  ("energyintel article js-walled -> archive", "energyintel.com/00000188",
   ("swap", EI_OLD, EI_NEW)),
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
