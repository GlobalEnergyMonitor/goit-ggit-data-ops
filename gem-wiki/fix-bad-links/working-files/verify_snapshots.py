#!/usr/bin/env python3
"""Verify planned Wayback swaps actually contain the expected content."""
import json
import time

import requests

HDRS = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/126.0.0.0 Safari/537.36")}

SNAPSHOTS = [
    ("slng terminal-layout",
     "https://web.archive.org/web/20160423025450/http://www.slng.com.sg/website/content.aspx?wpi=Terminal+Layout&mmi=85&smi=112",
     ["singapore lng", "terminal"]),
    ("lngworldnews fifth-tank",
     "https://web.archive.org/web/20190916141017/https://www.lngworldnews.com/slng-tests-the-market-demand-for-fifth-lng-storage-tank/",
     ["fifth", "storage tank"]),
    ("ema EOI pdf",
     "https://web.archive.org/web/20220119004645/https://www.ema.gov.sg/cmsmedia/Expression%20of%20Interest%20for%20OLT_final.pdf",
     ["%PDF"]),
    ("zawya sg regulatory",
     "https://web.archive.org/web/20201028150155/https://www.zawya.com/mena/en/story/Singapore_drafting_regulatory_framework_for_2nd_LNG_terminal_minister_says-TR20201027nL1N2HI097X1/",
     ["regulatory framework", "lng"]),
    ("igu 2019 pdf",
     "https://web.archive.org/web/20191215013015/https://www.igu.org/sites/default/files/node-news_item-field_file/IGU%20Annual%20Report%202019_23%20loresfinal.pdf",
     ["%PDF"]),
    ("hellenic qatar-shipping",
     "https://web.archive.org/web/20180215210624/http://www.hellenicshippingnews.com/qatar-shipping-company-moves-hub-from-uae-to-oman/",
     ["milaha", "oman"]),
    ("gnlglobal golar igloo (wb)",
     "https://web.archive.org/web/20240413220823/https://gnlglobal.com/la-fsru-golar-igloo-de-new-fortress-energy-ya-se-encuentra-en-europa/",
     ["golar igloo", "kuwait"]),
    ("qatargas history",
     "https://web.archive.org/web/20230829134649/https://www.qatargas.com/english/aboutus/history",
     ["1984", "qatargas"]),
    ("qatargas venture pdf",
     "https://web.archive.org/web/20230829134547/https://www.qatargas.com/english/aboutus/Documents/Venture%20Portfolio_Final.pdf",
     ["%PDF"]),
    ("qatargas corp-structure",
     "https://web.archive.org/web/20230829134622/https://www.qatargas.com/english/aboutus/corporate-structure",
     ["conocophillips", "mitsui"]),
    ("qatargas lng-trains",
     "https://web.archive.org/web/20230829134625/https://www.qatargas.com/english/operations/lng-trains",
     ["train", "7.8"]),
    ("agsiw lng dominance",
     "https://web.archive.org/web/20250215170326/http://www.agsiw.org/qatar-moves-ensure-lng-dominance/",
     ["80 million", "lng"]),
    ("cnbc 126mt",
     "https://web.archive.org/web/20200211135956/https://www.cnbc.com/2019/11/25/reuters-america-update-2-qatar-plans-to-boost-lng-production-to-126-mln-t-by-2027.html",
     ["126", "qatar"]),
    ("clydeco north field east",
     "https://web.archive.org/web/20210513053142/https://www.clydeco.com/en/insights/2021/03/qatar-s-north-field-east-lng-liquefaction-project",
     ["north field east", "carbon"]),
    ("mechademy qatargas2",
     "https://web.archive.org/web/20230307103850/https://www.mechademy.com/lng_plant/qatargas-2-trains-4-5/",
     ["qatargas 2", "2009"]),
]

LIVE = [
    ("gnlglobal live", "https://gnlglobal.com/la-fsru-golar-igloo-de-new-fortress-energy-ya-se-encuentra-en-europa/",
     ["golar igloo", "kuwait"]),
    ("energyinst 5092 live", "https://www.energyinst.org/documents/5092",
     ["fsru"]),
]


def grab(url):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HDRS, timeout=90)
            return r.status_code, r.content[:400000]
        except requests.RequestException as e:
            err = str(e)[:100]
            time.sleep(10)
    return None, err.encode()


def main():
    out = {}
    for name, url, kws in SNAPSHOTS + LIVE:
        status, body = grab(url)
        low = body.decode("utf-8", "replace").lower()
        hits = [k for k in kws if k.lower() in low or
                (k == "%PDF" and body[:5] == b"%PDF-")]
        out[name] = {"status": status, "hits": hits, "want": kws,
                     "ok": status == 200 and len(hits) == len(kws)}
        print(f"{'PASS' if out[name]['ok'] else 'FAIL'} [{status}] {name} "
              f"hits={hits}", flush=True)
        time.sleep(2)

    # CDX extras
    cdx = {}
    for name, u, mt in [
        ("reuters www factbox", "reuters.com/article/gulf-qatar-energy/factbox-oil-majors", "prefix"),
        ("slng samsung epc (lngworldnews)", "lngworldnews.com/slng-awards", "prefix"),
        ("slng samsung epc (site)", "slng.com.sg/website/content.aspx?wpi=Media+Release", "prefix"),
        ("energyinst 5092", "energyinst.org/documents/5092", "exact"),
    ]:
        params = {"url": u, "output": "text", "limit": "10",
                  "collapse": "urlkey"}
        if mt == "prefix":
            params["matchType"] = "prefix"
        for attempt in range(3):
            try:
                r = requests.get("https://web.archive.org/cdx/search/cdx",
                                 params=params, headers=HDRS, timeout=90)
                cdx[name] = r.text.strip()[:1500]
                break
            except requests.RequestException as e:
                cdx[name] = f"ERR {e}"[:120]
                time.sleep(10)
        print(f"CDX {name}:\n{cdx[name] or '(empty)'}\n", flush=True)
        time.sleep(2)

    json.dump({"snapshots": out, "cdx": cdx}, open("verify_results.json", "w"),
              indent=1)
    print("wrote verify_results.json")


if __name__ == "__main__":
    main()
