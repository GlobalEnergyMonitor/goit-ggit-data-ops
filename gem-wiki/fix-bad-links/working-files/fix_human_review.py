#!/usr/bin/env python3
"""Repairs from the 2026-07-23 human review of HUMAN-REVIEW.md (user-verified
replacement URLs)."""
import fixlib
import gemwiki as gw

ARGUS_AMNS = ("https://www.argusmedia.com/en/news-and-insights/latest-market-"
              "news/2639678-india-s-amns-in-talks-to-build-suvali-lng-terminal")
ARGUS_AMNS_WB = "https://web.archive.org/web/20241220194128/" + ARGUS_AMNS
ARGUS_LOCKDOWN = ("https://www.argusmedia.com/zh/news-and-insights/latest-"
                  "market-news/2095601-indian-states-extend-lockdowns-"
                  "slashing-fuel-demand")
NGW = ("https://www.naturalgasworld.com/"
       "bangladesh-scraps-reliance-power-fsru-proceeds-with-65287")
SPG_SPOILT = ("https://www.spglobal.com/energy/en/news-research/latest-news/"
              "natural-gas/022120-india-lng-buyers-spoilt-for-choice-as-china-"
              "woes-create-problem-of-plenty")

amns_swap = ("argus amns url dead for humans too -> dec 2024 snapshot",
             "2639678", ("swap", ARGUS_AMNS, ARGUS_AMNS_WB))

fixes = {
    "Dabhol LNG Terminal": ("swap dead argus url for archived copy", [amns_swap]),
    "Hazira LNG Terminal": ("swap dead argus url for archived copy", [amns_swap]),
    "Dhamra LNG Terminal": ("replace dead argus covid article with live equivalent", [
        ("argus odisha-lockdown dead, no archive -> live argus equivalent",
         "2095088",
         ("full",
          "<ref>[" + ARGUS_LOCKDOWN + " Indian states extend lockdowns, "
          "slashing fuel demand], Argus Media, April 2020</ref>")),
    ]),
    "Kutubdia (Reliance) FSRU": ("replace dead s&p platts url with natural gas world copy", [
        ("spglobal reliance-terminates dead for humans -> natural gas world",
         "101918-bangladesh-terminates",
         ("full",
          '<ref name=spg1>[' + NGW + ' "Bangladesh Scraps Reliance FSRU,"] '
          "Natural Gas World, October 18, 2018.</ref>")),
    ]),
    "Jaigarh LNG Terminal": ("replace dead hellenic copy with s&p global original", [
        ("hellenic dead -> s&p global original",
         "india-lng-buyers-spoilt",
         ("full",
          '<ref name="cap">[' + SPG_SPOILT + " India LNG buyers spoilt for "
          "choice as China woes create problem of plenty] S&P Global Platts, "
          "February 21, 2020</ref>")),
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
