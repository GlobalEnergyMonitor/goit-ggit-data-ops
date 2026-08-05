#!/usr/bin/env python3
"""US wave 6 -- second-pass validation for the snapshots the first pass could not
read. Writes deep_validate_us.json; run after retry_snaps.py.

Three reasons a real capture scores 0 hits in validate_us_snaps.py, none of which
mean the snapshot is bad:

  PDF   the body is `%PDF-...`, so tag-stripping yields binary noise. Handled
        here by piping the bytes through `pdftotext -layout -`.
  shell the publisher renders client-side, so the capture is a stub. Nothing to
        be done -- these are reported as SHELL and go to human review.
  short  the citing sentence is short, so `want` had only 3-4 usable words and a
        genuine match still scores 1/4.

For each candidate this prints the sentence being supported next to the strings
actually found in the document, so the second gate -- does this source support
*this* claim -- is decided on quoted text rather than on a hit count.

One consumer, 8 s apart. See validate_us_snaps.py for why that matters.
"""
import json
import re
import subprocess
import sys
import time

import requests

import validate_us_snaps as V

# url -> extra literal strings to look for, drawn from the wiki sentence. A hit
# count cannot settle the second gate; a quoted figure can.
PROBE = {
    "http://columbiariverkeeper.org/wp-content/uploads/2015/02/"
    "2015.1.16-ODFW-Corps-OLNG-JPA-final.pdf":
        ["Oregon LNG", "FERC", "2008", "application"],
    "http://www.w-advisory.com/kunianinterview.pdf":
        ["Kunian", "Eos", "FERC", "2015", "filing"],
    "https://www.gasworld.com/global-lng-services-launches-new-solution/"
    "2016947.article": ["Main Pass", "MPEH", "48", "MTPA", "export"],
    # note the page's own spelling: "brownville", not "brownsville"
    "https://www.nsenergybusiness.com/projects/annova-lng-export-terminal-"
    "brownville-texas/": ["six", "trains", "production", "mtpa"],
}


def text_of(resp):
    """Returns (kind, text). kind is 'pdf', 'html' or 'shell'."""
    if resp.content[:5] == b"%PDF-" or "pdf" in \
            resp.headers.get("content-type", "").lower():
        try:
            p = subprocess.run(["pdftotext", "-layout", "-", "-"],
                               input=resp.content, capture_output=True,
                               timeout=120)
            return "pdf", p.stdout.decode("utf-8", "replace")
        except Exception as e:
            return "pdf", f"__PDFTOTEXT_FAILED__ {e!r}"
    body = V.strip(resp.text)
    return ("shell" if len(body) < 400 else "html"), body


def main(argv):
    rows = {r["url"]: r for r in json.load(open("validate_us_snaps.json"))}
    urls = [u for u in PROBE if u in rows] or list(PROBE)
    missing = [u for u in PROBE if u not in rows]
    for u in missing:
        print(f"WARN not in validate_us_snaps.json: {u}", file=sys.stderr)

    out = []
    for i, u in enumerate(urls, 1):
        row = rows[u]
        snap = row["snapshot"]
        try:
            resp = requests.get(snap, headers={"User-Agent": V.UA}, timeout=120)
            kind, body = text_of(resp)
            low = body.lower()
            found = {p: (p.lower() in low) for p in PROBE[u]}
            # a couple of hundred chars around the first probe hit, so the
            # sentence can be read rather than inferred from a boolean
            quote = ""
            for p in PROBE[u]:
                m = re.search(re.escape(p), body, re.I)
                if m:
                    quote = V.WS.sub(" ", body[max(0, m.start() - 160):
                                               m.start() + 320]).strip()
                    break
            rec = {"url": u, "snapshot": snap, "pages": row.get("pages"),
                   "context": row.get("context"), "kind": kind,
                   "status": resp.status_code, "chars": len(body),
                   "found": found, "quote": quote}
        except Exception as e:
            rec = {"url": u, "snapshot": snap, "pages": row.get("pages"),
                   "context": row.get("context"), "kind": "ERR",
                   "status": "ERR", "error": repr(e), "found": {}, "quote": ""}
        out.append(rec)
        hit = "".join("Y" if v else "." for v in rec["found"].values())
        print(f'{i}/{len(urls)}  {rec["kind"]:5} {str(rec["status"]):>4} '
              f'{rec["chars"] if "chars" in rec else 0:>7}c  [{hit}]  '
              f'{u[:58]}', flush=True)
        json.dump(out, open("deep_validate_us.json", "w"), indent=1,
                  ensure_ascii=False)
        time.sleep(8)

    print("\n--- read these before accepting ---")
    for r in out:
        print("=" * 68)
        print((r["pages"] or ["?"])[0])
        print("CLAIM:", (r.get("context") or [""])[0][:220])
        print("FOUND:", r["found"])
        print("QUOTE:", r["quote"][:420] or "(none)")


if __name__ == "__main__":
    main(sys.argv[1:])
