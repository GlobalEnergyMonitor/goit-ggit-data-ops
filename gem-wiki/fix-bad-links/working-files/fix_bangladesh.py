#!/usr/bin/env python3
"""Bangladesh background-citation fixes (working file, not committed)."""
import re

import fixlib
import gemwiki as gw

WB = "https://web.archive.org/web/"
BPOST = "http://www.thebangladeshpost.com/national/6650/pdf"
BPOST_WB = WB + "20180804062446/http://www.thebangladeshpost.com:80/national/6650/pdf"
NEWAGE_UTM = ("https://www.newagebd.net/article/204196/bangladesh-approves-one-more-lng-terminal"
              "?utm_medium=email&_hsmi=262789059&_hsenc=p2ANqtz--KRcCSpHQrBVU_sdVKyHf0P5ImlEX0Ej"
              "_rvTy1fiFYaYlX4iaXrVntpfCwJERUTytHBfENuDRELFWQMBahPp6-b0SB1EzPN4Uwe0CJ2dMphvahgTg"
              "&utm_content=262789059&utm_source=hs_email")

fixes = {
    "ACWA LNG Terminal": ("fix dead background ref: swap acwapower link to archived copy", [
        ("acwapower dead -> archive", "acwa-power-inks-mou",
         ("swap", "https://www.acwapower.com/news/acwa-power-inks-mou-for-3600mw-gas-plant-in-bangladesh/#",
          WB + "20230809154254/https://www.acwapower.com/news/acwa-power-inks-mou-for-3600mw-gas-plant-in-bangladesh/")),
    ]),
    "Kutubdia (Reliance) FSRU": ("fix background ref: bit.ly shortlink to archived platts article", [
        ("bit.ly -> archived platts original", "bit.ly/2lHPSOJ Moheshkhali",
         ("swap", "http://bit.ly/2lHPSOJ",
          WB + "20161212012944/http://www.platts.com:80/latest-news/natural-gas/dhaka/bangladesh-to-award-lng-terminal-project-to-reliance-27725340")),
    ]),
    "Kutubdia LNG Terminal (Petronet)": ("fix background refs: archive swap for dead bangladesh post link; tidy empty named ref", [
        ("bangladesh post dead -> archive", "thebangladeshpost.com/national/6650",
         ("swap", BPOST, BPOST_WB)),
        ("empty named ref -> self-closing reuse", "name=et></ref>",
         ("full", "<ref name=et />")),
    ]),
    "Matarbari GE LNG Terminal": ("fix background refs: archive swaps for dead links; dedupe daily star ref", [
        ("energycentral soft404 -> archive", "energycentral.com/news/mou-signed",
         ("swap", "https://energycentral.com/news/mou-signed-bangladeshs-largest-lng-based-power-plant",
          WB + "20211022072748/https://energycentral.com/news/mou-signed-bangladeshs-largest-lng-based-power-plant")),
        ("cpgcbl eoi pdf dead -> archive", "Final-FAS-EOI-Notice-r4.pdf",
         ("swap", "https://cpgcbl.portal.gov.bd/sites/default/files/files/cpgcbl.portal.gov.bd/page/9c33abb5_e666_4a96_95b9_1e1a80f6720b/Final-FAS-EOI-Notice-r4.pdf",
          WB + "20210623142931/https://cpgcbl.portal.gov.bd/sites/default/files/files/cpgcbl.portal.gov.bd/page/9c33abb5_e666_4a96_95b9_1e1a80f6720b/Final-FAS-EOI-Notice-r4.pdf")),
    ]),
    "Matarbari LNG Terminal": ("fix background ref: remove bogus author field in risingbd citation", [
        ("risingbd bogus last= field", "risingbd",
         ("swap", "|last=https://www.risingbd.com", "")),
    ]),
    "Moheshkhali Floating LNG Terminal": ("fix background refs: archive swap for dead bangladesh post link; standardize giignl 2021 ref", [
        ("bangladesh post dead -> archive", "thebangladeshpost.com/national/6650",
         ("swap", BPOST, BPOST_WB)),
        ("giignl 2021 -> standard format", "giignl_2021_annual_report_apr27",
         ("full", fixlib.giignl(fixlib.G2021, 2021, name=":2", accessed="July 22, 2026"))),
    ]),
    "Payra FSRU": ("fix background refs: archive swaps for dead financial express and observer links", [
        ("financial express soft404 -> archive", "title=Growing lobbying",
         ("swap", "https://thefinancialexpress.com.bd/public/trade/growing-lobbying-prompts-authorities-to-decide-to-conduct-study-on-fsru-at-payra-1631759768",
          WB + "20211020220654/https://www.thefinancialexpress.com.bd/public/trade/growing-lobbying-prompts-authorities-to-decide-to-conduct-study-on-fsru-at-payra-1631759768")),
        ("observerbd article gone -> archive", "title=Petrobangla plans to set up 3 more",
         ("swap", "https://www.observerbd.com/news.php?id=456940",
          WB + "20240420035100/https://www.observerbd.com/news.php?id=456940")),
    ]),
    "Summit FSRU": ("fix background refs: bit.ly to original daily star url; archive swap for broken zawya link", [
        ("bit.ly -> live daily star original", "bit.ly/2lHIpPk",
         ("swap", "http://bit.ly/2lHIpPk",
          "https://www.thedailystar.net/business/summit-signs-deal-build-500m-lng-terminal-1340404")),
        ("zawya broken -> archive", "bangladeshs-summit-lng-says-fsru-operations-paused",
         ("swap", "https://www.zawya.com/en/world/indian-sub-continent/bangladeshs-summit-lng-says-fsru-operations-paused-due-to-cyclone-damage-nj4uz082",
          WB + "20260418195023/https://www.zawya.com/en/world/indian-sub-continent/bangladeshs-summit-lng-says-fsru-operations-paused-due-to-cyclone-damage-nj4uz082")),
    ]),
    "Summit Matarbari FSRU": ("fix background refs: archive swap for daily sun link; strip tracking params from new age url", [
        ("daily-sun defunct print page -> archive", "title=Summit proposes new LNG terminal",
         ("swap", "https://www.daily-sun.com/printversion/details/582658/Summit-proposes-new-LNG-terminal-at-Matarbari-",
          WB + "20211208195710/https://www.daily-sun.com/printversion/details/582658/Summit-proposes-new-LNG-terminal-at-Matarbari-")),
        ("new age strip tracking params", "newagebd.net/article/204196",
         ("swap", NEWAGE_UTM,
          "https://www.newagebd.net/article/204196/bangladesh-approves-one-more-lng-terminal")),
    ]),
}

s = gw.session()
diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}

# Matarbari GE: two byte-identical <ref name=":0"> definitions -> make the
# second a self-closing reuse (fixlib can't target non-unique ref text).
t = "Matarbari GE LNG Terminal"
old, new = diffs[t]
m = re.search(r'<ref name=":0">\{\{Cite news\|url=[^<]*74b-deals[^<]*\}\}</ref>', new)
assert m, "daily star :0 ref not found"
ref = m.group(0)
first = new.find(ref)
second = new.find(ref, first + 1)
assert second > 0, "second :0 definition not found"
assert new.find(ref, second + 1) == -1, "more than two :0 definitions"
new = new[:second] + '<ref name=":0" />' + new[second + len(ref):]
print(f"\n--- dedupe daily star :0 (second definition -> reuse) on {t}")
with open("Matarbari_GE_LNG_Terminal_new.wiki", "w") as f:
    f.write(new)
diffs[t] = (old, new)

print("\n" + "=" * 70 + "\nSAVING\n")
s = gw.session(login=True)
for t, (summ, fx) in fixes.items():
    fixlib.guarded_save(s, t, *diffs[t], summary=summ)

print("\ncite error check:")
for t in fixes:
    print(f"  {fixlib.cite_errors(s, t)}  {t}")
