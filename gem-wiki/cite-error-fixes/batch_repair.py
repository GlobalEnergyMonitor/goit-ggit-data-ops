"""Batch orphaned-ref repair over flagged gem.wiki pages, with per-page gates + CSV log."""
import csv
import json
import sys
import time
import urllib.parse

from repair_orphan_refs import build_repair, save_edit, orphan_names
from wiki_session import WikiSession

import glob

RESULTS = "cite_error_results.json"
DONE_TITLES = {
    "Lake Charles LNG Terminal", "Coral North FLNG Terminal", "Kollsnes LNG Terminal",
    "Kenai LNG Terminal", "Inkoo FSRU", "UTM Offshore FLNG Terminal",
    "Huizhou LNG Terminal", "Texas GulfLink Deepwater Port",
    "Main Pass Energy Hub FLNG Terminal", "Rio Grande LNG Terminal",
    "Jaigarh LNG Terminal",
    # fixed individually after the insertions-only gate rewrite
    "Świnoujście Polskie LNG Terminal", "Ahlone LNG Terminal",
}
# every title already attempted in a previous batch (fixed OR queued for manual)
for _log in glob.glob("batch*_log.csv"):
    with open(_log) as _f:
        DONE_TITLES.update(row["title"] for row in csv.DictReader(_f))


def url_to_title(url):
    return urllib.parse.unquote(url.split("gem.wiki/")[1]).replace("_", " ")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    log_path = sys.argv[2] if len(sys.argv) > 2 else "batch_repair_log.csv"
    d = json.load(open(RESULTS))
    flagged = [r for r in d["results"] if r.get("cite_error_count")]
    titles = [url_to_title(r["url"]) for r in flagged]
    todo = [t for t in titles if t not in DONE_TITLES][:n]
    print(f"{len(todo)} pages queued", flush=True)

    s = WikiSession()
    s.login()

    rows = []
    fixed = skipped = failed = 0
    for i, title in enumerate(todo, 1):
        row = {"title": title, "action": "", "detail": "", "revid": "",
               "errors_before": "", "errors_after": ""}
        try:
            r = build_repair(s, title)
            if r.get("skip"):
                row["action"] = "skipped"
                row["detail"] = r["skip"] + (
                    "; " + "; ".join(f"{n_}:{why}" for n_, why in r.get("failures", []))
                    if r.get("failures") else "")
                skipped += 1
            elif r["preview_cite_errors"] != 0:
                row["action"] = "skipped"
                row["detail"] = f"preview_still_has_{r['preview_cite_errors']}_errors"
                skipped += 1
            else:
                row["errors_before"] = r["live_cite_errors"]
                res = save_edit(s, r)
                e = res.get("edit", {})
                if e.get("result") == "Success":
                    live = s.call(action="parse", page=title, prop="text")
                    after = live["parse"]["text"]["*"].count("mw-ext-cite-error")
                    row.update(action="fixed", revid=e.get("newrevid"),
                               errors_after=after,
                               detail=f"{len(r['plan'])} defs restored")
                    fixed += 1
                else:
                    row.update(action="edit_failed", detail=json.dumps(res)[:200])
                    failed += 1
                time.sleep(5)
        except Exception as ex:
            row.update(action="error", detail=f"{type(ex).__name__}: {ex}"[:200])
            failed += 1
            time.sleep(5)
        rows.append(row)
        print(f"[{i}/{len(todo)}] {row['action']:12s} {title}  {row['detail']}", flush=True)

    with open(log_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nfixed={fixed} skipped={skipped} failed={failed}  log={log_path}", flush=True)


if __name__ == "__main__":
    main()
