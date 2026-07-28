"""Throttled post-save check of every web.archive.org URL this batch introduced.

Single-threaded with a 3 s gap -- well under archive.org's rate limits, which
matters more than speed here (a throttled 429 reads as a dead snapshot and
would send us chasing repairs that aren't needed).

Records the final URL after redirects: the Wayback machine routinely bounces a
requested timestamp to the nearest capture, which is fine, and to an
`id_`/different-year capture, which is worth eyeballing.
"""
import json
import time

import requests

UA = "GEM research baird.langenbrunner@globalenergymonitor.org"
urls = json.load(open("new_archive_urls.json"))
out = []
for i, (u, titles) in enumerate(sorted(urls.items()), 1):
    try:
        r = requests.get(u, headers={"User-Agent": UA}, timeout=60)
        rec = {"url": u, "pages": titles, "status": r.status_code,
               "final": r.url, "bytes": len(r.content)}
    except Exception as e:
        rec = {"url": u, "pages": titles, "status": "ERR", "final": "",
               "bytes": 0, "error": repr(e)}
    out.append(rec)
    flag = "" if rec["status"] == 200 else "  <<<"
    print(f'{i:2d}/{len(urls)}  {rec["status"]}  {rec["bytes"]:>8}  {u[:110]}{flag}',
          flush=True)
    time.sleep(3)

json.dump(out, open("new_archive_urls.check.jsonl", "w"), indent=1)
bad = [r for r in out if r["status"] != 200]
print(f"\n{len(out) - len(bad)}/{len(out)} OK")
for r in bad:
    print("  FAIL", r["status"], r["url"])
