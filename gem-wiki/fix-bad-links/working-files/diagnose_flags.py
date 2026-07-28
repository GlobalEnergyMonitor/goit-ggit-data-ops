#!/usr/bin/env python3
"""Diagnose flagged URLs from scan_*.json: browser-header retry + Wayback.

Usage:
  python3 diagnose_flags.py                       # every scan_*.json (all batches)
  python3 diagnose_flags.py scan_italy.json ...   # just this batch
  python3 diagnose_flags.py -o diag_italy.json scan_italy.json

Pass the batch's own scan files — the bare form re-diagnoses every country
ever scanned, which is minutes of needless refetching.

For every unique URL flagged CHECK / BROKEN / SOFT404 / DRIFT (and bit.ly
WEAK), report:
  - retry: status with full browser headers, final URL
  - wayback: closest snapshot URL + timestamp (availability API)
Writes diagnosis.json (or -o). WEAK/PDF-UNCHECKED left to manual judgment.
"""
import json
import glob
import sys
import time

import requests

HDRS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

VERDICTS = {"CHECK", "BROKEN", "SOFT404", "MALFORMED"}
FLAGS = {"DRIFT"}


def wayback(url):
    """Fast triage lookup only — one availability-API call, no retry.

    A blank here means "not found *this second*", NOT "never archived":
    archive.org rate-limits by answering with an empty result, and on
    2026-07-28 that turned all 106 Italy/Spain lookups into false negatives.
    Resolve archives properly with `wb_fill.py` (availability -> CDX 200 ->
    CDX 30x, with backoff and a THROTTLED sentinel) before concluding a ref is
    unrecoverable."""
    try:
        r = requests.get("https://archive.org/wayback/available",
                         params={"url": url}, headers=HDRS, timeout=30)
        snap = r.json().get("archived_snapshots", {}).get("closest", {})
        return snap.get("url"), snap.get("timestamp")
    except Exception as e:
        return None, f"err:{e}"[:80]


def retry(url):
    try:
        r = requests.get(url, headers=HDRS, timeout=30, allow_redirects=True,
                         stream=True)
        ctype = r.headers.get("content-type", "").split(";")[0]
        body = b""
        if "html" in ctype:
            body = r.raw.read(300000, decode_content=True)
        r.close()
        return r.status_code, r.url, ctype, body.decode("utf-8", "replace")
    except requests.RequestException as e:
        return None, url, "", str(e)[:120]


def main(argv):
    out_path = "diagnosis.json"
    if len(argv) >= 2 and argv[0] == "-o":
        out_path, argv = argv[1], argv[2:]
    files = argv or sorted(glob.glob("scan_*.json"))
    targets = {}  # url -> list of (country, page, n, verdict, flag, keywords)
    for f in files:
        if f == "scan_queue.json":
            continue
        country = f[5:-5] if f.startswith("scan_") else f
        d = json.load(open(f))
        for page, rep in d.items():
            if "error" in rep:
                continue
            kw = rep.get("keywords", [])
            for r in rep["results"]:
                u = r.get("url")
                if not u:
                    continue
                v, fl = r.get("verdict"), r.get("flag", "")
                if v in VERDICTS or fl in FLAGS or "bit.ly" in u:
                    targets.setdefault(u, []).append(
                        (country, page, r["n"], v, fl, kw))
    print(f"{len(targets)} unique URLs to diagnose", file=sys.stderr)
    out = {}
    for i, (u, cites) in enumerate(sorted(targets.items()), 1):
        status, final, ctype, body = retry(u)
        kws = {k for c in cites for k in c[5]}
        low = body.lower() if body else ""
        kw_hits = sorted(k for k in kws if k in low)
        wb_url, wb_ts = wayback(u)
        out[u] = {
            "cites": [c[:5] for c in cites],
            "retry_status": status,
            "final_url": final if final != u else None,
            "ctype": ctype,
            "kw_hits": kw_hits,
            "body_head": low[:200] if status and status != 200 else "",
            "wayback": wb_url,
            "wayback_ts": wb_ts,
        }
        print(f"[{i}/{len(targets)}] {status} wb={'Y' if wb_url else 'N'} {u[:80]}",
              file=sys.stderr, flush=True)
        time.sleep(0.3)
    json.dump(out, open(out_path, "w"), indent=1, ensure_ascii=False)
    print("wrote " + out_path, file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
