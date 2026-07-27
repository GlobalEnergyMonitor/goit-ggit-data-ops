#!/usr/bin/env python3
"""Verify planned Vietnam snapshots/replacements before building fixes."""
import json
import time

import requests

HDRS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
WB = "https://web.archive.org/web/"
CDX = "https://web.archive.org/cdx/search/cdx"

CHECKS = [
    ("jccp moit pdf", WB + "20251017004550/http://www.jccp.or.jp/country/docs/4_CPJ-5-18_MOIT.pdf",
     ["%PDF"]),
    ("ustda cai mep", WB + "20191210042622/https://ustda.gov/news/press-releases/2019/ustda-supports-historic-lng-development-vietnam",
     ["lng", "vietnam"]),
    ("exxonmobil cat hai", WB + "20250424012551/https://www.exxonmobillng.com/en/about-us/trending-topics/integrated-lng-to-power-project-in-vietnam",
     ["hai phong", "lng"]),
    ("usembassy son my", WB + "20230605231503/https://vn.usembassy.gov/fact-sheet-2019-indo-pacific-business-forum-showcases-high-standard-u-s-investment/",
     ["son my"]),
    ("dredgingandports son my", WB + "20191230191235/https://dredgingandports.com/news/2019/vietnam-builds-first-lng-terminal/",
     ["lng", "vietnam"]),
    ("bnews son my", WB + "20260716064417/https://bnews.vn/pv-gas-va-tap-doan-aes-cong-bo-nhan-su-cong-ty-tnhh-kho-cang-lng-son-my/242059.html",
     ["aes", "lng"]),
    ("vneconomy quynh lap", WB + "20260715235054/https://en.vneconomy.vn/construction-begins-on-22-bln-quynh-lap-lng-power-plant.htm",
     ["quynh lap"]),
    ("energyintel wayback", "http://web.archive.org/web/20250723145420/https://www.energyintel.com/00000188-9e31-dfa7-aded-9ffb3ab90000",
     ["hai phong"]),
]

LIVE = [
    ("energyintel live", "https://www.energyintel.com/00000188-9e31-dfa7-aded-9ffb3ab90000",
     ["hai phong", "tien lang"]),
    ("marinecurrents thai binh live", "https://www.marinecurrents.com/thai-binh-lng-power-plant-vietnam-proposal/",
     ["thai binh"]),
    ("marinecurrents hai phong live", "https://www.marinecurrents.com/two-hai-phong-lng-to-power-projects-ensure-clean-energy-resource-for-vietnam/",
     ["hai phong"]),
]

CDXQ = [
    ("powerengineeringint edf", "powerengineeringint.com/articles/2018/03/edf-to-build-new-gas-fired-power-plant-in-vietnam.html"),
    ("hanoitimes aes jv", "hanoitimes.vn/aes-petrovietnam-set-up-joint-venture-for-us14-billion-lng-terminal-314645.html"),
    ("vneconomy vung ang iii", "en.vneconomy.vn/ha-tinh-approves-2bln-vung-ang-iii-lng-power-plant-project.htm"),
    ("vneconomy bgrimm", "en.vneconomy.vn/pv-power-and-bgrimm-sign-agreement-for-2bln-lng-power-project-in-ha-tinh-province.htm"),
    ("marinecurrents thai binh", "marinecurrents.com/thai-binh-lng-power-plant-vietnam-proposal/"),
]


def grab(url, tries=4):
    for i in range(tries):
        try:
            r = requests.get(url, headers=HDRS, timeout=90)
            if r.status_code in (200, 301, 302):
                return r
        except Exception as e:
            err = e
        time.sleep(10)
    return None


results = {}
for label, url, kws in CHECKS + LIVE:
    r = grab(url)
    if r is None:
        print(f"FAIL [no response] {label}")
        results[label] = None
        continue
    body = r.text.lower() if "%PDF" not in kws else r.content[:8].decode("latin1")
    hits = [k for k in kws if k.lower() in body]
    ok = "PASS" if hits else "FAIL"
    print(f"{ok} [{r.status_code}] {label} hits={hits}")
    results[label] = {"status": r.status_code, "hits": hits}

for label, q in CDXQ:
    time.sleep(10)
    try:
        r = requests.get(CDX, params={"url": q, "output": "text", "limit": 8},
                         headers=HDRS, timeout=90)
        out = r.text.strip() or "(empty)"
    except Exception as e:
        out = f"err: {e}"
    print(f"\nCDX {label}:\n{out}")
    results["cdx " + label] = out

with open("verify_vietnam_results.json", "w") as f:
    json.dump(results, f, indent=1)
print("\nwrote verify_vietnam_results.json")
