#!/usr/bin/env python3
"""Task 3 (Thailand/Turkiye/UAE): verify planned wayback swaps, live checks, CDX lookups."""
import json
import time

import requests

HDRS = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/126.0.0.0 Safari/537.36")}

SNAPSHOTS = [
    ("pttlng pj_composition",
     "https://web.archive.org/web/20171031022834/http://www.pttlng.com/en/pj_composition.aspx",
     ["lng"]),
    ("pttlng pj_mile",
     "https://web.archive.org/web/20171105162738/http://www.pttlng.com/en/pj_mile.aspx",
     ["lng"]),
    ("lngworldnews ptt-upping",
     "https://web.archive.org/web/20190517003942/https://www.lngworldnews.com/ptt-upping-lng-import-capacity-second-import-terminal-approved/",
     ["ptt", "import"]),
    ("etkiliman FSRU.html",
     "https://web.archive.org/web/20241214214632/http://etkiliman.com.tr/en/FSRU/FSRU.html",
     ["fsru"]),
    ("igu 103419 pdf",
     "https://web.archive.org/web/20191028040840/https://www.igu.org/sites/default/files/node-document-field_file/103419-World_IGU_Report_FINAL_LR.PDF",
     ["%PDF"]),
    ("lngworldnews adgas",
     "https://web.archive.org/web/20171121232403/http://www.lngworldnews.com/adgas-to-shut-down-two-lng-trains-for-scheduled-maintenance/",
     ["adgas", "maintenance"]),
]

LIVE = [
    ("energyintel sharjah live",
     "https://www.energyintel.com/0000017b-a7d8-de4c-a17b-e7da104a0000",
     ["sharjah", "uniper"]),
    ("dw.com uae-germany live",
     "https://www.dw.com/en/lng-for-germany-uae-delivers-first-shipment/a-64292879",
     ["das island", "germany"]),
    ("turkiyetoday dortyol article",
     "https://www.turkiyetoday.com/business/turkiye-plans-new-fsru-deployment-at-dortyol-terminal-minister-3213860",
     ["dortyol", "fsru"]),
    ("wam.ae adnoc third HoA live",
     "https://www.wam.ae/en/article/b31snxc-adnoc-signs-third-long-term-heads-agreement-for",
     ["enbw", "ruwais"]),
    ("adnoc fid press release",
     "https://www.adnoc.ae/en/news-and-media/press-releases/2024/adnoc-takes-fid-on-ruwais-lng-project",
     ["ruwais", "fid"]),
]

CDX = [
    ("lngworldnews engie etki", "lngworldnews.com/engie-turkeys-first-fsru-inaugurated", "prefix"),
    ("etkiliman inaugurates", "etkiliman.com.tr/EN/news/Turkey-inaugurates-its-first-FSRU-at-Aliaga.html", "exact"),
    ("etkiliman inaugurates prefix", "etkiliman.com.tr/en/news/Turkey-inaugurates", "prefix"),
    ("bitly 2xvfCBI", "bit.ly/2xvfCBI", "exact"),
    ("lngworldnews uae another fsru", "lngworldnews.com/report-uae-plans-another-lng-fsru", "prefix"),
    ("zawya sharjah ownership", "zawya.com/mena/en/story/Sharjah_takes_full_ownership_of_strategic_LNG_import_project-ZAWYA20190619134347/", "exact"),
    ("sefe adnoc hoa", "sefe-group.com/en/newsroom/press-releases/sefe-signs-a-long-term-heads-of-agreement-with-adnoc", "prefix"),
    ("wam b31snxc", "wam.ae/en/article/b31snxc-adnoc-signs-third-long-term-heads-agreement-for", "exact"),
    ("ceenergynews dortyol", "ceenergynews.com/lng/", "prefix"),
    ("energyintel sharjah", "energyintel.com/0000017b-a7d8-de4c-a17b-e7da104a0000", "exact"),
]


def grab(url):
    err = b"no attempt"
    for attempt in range(4):
        try:
            r = requests.get(url, headers=HDRS, timeout=90)
            return r.status_code, r.content[:400000]
        except requests.RequestException as e:
            err = str(e)[:120].encode()
            time.sleep(10)
    return None, err


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

    cdx = {}
    for name, u, mt in CDX:
        params = {"url": u, "output": "text", "limit": "12",
                  "collapse": "urlkey"}
        if mt == "prefix":
            params["matchType"] = "prefix"
        got = "(none)"
        for attempt in range(4):
            try:
                r = requests.get("https://web.archive.org/cdx/search/cdx",
                                 params=params, headers=HDRS, timeout=90)
                got = r.text.strip()[:2000]
                break
            except requests.RequestException as e:
                got = f"ERR {e}"[:120]
                time.sleep(12)
        cdx[name] = got
        print(f"CDX {name}:\n{got or '(empty)'}\n", flush=True)
        time.sleep(2)

    json.dump({"snapshots": out, "cdx": cdx},
              open("verify_task3_results.json", "w"), indent=1)
    print("wrote verify_task3_results.json")


if __name__ == "__main__":
    main()
