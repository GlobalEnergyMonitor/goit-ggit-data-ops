#!/usr/bin/env python3
"""US batch, wave 6 prep -- content-validate each Wayback snapshot before citing it.

  python3 validate_us_snaps.py            # validate every still-live archived url
  python3 validate_us_snaps.py -o out.json

A snapshot url is not evidence. archive.org will happily serve a 200 that is a
capture of a 404 page, a paywall interstitial, a cookie wall, or the publisher's
homepage after a redirect -- all of which look identical to a real capture from
the outside. So every candidate is fetched, tag-stripped, and scored against
words drawn from the citing sentence and the ref's own link text. The output is
for human/agent judgment, not an automatic accept: `hits` says the snapshot is
plausibly the cited document, and nothing more.

Deliberately single-threaded with a 3 s gap. The project's cap is 3 concurrent
archive.org consumers and the CDX passes have been eating all three; more
importantly a throttled 429 here would read as a dead snapshot and send a later
wave chasing repairs that are not needed. Slow and trustworthy beats fast.
"""
import argparse
import html
import json
import re
import sys
import time

import requests

UA = "GEM research baird.langenbrunner@globalenergymonitor.org"
STOP = set("""the a an and or of in on at to for from with by is are was were be
been being as that this these those it its his her their our your not no all
any more most other some such than then there here what which who whom how when
where why can will just also into over under after before about""".split())
TAGS = re.compile(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>|<[^>]+>")
WS = re.compile(r"\s+")

# Wayback's own furniture, plus the signatures of a capture that captured
# nothing. Presence of these is not failure on its own -- the toolbar is on every
# capture -- but a body that is *only* these is.
JUNK = re.compile(r"(?i)page cannot be found|404 not found|access denied"
                  r"|subscribe to continue|enable javascript|are you a robot")


def words(*texts):
    out = []
    for t in texts:
        for w in re.findall(r"[a-z0-9']{4,}", (t or "").lower()):
            if w not in STOP and w not in out:
                out.append(w)
    return out


def strip(h):
    return WS.sub(" ", html.unescape(TAGS.sub(" ", h))).strip()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", default="validate_us_snaps.json")
    ap.add_argument("--sleep", type=float, default=3.0)
    a = ap.parse_args(argv)

    diag = json.load(open("diag_us.json"))
    scan = json.load(open("scan_us.json"))
    live = json.load(open("wb_still_live.json"))

    # url -> the citing sentence(s), for keyword derivation and human reading
    ctx = {}
    for page, rec in scan.items():
        for r in rec.get("results", []):
            if r.get("url"):
                ctx.setdefault(r["url"], []).append((page, r.get("context", "")))

    todo = [u for u in live
            if (diag[u].get("wayback") or "") not in ("", "THROTTLED")]
    print(f"{len(todo)} snapshots to validate", file=sys.stderr)

    out = []
    for i, u in enumerate(todo, 1):
        snap = diag[u]["wayback"]
        pages = [p for p, _ in ctx.get(u, [])]
        sents = [c for _, c in ctx.get(u, [])]
        want = words(*sents)[:25]
        try:
            r = requests.get(snap, headers={"User-Agent": UA}, timeout=90)
            body = strip(r.text)
            rec = {"url": u, "snapshot": snap, "ts": diag[u].get("wayback_ts"),
                   "pages": pages, "context": sents, "status": r.status_code,
                   "final": r.url, "bytes": len(r.content),
                   "hits": [w for w in want if w in body.lower()],
                   "want": want, "junk": bool(JUNK.search(body[:4000])),
                   "head": body[:1200]}
        except Exception as e:
            rec = {"url": u, "snapshot": snap, "pages": pages,
                   "context": sents, "status": "ERR", "error": repr(e),
                   "hits": [], "want": want, "junk": None, "head": ""}
        out.append(rec)
        n, m = len(rec["hits"]), len(want)
        print(f'{i:3d}/{len(todo)}  {str(rec["status"]):>4}  hits {n:2d}/{m:2d}'
              f'{"  JUNK" if rec["junk"] else "":6} {u[:74]}', flush=True)
        json.dump(out, open(a.o, "w"), indent=1, ensure_ascii=False)
        time.sleep(a.sleep)

    ok = [r for r in out if r["status"] == 200 and r["hits"] and not r["junk"]]
    print(f"\n{len(ok)}/{len(out)} plausible; the rest need reading",
          file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
