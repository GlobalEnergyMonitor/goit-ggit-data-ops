#!/usr/bin/env python3
"""Follow-up India fixes (2026-07-22): refs missed by the case-sensitive
scanner (capitalized <Ref> tags) + the Dhamra cosmetic bracket fix."""
import fixlib
import gemwiki as gw

OE_KOCHI = ("https://www.offshore-energy.biz/"
            "petronet-lng-to-up-kochi-terminals-utilization-capacity-"
            "to-40-pct-by-2019/")

fixes = {
    "Kochi LNG Terminal": ("repair dead reut.rs shortlink in background citation", [
        ("reut.rs shortlink now redirects to reuters homepage -> "
         "offshore-energy copy of the same reuters piece",
         "reut.rs/2jDMcLc",
         ("full",
          "<ref>[" + OE_KOCHI + " Petronet LNG to up Kochi terminal's "
          "utilization capacity to 40 pct by 2019], Offshore Energy "
          "(citing Reuters), January 11, 2017</ref>")),
    ]),
    "Dhamra LNG Terminal": ("fix malformed external link in background citation", [
        ("add missing opening bracket",
         "adani-breaks-ground-on-dhamra-lng-project",
         ("swap",
          "<ref>https://www.offshore-energy.biz/adani-breaks-ground",
          "<ref>[https://www.offshore-energy.biz/adani-breaks-ground")),
    ]),
}

s = gw.session()
diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}

s = gw.session(login=True)
for t, (summ, fx) in fixes.items():
    fixlib.guarded_save(s, t, *diffs[t], summary=summ)

s = gw.session()
for t in fixes:
    print(f"cite errors {t}: {fixlib.cite_errors(s, t)}")
