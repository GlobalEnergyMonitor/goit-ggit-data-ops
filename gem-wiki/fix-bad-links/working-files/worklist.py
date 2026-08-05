#!/usr/bin/env python3
"""Join a scan_*.json against the diag_*.json files into a per-page worklist.

The scan says what is wrong; the diagnosis says what a browser-headed retry and
the Wayback lookup found. Repair decisions need both in one view, per page, in
ref order — that is all this prints.

  python3 worklist.py scan_italy.json > worklist_italy.txt
  python3 worklist.py -d diag_us.json scan_us.json > worklist_us.txt

`-d` may be repeated; with no `-d` the historical ISG diag set below is used.

A shortlink is diagnosed twice: `diag_<batch>` keys it by the `bit.ly/...` the
wikitext carries, `diag_shortlink_targets` by the URL it resolves to, and only
the second one has the archive. So both records are consulted and the one that
actually found a snapshot wins — keying on the wikitext URL alone reports every
shortlink as unarchived.
"""
import json
import sys

DIAGS = ("diag_itesx.json", "diag_shortlink_targets.json", "diag_germany.json")


def best(diag, *urls):
    """The diagnosis record for a ref, preferring one that resolved an archive."""
    recs = [dict(diag[u], _key=u) for u in urls if u and u in diag]
    for r in recs:
        wb = r.get("wayback")
        if wb and wb != "THROTTLED":
            return r
    return recs[0] if recs else {}


def main(argv):
    diags, rest = [], []
    i = 0
    while i < len(argv):
        if argv[i] == "-d":
            diags.append(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    argv = rest
    diag = {}
    for f in (diags or DIAGS):
        try:
            diag.update(json.load(open(f)))
        except FileNotFoundError:
            pass
    ver = {}
    try:
        for line in open("verify_snaps_cache.jsonl"):
            if line.strip():
                r = json.loads(line)
                ver[r["url"]] = r
    except FileNotFoundError:
        pass
    for path in argv:
        for page, rep in json.load(open(path)).items():
            rows = [r for r in rep.get("results", [])
                    if r.get("url") and (r["verdict"] != "OK" or r.get("flags"))]
            if not rows:
                continue
            print(f"\n===== {page}  (refs={rep['refs']})")
            for r in rows:
                u = r["url"]
                dg = best(diag, u, r.get("final_url"),
                          (diag.get(u) or {}).get("final_url"))
                print(f" [{r['n']:>2}] {r['verdict']:9} http={r.get('status')} "
                      f"retry={dg.get('retry_status')} flags={r.get('flags')}")
                print(f"      url: {u}")
                if r.get("final_url") and r["final_url"] != u:
                    print(f"      ->   {r['final_url']}")
                if dg.get("wayback"):
                    v = ver.get(dg.get("_key") or "") or {}
                    tag = f"[{v['result']}: {v.get('why','')[:50]}] " if v else ""
                    print(f"      wb:  {tag}{dg['wayback']}")
                if r.get("context"):
                    print(f"      ctx: {r['context'][:200]}")


if __name__ == "__main__":
    main(sys.argv[1:])
