#!/usr/bin/env python3
"""Slow, single-threaded CDX check for a handful of URLs named on argv.

Exists because a negative from a bulk sweep is only trustworthy if archive.org
was actually answering at the time -- a throttled availability API returns an
empty result that looks exactly like "never archived".  Anything important
enough to re-source deserves one deliberate, unhurried re-ask before we accept
the negative and go hunting for a replacement.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "Chrome/126 Safari/537.36")


def cdx(url, statuscode="200"):
    q = ("http://web.archive.org/cdx/search/cdx?url="
         + urllib.parse.quote(url, safe="")
         + f"&output=json&limit=5&filter=statuscode:{statuscode}&collapse=digest")
    body = urllib.request.urlopen(
        urllib.request.Request(q, headers={"User-Agent": UA}), timeout=60).read().decode()
    if not body.strip().startswith("["):
        return "THROTTLED", None
    rows = json.loads(body)
    if len(rows) < 2:
        return None, None
    ts, orig = rows[1][1], rows[1][2]
    return f"http://web.archive.org/web/{ts}/{orig}", ts


for u in sys.argv[1:]:
    for code in ("200", "30[12]"):
        try:
            wb, ts = cdx(u, code)
        except Exception as e:
            wb, ts = f"ERR {type(e).__name__}", None
        if wb:
            break
        time.sleep(4)
    print(json.dumps({"url": u, "wayback": wb, "ts": ts}), flush=True)
    with open("cdx_focus.jsonl", "a") as fh:
        fh.write(json.dumps({"url": u, "wayback": wb, "ts": ts}) + "\n")
    time.sleep(4)
