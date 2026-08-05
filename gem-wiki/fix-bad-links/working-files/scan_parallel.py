#!/usr/bin/env python3
"""Thread-parallel wrapper around scan_background_refs.scan_page.

Usage:
  python3 scan_parallel.py pages.json out.json [workers]

`pages.json` is a JSON list of page titles (build it from the GEM export's
`Wiki` column ∪ the wiki category — see README step 1).

Why this exists: scan_background_refs.py walks pages serially, which is fine
for a 6-page country and hopeless for the 108-page US batch. The per-ref HTTP
checks hit hundreds of *different* publisher hosts, so they parallelize
cleanly — this is NOT the archive.org path, which the README caps at three
consumers total. Keep archive.org work in wb_fill/cdx_* where that cap lives.

Each worker gets its own requests.Session (gemwiki.session() is not shared
across threads). Output is the same {title: report} JSON that
scan_background_refs.py writes, so every downstream tool (diagnose_flags,
worklist, dump_refs) consumes it unchanged.
"""
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, sys.path[0] + "/../..")
import gemwiki as gw
import scan_background_refs as sbr

_local = threading.local()


def _session():
    s = getattr(_local, "s", None)
    if s is None:
        s = _local.s = gw.session()
    return s


def main(args):
    pages_path, out_path = args[0], args[1]
    workers = int(args[2]) if len(args) > 2 else 8
    titles = json.load(open(pages_path))
    report, errors = {}, {}
    done = 0

    def work(t):
        return t, sbr.scan_page(_session(), t)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(work, t): t for t in titles}
        for f in as_completed(futs):
            t = futs[f]
            done += 1
            try:
                _, rep = f.result()
                report[t] = rep
            except Exception as e:                      # keep going; report at end
                errors[t] = f"{type(e).__name__}: {e}"
            print(f"[{done}/{len(titles)}] {t}", file=sys.stderr, flush=True)

    json.dump(report, open(out_path, "w"), indent=1, ensure_ascii=False)
    # pages with no Background section come back as {"error": ...} — no 'refs'
    noback = [t for t, r in report.items() if "refs" not in r]
    print(f"\nwrote {out_path}: {len(report)} pages, "
          f"{sum(r.get('refs', 0) for r in report.values())} refs, "
          f"{len(noback)} with no Background section", file=sys.stderr)
    if errors:
        print(f"FAILED {len(errors)} pages:", file=sys.stderr)
        for t, e in errors.items():
            print(f"  {t}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
