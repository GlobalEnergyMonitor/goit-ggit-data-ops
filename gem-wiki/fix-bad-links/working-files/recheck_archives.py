"""Re-check the archive URLs that failed the first sweep -- much more slowly.

A *run* of consecutive failures is the rate-limit signature, not evidence that
nine snapshots died at once. Anything still failing after a 20 s gap and two
retries is a real negative; anything that comes back 200 was throttling and is
recorded as such, never as a dead capture.
"""
import json
import time

import requests

UA = "GEM research baird.langenbrunner@globalenergymonitor.org"
prev = json.load(open("new_archive_urls.check.jsonl"))
bad = [r for r in prev if r["status"] != 200]
print(f"re-checking {len(bad)} at 20 s intervals\n")
# The first sweep died on TCP `Connection refused` -- archive.org drops the
# connection outright rather than answering 429 -- so let the block lapse
# before knocking again, or every retry just re-arms it.
time.sleep(120)

fixed = {}
for i, rec in enumerate(bad, 1):
    u = rec["url"]
    for attempt in range(1, 4):
        try:
            r = requests.get(u, headers={"User-Agent": UA}, timeout=90)
            st, n, err = r.status_code, len(r.content), ""
        except Exception as e:
            st, n, err = "ERR", 0, repr(e)[:90]
        if st == 200:
            break
        time.sleep(20)
    fixed[u] = {"status": st, "bytes": n, "error": err}
    print(f'{i:2d}/{len(bad)}  {st}  {n:>8}  try{attempt}  {u[:100]}', flush=True)
    if err:
        print(f"        {err}", flush=True)
    time.sleep(20)

for rec in prev:
    if rec["url"] in fixed:
        rec.update(fixed[rec["url"]])
        rec["note"] = "first sweep failed on throttling; passed on re-check" \
            if rec["status"] == 200 else "failed twice -- real negative"
json.dump(prev, open("new_archive_urls.check.jsonl", "w"), indent=1)
still = [r for r in prev if r["status"] != 200]
print(f"\n{len(prev) - len(still)}/{len(prev)} OK")
for r in still:
    print("  FAIL", r["status"], r["url"])
