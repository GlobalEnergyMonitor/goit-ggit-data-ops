#!/usr/bin/env python3
"""Re-fetch the validate_us_snaps.py rows whose fetch never got a straight
answer. A ConnectionError to web.archive.org is archive.org refusing the
connection, not a dead snapshot -- recording it as a negative would send wave 6
chasing repairs that are not needed. 8 s gap, single thread, one consumer."""
import json
import sys

import validate_us_snaps as V
import requests
import time

rows = json.load(open("validate_us_snaps.json"))
retry = [r for r in rows if r["status"] in ("ERR", 403)]
print(f"{len(retry)} rows to re-fetch", file=sys.stderr)
for i, r in enumerate(retry, 1):
    try:
        resp = requests.get(r["snapshot"], headers={"User-Agent": V.UA},
                            timeout=120)
        body = V.strip(resp.text)
        r.update(status=resp.status_code, final=resp.url,
                 bytes=len(resp.content),
                 hits=[w for w in r["want"] if w in body.lower()],
                 junk=bool(V.JUNK.search(body[:4000])), head=body[:1200])
        r.pop("error", None)
    except Exception as e:
        r.update(status="ERR", error=repr(e))
    print(f'{i:2d}/{len(retry)}  {str(r["status"]):>4}  '
          f'hits {len(r["hits"]):2d}/{len(r["want"]):2d}  {r["url"][:64]}',
          flush=True)
    json.dump(rows, open("validate_us_snaps.json", "w"), indent=1,
              ensure_ascii=False)
    time.sleep(8)
