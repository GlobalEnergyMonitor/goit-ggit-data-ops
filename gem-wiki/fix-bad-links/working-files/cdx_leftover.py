#!/usr/bin/env python3
"""Second pass for URLs the fast availability API could not answer.

`wb_fill.py` asks the availability API and then two CDX queries for every URL,
which is three archive.org round-trips each and rate-limits long before it
finishes.  Splitting it pays: an availability-only sweep answers most URLs
cheaply (avail_probe), and only the residue needs CDX.  This runs that residue
at low concurrency -- archive.org throttles the *account*, not the connection,
so more workers here just manufactures THROTTLED verdicts.
"""
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

from wb_fill import cdx

DIAGS = ("diag_itesx.json", "diag_germany.json")

left = json.load(open("avail_leftover.json"))
todo = left["retry"] + left["cdx"]          # throttled first: likeliest to resolve
lock = threading.Lock()
out, done = {}, [0]


def run(u):
    wb, ts = cdx(u, "200")
    if not wb:
        wb, ts = cdx(u, "30[12]")
    with lock:
        out[u] = (wb, ts)
        done[0] += 1
        print(f"[{done[0]}/{len(todo)}] {str(wb)[:70]:70} {u[:60]}",
              file=sys.stderr, flush=True)
        with open("cdx_leftover.jsonl", "a") as fh:
            fh.write(json.dumps({"url": u, "wayback": wb, "ts": ts}) + "\n")


with ThreadPoolExecutor(max_workers=2) as p:
    list(p.map(run, todo))

for f in DIAGS:
    d = json.load(open(f))
    n = 0
    for u, (wb, ts) in out.items():
        if u in d and wb and wb != "THROTTLED":
            d[u]["wayback"] = wb
            d[u]["wayback_ts"] = ts
            n += 1
    json.dump(d, open(f, "w"), indent=1, ensure_ascii=False)
    print(f"{f} filled {n}", file=sys.stderr)
