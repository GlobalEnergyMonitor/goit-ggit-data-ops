#!/usr/bin/env python3
"""Two-phase parallel diagnose — same output as diagnose_flags.py, much faster.

Usage:
  python3 diagnose_parallel.py -o diag_<batch>.json scan_<batch>.json ...
  python3 diagnose_parallel.py --no-wb -o diag_<batch>.json scan_<batch>.json

`--no-wb` runs phase 1 only and writes no `wayback` key, leaving the whole
archive.org budget to whoever holds it. That is what makes two country batches
overlap: the archive cap is three consumers *project-wide*, not per batch, so
while one batch's wb_fill/cdx job is running the other's publisher phase can
still go full speed. Fill the archives in afterwards with
`wb_fill.py diag_<batch>.json`, which treats a missing key exactly like a blank.

Why two phases. diagnose_flags.py walks one URL at a time and, per URL, hits
the publisher *and* archive.org. That serializes ~450 URLs behind a single
thread and takes the better part of an hour on a US-sized batch. But the two
requests have opposite parallelism budgets:

  - the publisher retry fans out over hundreds of *different* hosts, so it
    parallelizes freely (PUB_WORKERS);
  - archive.org is one host with a hard README cap of **three consumers
    total** — past that it starts answering empty/503, which is a false
    "never archived" (see README step 3).

So phase 1 fans the retries out, and phase 2 does the availability lookups at
WB_WORKERS=3 with a small inter-request sleep. Anything the fast availability
lookup misses is still `wb_fill.py`'s job — a blank here means "not found this
second", never "unarchived".
"""
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import diagnose_flags as df

PUB_WORKERS = 12
WB_WORKERS = 3          # README cap: three archive.org consumers, total
WB_SLEEP = 0.7          # per-worker pause, keeps the aggregate rate polite

_wb_lock = threading.Lock()


def main(argv):
    out_path = "diagnosis.json"
    no_wb = "--no-wb" in argv
    argv = [a for a in argv if a != "--no-wb"]
    if len(argv) >= 2 and argv[0] == "-o":
        out_path, argv = argv[1], argv[2:]
    if not argv:
        sys.exit("pass the batch's own scan_*.json files explicitly")

    targets = df.collect_targets(argv)
    urls = sorted(targets)
    n = len(urls)
    print(f"{n} unique URLs to diagnose", file=sys.stderr)

    out = {}
    for u in urls:
        cites = targets[u]
        out[u] = {"cites": [c[:5] for c in cites],
                  "_kws": {k for c in cites for k in c[5]}}

    # phase 1 — publisher retry, wide fan-out over many distinct hosts
    done = 0
    with ThreadPoolExecutor(max_workers=PUB_WORKERS) as ex:
        futs = {ex.submit(df.retry, u): u for u in urls}
        for f in as_completed(futs):
            u = futs[f]
            done += 1
            try:
                status, final, ctype, body = f.result()
            except Exception as e:
                status, final, ctype, body = None, u, "", f"{type(e).__name__}: {e}"
            low = body.lower() if body else ""
            rec = out[u]
            rec.update(
                retry_status=status,
                final_url=final if final != u else None,
                ctype=ctype,
                kw_hits=sorted(k for k in rec["_kws"] if k in low),
                body_head=low[:200] if status and status != 200 else "",
            )
            print(f"[retry {done}/{n}] {status} {u[:80]}", file=sys.stderr, flush=True)

    # phase 2 — archive.org availability, three consumers and no more
    done = 0

    if no_wb:
        for rec in out.values():
            rec.pop("_kws", None)
        json.dump(out, open(out_path, "w"), indent=1, ensure_ascii=False)
        print(f"wrote {out_path}: {n} URLs, phase 1 only "
              f"(--no-wb; run wb_fill.py to add archives)", file=sys.stderr)
        return

    def wb(u):
        r = df.wayback(u)
        time.sleep(WB_SLEEP)
        return r

    with ThreadPoolExecutor(max_workers=WB_WORKERS) as ex:
        futs = {ex.submit(wb, u): u for u in urls}
        for f in as_completed(futs):
            u = futs[f]
            done += 1
            try:
                wb_url, wb_ts = f.result()
            except Exception as e:
                wb_url, wb_ts = None, f"err:{type(e).__name__}"
            out[u]["wayback"] = wb_url
            out[u]["wayback_ts"] = wb_ts
            with _wb_lock:
                print(f"[wb {done}/{n}] {'Y' if wb_url else 'N'} {u[:80]}",
                      file=sys.stderr, flush=True)

    for rec in out.values():
        rec.pop("_kws", None)
    json.dump(out, open(out_path, "w"), indent=1, ensure_ascii=False)
    blank = sum(1 for r in out.values() if not r.get("wayback"))
    print(f"wrote {out_path}: {n} URLs, {blank} with no availability hit "
          f"(wb_fill.py resolves those properly)", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
