#!/usr/bin/env python3
"""US batch, step 5 -- the three mechanical repair classes from mech_us.json.

  python3 fix_us_mech.py            # build + print every old->new pair
  python3 fix_us_mech.py --save     # build, then guarded_save each page

Classes, all decided in step 4 and none needing further research:

  giignl-cdn        15 refs / 10 pages. giignl.org's own report PDFs are all
                    404; the reports live on the Webflow CDN (fixlib.G20XX,
                    each verified 200 application/pdf). Rebuilt in the standard
                    format via fixlib.giignl() so the ref names the report and
                    year rather than a bare CDN hash -- the ref name and any
                    page number are lifted off the existing ref, not retyped.
  lngworldnews      19 refs / 18 pages. lngworldnews.com folded into
                    offshore-energy.biz keeping the slug; every replacement in
                    reloc_lngworldnews.json was fetched and headline-matched.
  abarrelfull-drop  24 refs / 24 pages. abarrelfull.wikidot.com is a banned
                    source (a wiki mirror, not a source) -- established by the
                    2026-07-28 ISG batch, where it was dropped outright rather
                    than de-shortlinked. Each of these supports only the
                    definitional lead sentence, which the page's own tracker
                    infobox documents.

Deliberately NOT here -- three abarrelfull refs carry a substantive claim, so
dropping them would strand it. They go to re-sourcing / HUMAN-REVIEW.md:
Casotte Landing (FERC approval 2007), Ingleside Energy (import->export
history), Rio Grande (original 6 x 4.5 mtpa train plan).
"""
import json
import os
import re
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

ACCESSED = "July 28, 2026"
OUTDIR = "us_wiki"

_TEXT = {}


def page_text(s, title):
    """One fetch per page, not one per ref."""
    if title not in _TEXT:
        _TEXT[title] = gw.page_text(s, title)
    return _TEXT[title]

# dead giignl.org path fragment -> (CDN url, report year)
GIIGNL = {
    "giignl_-_2020_annual_report_-_04082020.pdf": (fixlib.G2020, 2020),
    "GIIGNL2022_Annual_Report_May24.pdf": (fixlib.G2022, 2022),
    "GIIGNL-2023-Annual-Report-July20.pdf": (fixlib.G2023, 2023),
    "GIIGNL-2024-Annual-Report-1.pdf": (fixlib.G2024, 2024),
}

# abarrelfull refs whose claim outlives the ref -- excluded from the drop
KEEP_FOR_RESOURCING = {"Casotte Landing LNG Terminal",
                       "Ingleside Energy LNG Terminal"}

# the same dead url is defined by two identical <ref name="s1"> on this page
SWAP_ALL = {("CE FLNG Terminal",
             "http://www.lngworldnews.com/ferc-questions-ce-flng-projects-viability/")}

SUMMARY = {
    "giignl": "update dead giignl annual report links to the current pdfs",
    "lngwn": "lng world news links moved to offshore-energy.biz",
    "abf": "drop dead a barrel full wiki-mirror citations",
}


def giignl_fix(s, page, url):
    """(label, marker, action) rebuilding a giignl ref in the standard format,
    carrying over the existing ref's name and page number."""
    frag = next(f for f in GIIGNL if f in url)
    cdn, year = GIIGNL[frag]
    ref = fixlib.find_ref(page_text(s, page), url)
    name = re.search(r'name\s*=\s*"?([^"\s>]+)"?', ref)
    pg = re.search(r"page (\d+)", ref)
    return (f"giignl {year} -> cdn", url,
            ("full", fixlib.giignl(cdn, year,
                                   name=name.group(1) if name else None,
                                   page=int(pg.group(1)) if pg else None,
                                   accessed=ACCESSED)))


def main(argv):
    save = "--save" in argv
    mech = json.load(open("mech_us.json"))
    reloc = json.load(open("reloc_lngworldnews.json"))
    s = gw.session()

    fixes, classes = {}, {}
    for page, items in mech["giignl-cdn"].items():
        for _n, url in items:
            fixes.setdefault(page, []).append(giignl_fix(s, page, url))
            classes.setdefault(page, set()).add("giignl")

    for page, items in mech["lngworldnews-reloc"].items():
        seen = set()
        for _n, url in items:
            if url in seen:
                continue                     # one url, one edit, however cited
            seen.add(url)
            new_url = reloc[url]["cand"]
            act = "swap_all" if (page, url) in SWAP_ALL else "swap"
            fixes.setdefault(page, []).append(
                ("lngworldnews -> offshore-energy", url, (act, url, new_url)))
            classes.setdefault(page, set()).add("lngwn")

    for page, items in mech["abarrelfull-drop"].items():
        if page in KEEP_FOR_RESOURCING:
            print(f"SKIP (re-sourcing) {page}", file=sys.stderr)
            continue
        for _n, url in items:
            fixes.setdefault(page, []).append(
                ("drop banned abarrelfull mirror", url, ("drop",)))
            classes.setdefault(page, set()).add("abf")

    n = sum(len(v) for v in fixes.values())
    print(f"{len(fixes)} pages, {n} fixes\n", file=sys.stderr)

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
            print(f"  cite errors: {errs}" + ("  <-- INVESTIGATE" if errs else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
