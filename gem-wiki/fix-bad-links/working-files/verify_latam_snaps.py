#!/usr/bin/env python3
"""Content-verify candidate Wayback snapshots for the LatAm small-country batch.

Reads diag_latam_small.json rows
([title, n, verdict, status, url, recheck, final_url, wayback]) and, for every
row with a snapshot, fetches that snapshot and decides whether it is usable as
a swap target:

  PASS       - 200, no soft-404 tell, real body text, and it names the terminal
  THIN       - loads but no keyword match, or too little text to be an article
               (likely a homepage shell or JS-only capture) -> needs eyes
  FAIL       - the snapshot itself errors or replays a 404
  NO-ARCHIVE - nothing captured

Usage: python3 verify_latam_snaps.py > verify_latam.json
"""
import json
import re
import sys
import time

import requests

from scan_background_refs import (BROWSER_UA, LNG_WORDS, SOFT404_PATTERNS,
                                  TAG_RE, name_keywords)

WB = "https://web.archive.org/web/"


def snap_url(wayback, original):
    """wayback field looks like '20250522 s200' -> use the timestamp."""
    return f"{WB}{wayback.split()[0]}/{original}"


def fetch(url):
    """Wayback is slow and flaky; retry with backoff. Note urllib3's
    ReadTimeoutError can escape r.raw.read() without being a
    requests.RequestException, so catch broadly."""
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


def verify(title, url, wayback):
    """The diag file only kept the capture DATE, and a date-only Wayback URL
    302s to the nearest capture. Follow that redirect and keep the canonical
    14-digit snapshot URL, so the citation pins the exact capture we verified
    rather than whatever Wayback resolves to later."""
    su = snap_url(wayback, url)
    status, ctype, raw, final = fetch(su)
    out = {"snapshot": final if re.search(r"/web/\d{14}/", final) else su,
           "requested": su, "snap_status": status, "ctype": ctype}
    if status is None:
        return {**out, "result": "FAIL", "why": f"fetch error: {raw[:100]}"}
    if status != 200:
        return {**out, "result": "FAIL", "why": f"snapshot HTTP {status}"}
    if raw[:5] == b"%PDF-":
        return {**out, "result": "PASS", "why": "pdf replays, url identity"}
    if "html" not in ctype:
        return {**out, "result": "PASS", "why": f"non-html ({ctype}), url identity"}
    html = raw.decode("utf-8", "replace")
    clean = strip_chrome(html)
    text = re.sub(r"\s+", " ", TAG_RE.sub(" ", clean)).strip()
    low = text.lower()
    hit = SOFT404_PATTERNS.search(clean)
    if hit:
        return {**out, "result": "FAIL", "chars": len(text),
                "why": "soft-404 tell: " + hit.group(0)[:60]}
    kws = [w for w in name_keywords(title) if w in low]
    lng = [w for w in LNG_WORDS if w in low]
    out.update(chars=len(text), kw_hits=kws, lng_hits=lng)
    if len(text) < 600:
        return {**out, "result": "THIN", "why": f"only {len(text)} chars of text"}
    if kws:
        return {**out, "result": "PASS", "why": f"names terminal: {kws}"}
    if lng:
        return {**out, "result": "THIN", "why": f"lng vocabulary only: {lng}"}
    return {**out, "result": "THIN", "why": "no terminal keyword, no lng vocabulary"}


CACHE = "verify_latam_cache.jsonl"


def load_cache():
    done = {}
    try:
        for line in open(CACHE):
            line = line.strip()
            if line:
                r = json.loads(line)
                done[(r["page"], r["n"])] = r
    except FileNotFoundError:
        pass
    return done


def main():
    """Results are appended to verify_latam_cache.jsonl as they land, so a
    crash or a Wayback outage only costs the row in flight — rerun to resume."""
    rows = json.load(open("diag_latam_small.json"))
    done = load_cache()
    out = []
    with open(CACHE, "a") as cache:
        for title, n, verdict, status, url, recheck, final, wayback in rows:
            if (title, n) in done:
                rec = done[(title, n)]
                out.append(rec)
                print(f"{rec['result']:11} {title} [{n}] (cached)",
                      file=sys.stderr, flush=True)
                continue
            rec = {"page": title, "n": n, "verdict": verdict, "status": status,
                   "url": url, "recheck": recheck, "wayback": wayback}
            if not wayback or "s200" not in str(wayback):
                rec.update(result="NO-ARCHIVE", why=str(wayback) or "no snapshot")
            else:
                rec.update(verify(title, url, wayback))
            out.append(rec)
            cache.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cache.flush()
            print(f"{rec['result']:11} {title} [{n}] {rec.get('why','')[:66]}",
                  file=sys.stderr, flush=True)
            time.sleep(1)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
