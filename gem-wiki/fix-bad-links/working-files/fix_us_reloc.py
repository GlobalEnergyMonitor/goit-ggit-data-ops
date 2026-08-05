#!/usr/bin/env python3
"""US batch, step 5 wave 2 -- the relocations the research agents found.

  python3 fix_us_reloc.py            # build + print every old->new pair
  python3 fix_us_reloc.py --save     # build, then guarded_save each page

Every RELOCATED row in SOURCES is applied *except* the URLs listed in REJECT.
The agents answered "is this the same document, live elsewhere?"; each row was
then re-read next to the paragraph it has to hold up (review_reloc.py) before
being left in. REJECT records the ones that failed that second gate, with the
reason, so a later pass doesn't silently re-accept them.

Three refs need more than a URL swap, because the replacement is a differently
titled document and a bare swap would leave the ref naming the wrong thing --
those are in FULL. One URL is cited by two refs on the same page, so it uses
swap_all (find_ref refuses a non-unique marker by design).
"""
import json
import os
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

OUTDIR = "us_wiki"
ACCESSED = "July 28, 2026"

# reloc file -> edit-summary class
SOURCES = {
    "reloc_company_a.json": "company",
    "reloc_company_b.json": "company",
    "dossier_us/reloc_govngo.json": "govngo",
    "dossier_us/reloc_press_a.json": "press",
}

SUMMARY = {
    "company": "update moved company project and press-release links",
    "govngo": "update moved agency and industry-report links",
    "press": "update moved trade-press article links",
}

REJECT = {
    # The wiki sentence describes "an early version" of the project -- four
    # floating trains, 13 mtpa. delfinmidstream.com/delfin-lng/ is the *current*
    # plan (three vessels, 13.2 mtpa), so it relocates cleanly but no longer
    # supports the sentence citing it. Needs the Aug-2017 capture instead.
    "http://www.delfinlng.com/":
        "live page describes the current plan, not the cited early version",
    # Not a dead link at all: the live ref already reads Elba_Island_(Georgia).
    # The url extractor stopped at the ')' in the wikilink, so the *extract* was
    # truncated, not the citation. Nothing to fix.
    "https://en.wikipedia.org/wiki/Elba_Island_(Georgia":
        "extractor artifact -- live ref already has the closing paren",
}

# url -> the same url is defined by more than one editable ref on the page
SWAP_ALL = {"http://www.txlng.com/theproject/project-overview.html"}

# (page, url) -> replacement ref text, for replacements whose document is titled
# differently enough that keeping the old link text would misname it
FULL = {
    # was: {{Cite web ... website=Nasdaq}}. Nasdaq dropped its wire archive; the
    # surviving copy is the Reuters original on Yahoo Finance, so the publisher
    # field has to change with the url.
    ("New Fortress Grand Isle FLNG Terminal",
     "https://www.nasdaq.com/articles/new-fortress-seeks-to-build-offshore-"
     "louisiana-lng-plant-by-q1-2023"):
        '<ref name=":0">{{Cite web|url=https://finance.yahoo.com/news/'
        '1-fortress-seeks-build-offshore-133249556.html|title=UPDATE 1-New '
        'Fortress seeks to build offshore Louisiana LNG plant by Q1 2023|last='
        '|first=|date=|website=Reuters via Yahoo Finance|url-status=live'
        '|archive-url=|archive-date=|access-date=2026-07-28}}</ref>',
    # was: "Freeport LNG Export project," a project page that no longer exists.
    # freeportlng.com/about/corporate-history carries the same DOE authorization
    # history, but it is a corporate-history page and must be named as one.
    ("Freeport LNG Terminal", "http://www.freeportlng.com/The_Project.asp"):
        '<ref name=free>[https://freeportlng.com/about/corporate-history '
        '"Corporate History,"] Freeport LNG, accessed ' + ACCESSED + '.</ref>',
    # was: bare link text "panhandleenergy.com". Panhandle's LNG expansion page
    # is gone; Energy Transfer's infopost PDF is the same terminal spec sheet and
    # states the cited 9.0 Bcf storage and 2.1 Bcf/d peak sendout.
    ("Lake Charles LNG Terminal",
     "http://www.panhandleenergy.com/expansion_lng.asp"):
        '<ref>[https://lclngmessenger.energytransfer.com/InfoPost/resources/'
        'documents/TLNGTerminal.pdf "Lake Charles LNG Overview,"] Energy '
        'Transfer, accessed ' + ACCESSED + '.</ref>',
}


def main(argv):
    save = "--save" in argv
    fixes, classes, skipped = {}, {}, []
    for path, cls in SOURCES.items():
        for r in json.load(open(path)):
            if r.get("verdict") != "RELOCATED":
                continue
            url, new = r["url"], r["replacement"]
            if url in REJECT:
                skipped.append((url, REJECT[url]))
                continue
            for page in dict.fromkeys(r.get("pages") or []):
                key = (page, url)
                if key in FULL:
                    act = ("full", FULL[key])
                elif url in SWAP_ALL:
                    act = ("swap_all", url, new)
                else:
                    act = ("swap", url, new)
                fixes.setdefault(page, []).append(
                    (f"{cls} reloc", url, act))
                classes.setdefault(page, set()).add(cls)

    for url, why in skipped:
        print(f"REJECT {url}\n       {why}", file=sys.stderr)
    n = sum(len(v) for v in fixes.values())
    print(f"\n{len(fixes)} pages, {n} fixes\n", file=sys.stderr)

    s = gw.session()
    os.makedirs(OUTDIR, exist_ok=True)
    diffs = {p: fixlib.build(s, p, fx, outdir=OUTDIR)
             for p, fx in sorted(fixes.items())}
    if not save:
        return

    s = gw.session(login=True)
    for page in sorted(fixes):
        summ = "background: " + "; ".join(SUMMARY[c]
                                         for c in sorted(classes[page]))
        res = fixlib.guarded_save(s, page, *diffs[page], summary=summ)
        if res:
            errs = fixlib.cite_errors(s, page)
            print(f"  cite errors: {errs}"
                  + ("  <-- INVESTIGATE" if errs else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
