#!/usr/bin/env python3
"""US batch, step 5 wave 3 -- the trade-press relocations that survived the
batch-collision adjudication, plus the three abarrelfull re-sourcings.

  python3 fix_us_wave3.py            # build + print every old->new pair
  python3 fix_us_wave3.py --save     # build, then guarded_save each page

Two groups, two provenances:

PRESS -- reloc_press_b.json. Four subagent batches were mistakenly pointed at
one output path and clobbered each other; the parent agent independently
re-verified all 24 rows and produced this file, and every RELOCATED row here was
then fetched again by hand (status, headline, and one specific fact from the
cited sentence). Where two agents disagreed -- savannahnow -- the Gannett
/story/ URL is the one that actually resolves.

ABF -- resource_abf_us.json. abarrelfull.wikidot.com is a wiki mirror, not a
source, so these are not relocations: the claim has to be re-sourced to the
primary document. All three replacements were read in full (`pdftotext -layout`
for the DOE order, tag-stripped HTML for the two SEC filings) and the sentence
supporting the wiki claim is quoted in EVIDENCE below.

Ingleside is deliberately a PARTIAL: the Oxy 8-K covers the import-terminal half
of the sentence and nothing covers the export-resubmission half. The citation
still improves -- a primary filing replacing a mirror -- but the gap is real and
goes to HUMAN-REVIEW.md rather than being papered over.
"""
import json
import os
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

OUTDIR = "us_wiki"

SUMMARY = {
    "press": "update moved trade-press article links",
    "abf": "replace a barrel full wiki mirror citation with the primary source",
}

# Same dead url defined by more than one editable ref on the page, so find_ref
# would refuse the marker by design. Elba Island: 4x <ref name=mar2> plus 1
# unnamed, all byte-identical. Commonwealth: 2x byte-identical unnamed refs.
SWAP_ALL = {
    "http://savannahnow.com/news/2015-10-16/kinder-morgan-construction-plans-"
    "elba-include-10000-trucks-month",
    "https://finance.yahoo.com/news/commonwealth-lng-gunvor-singapore-pte-"
    "160300050.html",
}

# Fixes that are not url swaps, appended after the url swap for that page.
# The Gunvor release is the primary document the Yahoo wire item was carrying,
# so once the url points at gunvorgroup.com the trailing "Yahoo Finance"
# attribution names the wrong publisher and has to move with it.
EXTRA = {
    "Commonwealth LNG Terminal": [
        ("press attrib", None,
         ("swap_all", "Yahoo Finance, June 12, 2019",
          "Gunvor Group, June 12, 2019")),
    ],
}

# page -> (marker for the dead mirror ref, replacement ref). Keyed by page rather
# than url because resource_abf_us.json records the *replacement* url, not the
# mirror being removed, so the marker cannot be read off the row. Two of the
# three mirrors are bit.ly-shortened and one is a bare wikidot url; each marker
# below was confirmed to hit exactly one non-autoref ref on its page (the other
# occurrences are all inside bot-owned autoref_* refs in the data tables, which
# find_ref filters out and this project must not touch).
#
# EVIDENCE, verified against the fetched document:
#
# Casotte Landing -- Chevron FY2007 10-K, filed 2008-02-28: "Chevron also
#   continued the federal, state and local permitting process during 2007 and
#   early 2008 for a proposed natural gas import terminal at Casotte Landing in
#   Jackson County, Mississippi. In February 2007, the company received approval
#   from the Federal Energy Regulatory Commission for the proposed terminal."
#   Covers the wiki claim (FERC approval, 2007) in full.
#
# Rio Grande -- DOE/FE Order No. 3869, 2016-08-17: "the project will have six
#   liquefaction trains with an aggregate production capacity of around 27 MPTA"
#   ("MPTA" is DOE's own typo) and trains "each capable of producing
#   approximately 4.5 million tonnes per annum (MTPA)". Covers 6 x 4.5 = 27 mtpa
#   in full.
#
# Ingleside -- Occidental 8-K Exhibit 99.1, 2005-09-07: "Ingleside, Texas LNG
#   Terminal ... FERC Approval Granted in Late July. $450 Million LNG Receiving
#   Terminal and Related 26-Mile Pipeline." Covers the import-terminal half of
#   the claim only -- see HUMAN-REVIEW.md.
ABF = {
    # unnamed ref -> stays unnamed
    "Casotte Landing LNG Terminal": (
        "bit.ly/2mKvdIn",
        '<ref>Chevron Corporation, [https://www.sec.gov/Archives/edgar/data/'
        '93410/000095013408003672/f37829e10vk.htm "Form 10-K for the fiscal '
        'year ended December 31, 2007,"] U.S. Securities and Exchange '
        'Commission, February 28, 2008.</ref>'),
    # unnamed ref -> stays unnamed
    "Rio Grande LNG Terminal": (
        "abarrelfull.wikidot.com",
        '<ref>U.S. Department of Energy, Office of Fossil Energy, '
        '[https://www.energy.gov/sites/prod/files/2016/08/f33/ord3869.pdf '
        '"Order Granting Long-Term, Multi-Contract Authorization to Export '
        'Liquefied Natural Gas by Vessel from the Proposed Rio Grande LNG '
        'Terminal in Brownsville, Texas, to Free Trade Agreement Nations,"] '
        'DOE/FE Order No. 3869, FE Docket No. 15-190-LNG, August 17, '
        '2016.</ref>'),
    # name=bfull is never reused self-closing on this page (only autoref_1 is),
    # so rewriting the definition in place is safe; the name is kept to hold the
    # churn down.
    "Ingleside Energy LNG Terminal": (
        "bit.ly/2ncgxVg",
        '<ref name=bfull>Occidental Petroleum Corporation, '
        '[https://www.sec.gov/Archives/edgar/data/797468/000079746805000131/'
        'exhibit991-20050907.htm "Investor Presentation, Lehman Brothers 19th '
        'Annual CEO Energy/Power Conference,"] Exhibit 99.1 to Form 8-K, U.S. '
        'Securities and Exchange Commission, September 7, 2005.</ref>'),
}


def main(argv):
    save = "--save" in argv
    fixes, classes = {}, {}

    def add(page, cls, fix):
        fixes.setdefault(page, []).append(fix)
        classes.setdefault(page, set()).add(cls)

    for r in json.load(open("reloc_press_b.json")):
        if r.get("verdict") != "RELOCATED":
            continue
        url, new = r["url"], r["replacement"]
        for page in dict.fromkeys(r.get("pages") or []):
            act = ("swap_all", url, new) if url in SWAP_ALL \
                else ("swap", url, new)
            add(page, "press", ("press reloc", url, act))
    for page, extra in EXTRA.items():
        for fix in extra:
            add(page, "press", fix)

    for r in json.load(open("resource_abf_us.json")):
        page = r["page"]
        if page not in ABF:
            raise SystemExit(f"no replacement ref authored for {page!r}")
        marker, new_ref = ABF[page]
        add(page, "abf", ("abf resource", marker, ("full", new_ref)))

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
        summ = "background: " + "; ".join(SUMMARY[c]
                                         for c in sorted(classes[page]))
        res = fixlib.guarded_save(s, page, *diffs[page], summary=summ)
        if res:
            errs = fixlib.cite_errors(s, page)
            print(f"  cite errors: {errs}"
                  + ("  <-- INVESTIGATE" if errs else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
