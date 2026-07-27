#!/usr/bin/env python3
"""Round 2: resolve the failures/unknowns from verify_vietnam.py."""
import time

import requests

HDRS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
WB = "https://web.archive.org/web/"
CDX = "https://web.archive.org/cdx/search/cdx"


def grab(url, tries=3):
    for i in range(tries):
        try:
            r = requests.get(url, headers=HDRS, timeout=90)
            return r
        except Exception as e:
            print(f"   (attempt {i+1} err: {e})")
            time.sleep(10)
    return None


def content_check(label, url, kws, pdf=False):
    r = grab(url)
    if r is None:
        print(f"FAIL [no response] {label}")
        return
    if pdf:
        magic = r.content[:8].decode("latin1", "replace")
        print(f"{'PASS' if magic.startswith('%PDF') else 'FAIL'} "
              f"[{r.status_code}] {label} magic={magic!r} len={len(r.content)}")
        return
    body = r.text.lower()
    hits = [k for k in kws if k.lower() in body]
    print(f"{'PASS' if hits else 'FAIL'} [{r.status_code}] {label} "
          f"hits={hits} len={len(body)}")


def cdx(label, **params):
    time.sleep(10)
    p = {"output": "text", "limit": 10}
    p.update(params)
    try:
        r = requests.get(CDX, params=p, headers=HDRS, timeout=90)
        print(f"\nCDX {label}:\n{r.text.strip() or '(empty)'}")
    except Exception as e:
        print(f"\nCDX {label}: err {e}")


# 1. jccp: find a real PDF capture
cdx("jccp pdf all", url="jccp.or.jp/country/docs/4_CPJ-5-18_MOIT.pdf")

# 2. energyintel wayback: check title text instead
content_check("energyintel wayback title",
              WB + "20250723145420/https://www.energyintel.com/00000188-9e31-dfa7-aded-9ffb3ab90000",
              ["cautious support", "new power plan", "vietnam"])

# 3. marinecurrents thai binh: any capture under other params
cdx("marinecurrents thai binh prefix",
    url="marinecurrents.com/thai-binh-lng-power-plant*", matchType="prefix")

# 4. marinecurrents hai phong archived copy content
content_check("marinecurrents hai phong wayback",
              WB + "20221005115805/https://www.marinecurrents.com/two-hai-phong-lng-to-power-projects-ensure-clean-energy-resource-for-vietnam/",
              ["hai phong", "tien lang"])

# 5. powerengineeringint: where does the archived 301 go?
r = grab(WB + "20180525175321/http://www.powerengineeringint.com/articles/2018/03/edf-to-build-new-gas-fired-power-plant-in-vietnam.html")
if r is not None:
    print(f"\npowerengineeringint archived redirect: final={r.url} "
          f"status={r.status_code}")
    body = r.text.lower()
    hits = [k for k in ["edf", "son my", "vietnam"] if k in body]
    print(f"   content hits={hits} len={len(body)}")

# 6. hanoitimes snapshot content
content_check("hanoitimes wayback",
              WB + "20211130084118/http://hanoitimes.vn/aes-petrovietnam-set-up-joint-venture-for-us14-billion-lng-terminal-314645.html",
              ["aes", "petrovietnam"])

# 7. vneconomy vung ang iii snapshot content
content_check("vneconomy vung ang iii wayback",
              WB + "20260611152718/https://en.vneconomy.vn/ha-tinh-approves-2bln-vung-ang-iii-lng-power-plant-project.htm",
              ["vung ang", "b.grimm"])

# 8. vneconomy live retries (site may have been down during scan)
content_check("vneconomy vung ang iii LIVE",
              "https://en.vneconomy.vn/ha-tinh-approves-2bln-vung-ang-iii-lng-power-plant-project.htm",
              ["vung ang"])
content_check("vneconomy bgrimm LIVE",
              "https://en.vneconomy.vn/pv-power-and-bgrimm-sign-agreement-for-2bln-lng-power-project-in-ha-tinh-province.htm",
              ["b.grimm", "vung ang", "ha tinh"])

# 9. marinecurrents live homepage — what is the site now?
r = grab("https://www.marinecurrents.com/")
if r is not None:
    import re
    m = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
    print(f"\nmarinecurrents homepage [{r.status_code}] "
          f"title={m.group(1).strip()[:120] if m else '(none)'}")
