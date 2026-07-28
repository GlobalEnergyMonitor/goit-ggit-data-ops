#!/usr/bin/env python3
"""Content-verify the Wayback snapshots recorded in a diag_*.json.

`wb_fill.py` only proves a capture EXISTS. A 200 capture is routinely unusable:
Wayback happily replays a site's own "article not found" page, or a JS shell
with no article text, and both look healthy from the outside. So before a
snapshot becomes a citation, fetch it and judge the body:

  PASS       200, no soft-404 tell, real body text, and it names the terminal
  THIN       loads but no keyword match, or too little text to be an article
  FAIL       the snapshot itself errors or replays a 404
  NO-ARCHIVE nothing captured (or the lookup was THROTTLED — recheck those)

Usage:
  python3 verify_snaps.py diag_italy.json [more.json ...] > verify_italy.json
  python3 verify_snaps.py -j6 diag_italy.json

Reads the dict-shaped diag files written by diagnose_flags.py -o (url -> record
with `cites` and `wayback`); results are keyed by URL and cached in
verify_snaps_cache.jsonl so an interrupted run resumes for free.
"""
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from scan_background_refs import (BROWSER_UA, LNG_WORDS, SOFT404_PATTERNS,
                                  TAG_RE, name_keywords)

CACHE = "verify_snaps_cache.jsonl"


def fetch(url):
    """Wayback is slow and flaky; retry with backoff. urllib3's ReadTimeoutError
    can escape r.raw.read() without being a requests.RequestException, so catch
    broadly."""
    err = "unknown"
    for attempt in range(4):
        try:
            r = requests.get(url, headers={"User-Agent": BROWSER_UA},
                             timeout=(20, 45), allow_redirects=True, stream=True)
            ctype = r.headers.get("content-type", "").split(";")[0]
            head = r.raw.read(600000, decode_content=True)
            r.close()
            return r.status_code, ctype, head, r.url
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:100]}"
            time.sleep(5 * (attempt + 1))
    return None, "", err.encode(), url


def strip_chrome(html):
    """Drop the Wayback banner and scripts so their text can't satisfy checks."""
    html = re.sub(r"(?is)<!--\s*BEGIN WAYBACK TOOLBAR INSERT\s*-->.*?"
                  r"<!--\s*END WAYBACK TOOLBAR INSERT\s*-->", " ", html)
    html = re.sub(r"(?is)<script.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?</style>", " ", html)
    return html


def verify(snapshot, titles):
    """Follow the capture and keep the canonical 14-digit snapshot URL, so the
    citation pins the exact capture we verified rather than whatever Wayback
    resolves to later."""
    status, ctype, raw, final = fetch(snapshot)
    out = {"snapshot": final if re.search(r"/web/\d{14}/", final) else snapshot,
           "requested": snapshot, "snap_status": status, "ctype": ctype}
    if status is None:
        return {**out, "result": "FAIL", "why": f"fetch error: {raw[:100]}"}
    if status != 200:
        return {**out, "result": "FAIL", "why": f"snapshot HTTP {status}"}
    if raw[:5] == b"%PDF-":
        return {**out, "result": "PASS", "why": "pdf replays, url identity"}
    if "html" not in ctype:
        return {**out, "result": "PASS", "why": f"non-html ({ctype}), url identity"}
    clean = strip_chrome(raw.decode("utf-8", "replace"))
    text = re.sub(r"\s+", " ", TAG_RE.sub(" ", clean)).strip()
    low = text.lower()
    hit = SOFT404_PATTERNS.search(clean)
    if hit:
        return {**out, "result": "FAIL", "chars": len(text),
                "why": "soft-404 tell: " + hit.group(0)[:60]}
    kws = sorted({w for t in titles for w in name_keywords(t) if w in low})
    lng = [w for w in LNG_WORDS if w in low]
    out.update(chars=len(text), kw_hits=kws, lng_hits=lng)
    if len(text) < 600:
        return {**out, "result": "THIN", "why": f"only {len(text)} chars of text"}
    if kws:
        return {**out, "result": "PASS", "why": f"names terminal: {kws}"}
    if lng:
        return {**out, "result": "THIN", "why": f"lng vocabulary only: {lng}"}
    return {**out, "result": "THIN", "why": "no terminal keyword, no lng vocabulary"}


def main(argv):
    workers = next((int(a[2:]) for a in argv if a.startswith("-j")), 4)
    paths = [a for a in argv if not a.startswith("-")]
    rows = {}
    for path in paths:
        for url, rec in json.load(open(path)).items():
            rows.setdefault(url, rec)
    cache = {}
    try:
        for line in open(CACHE):
            if line.strip():
                r = json.loads(line)
                cache[r["url"]] = r
    except FileNotFoundError:
        pass
    lock = threading.Lock()
    out = {}
    with open(CACHE, "a") as fh:
        def run(item):
            url, rec = item
            if url in cache:
                res = cache[url]
            else:
                wb = rec.get("wayback")
                titles = sorted({c[1] for c in rec.get("cites", [])})
                if not wb or wb == "THROTTLED":
                    res = {"result": "NO-ARCHIVE", "why": str(wb) or "no snapshot"}
                else:
                    res = verify(wb, titles)
                res = {"url": url, "cites": rec.get("cites", []),
                       "retry_status": rec.get("retry_status"),
                       "final_url": rec.get("final_url"), **res}
                with lock:
                    fh.write(json.dumps(res, ensure_ascii=False) + "\n")
                    fh.flush()
            with lock:
                out[url] = res
                print(f"{res['result']:11} {res.get('why','')[:60]:60} {url[:60]}",
                      file=sys.stderr, flush=True)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(run, rows.items()))
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
