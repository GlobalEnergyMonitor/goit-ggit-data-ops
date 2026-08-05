#!/usr/bin/env python3
"""US batch, step 5 wave 5 -- the 11 MALFORMED refs' 7 in-scope wikilink refs.

  python3 fix_us_wave5.py            # build + print every old->new pair
  python3 fix_us_wave5.py --save     # build, then guarded_save each page

These are a different defect from everything else in this project, and worth
being precise about: they are NOT dead links. They have no url at all, and never
did. Each one carries complete bibliographic data -- author, headline, publisher,
date -- with the *headline* wrapped in `[[...]]`, MediaWiki's syntax for an
internal link to another wiki page. All seven targets were checked against the
API and all seven are missing, so today each ref renders as a red link inviting a
reader to create a GEM.wiki page named after a news headline. That is worse than
an unlinked citation: it looks like an internal cross-reference to something that
should exist here.

The repair is to delete the four bracket characters and nothing else. What is
left is a complete, valid, unlinked citation -- which is ordinary practice, and
is exactly what the citing editor's own text already says. No sourcing judgment
is involved, no claim changes, and nothing is asserted that was not already
asserted. It is also trivially reversible.

Deliberately NOT done here: turning these into external links. Two of the seven
have candidate urls (S&P Global for Corpus Christi, Reuters for the Plaquemines
Shell deal) that two independent agents converged on -- one by URL-pattern
inference, one by decoding the Google News redirect -- but both hosts bot-wall,
and a 401/403 is never a confirmation in this project. Bloomberg likewise for the
CNOOC piece. Those upgrades need a human with a browser and are queued in
HUMAN-REVIEW.md; the un-bracketing below does not depend on them and does not
foreclose them.

Out of scope, left alone: the other 4 of the 11 MALFORMED refs are offline/print
citations (BloombergNEF on Main Pass Energy Hub, E&E's Northey on Cameron, The
Oregonian's Sickinger x2 on Oregon LNG) with no url to repair.
"""
import json
import os
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

OUTDIR = "us_wiki"
SRC = "dossier_us/malformed.json"
SUMMARY = ("background: unbracket citation headlines that render as red "
           "wikilinks")


def main(argv):
    save = "--save" in argv
    fixes = {}
    for r in json.load(open(SRC)):
        ref = r["ref"]
        if "[[" not in ref:
            continue
        new_ref = ref.replace("[[", "").replace("]]", "")
        # the whole ref text is the marker: it is what makes this ref unique on
        # the page, and Plaquemines carries three of these.
        fixes.setdefault(r["page"], []).append(
            ("unbracket", ref, ("full", new_ref)))

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
