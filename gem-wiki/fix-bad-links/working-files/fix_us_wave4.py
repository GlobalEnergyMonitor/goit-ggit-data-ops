#!/usr/bin/env python3
"""US batch, step 5 wave 4 -- the resolved bit.ly shortlinks.

  python3 fix_us_wave4.py            # build + print every old->new pair
  python3 fix_us_wave4.py --save     # build, then guarded_save each page

17 bit.ly shortlinks were sitting in the archive.org queue, which was the wrong
queue: bit.ly is dead as a redirector but the refs still name a real publisher
and a real title, so the document can usually be re-found by title alone and
archive.org's scarce budget is never spent. 7 of 17 came back RELOCATED.

Five are pure de-shortlinks: the replacement is the identically-titled document
at its publisher's live url. For those the second gate is satisfied by
construction -- nothing about what the citation says or supports changes, only
the redirector in front of it. The two that point at *living corporate pages*
are the ones that needed reading, because a living page moves on from the
version an editor cited in 2017:

  Plaquemines  ACCEPT. Live page: "The approximately 630 acre site is located on
    the Mississippi River" -- supports the cited sentence. (The wiki says 632
    acres; Venture Global now rounds to 630. A currency note, not a link
    defect -- see HUMAN-REVIEW.md.)

  Port Arthur  SPLIT. The same shortlink is cited by two refs with different
    link text, and they do not both survive:
      "About Port Arthure LNG," -> identity sentence. Live Sempra page confirms
        a liquefaction/export terminal in Jefferson County, Texas. ACCEPT.
      "About Port Arthur LNG: Project Schedule," -> "expects to receive FERC
        approval and DOE non-FTA authorization in mid 2018, with operation in
        2023." The live page has no schedule section at all and now reports FID
        in March 2023 with Train 1 operating in 2027. NOT supported -> left
        alone here and queued for the 2017 Wayback capture instead.
    This is why the fix targets the ref by its link text rather than by url:
    swap_all would have quietly taken the Project Schedule ref with it.
"""
import json
import os
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

OUTDIR = "us_wiki"
SRC = "dossier_us/reloc_shortlinks.json"
SUMMARY = "background: replace dead bit.ly shortlinks with direct source links"

# url -> marker overriding the default (the url itself). Needed only where the
# url does not uniquely identify the ref being fixed.
MARKER = {
    # two refs share this shortlink; only the first one's claim survives
    "http://bit.ly/2niBu0B": "About Port Arthur LNG,]",
}

# url -> full replacement ref, where the publisher/access-date in the old ref
# would misdescribe the live page it now points at. The five not listed here are
# plain url swaps: same document, same publisher, same date, so the original
# provenance is left exactly as the citing editor wrote it.
FULL = {
    # was: "Venture Global Plaquemines LNG," Plaquemines LNG, accessed May 2017.
    # The publisher is Venture Global, not "Plaquemines LNG", and the access date
    # has to move with a live page rather than claim a 2017 reading of it.
    "http://bit.ly/2nOAgqI":
        '<ref>[https://ventureglobal.com/venture-global-plaquemines/ '
        '"Plaquemines,"] Venture Global, accessed July 28, 2026.</ref>',
    # was: "About Port Arthur LNG," Port Arthur LNG, accessed May 2017. Sempra
    # Infrastructure now hosts the project page under its own name.
    "http://bit.ly/2niBu0B":
        '<ref>[https://www.semprainfrastructure.com/port-arthur-lng "Port '
        'Arthur LNG,"] Sempra Infrastructure, accessed July 28, 2026.</ref>',
}

# url -> why it is not applied, so a later pass cannot silently re-accept it
REJECT = {}


def main(argv):
    save = "--save" in argv
    fixes = {}
    for r in json.load(open(SRC)):
        if r.get("verdict") != "RELOCATED":
            continue
        url, new = r["url"], r["replacement"]
        if url in REJECT:
            print(f"REJECT {url}\n       {REJECT[url]}", file=sys.stderr)
            continue
        marker = MARKER.get(url, url)
        act = ("full", FULL[url]) if url in FULL else ("swap", url, new)
        for page in dict.fromkeys(r.get("pages") or []):
            fixes.setdefault(page, []).append(("shortlink", marker, act))

    n = sum(len(v) for v in fixes.values())
    print(f"{len(fixes)} pages, {n} fixes\n", file=sys.stderr)

    s = gw.session()
    os.makedirs(OUTDIR, exist_ok=True)
    diffs = {p: fixlib.build(s, p, fx, outdir=OUTDIR)
             for p, fx in sorted(fixes.items())}
    if not save:
        return

    s = gw.session(login=True)
    for page in sorted(fixes):
        res = fixlib.guarded_save(s, page, *diffs[page], summary=SUMMARY)
        if res:
            errs = fixlib.cite_errors(s, page)
            print(f"  cite errors: {errs}"
                  + ("  <-- INVESTIGATE" if errs else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
