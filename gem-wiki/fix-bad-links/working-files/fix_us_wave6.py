#!/usr/bin/env python3
"""US batch, step 5 wave 6 -- the content-validated Wayback swaps.

  python3 fix_us_wave6.py            # build + print every old->new pair
  python3 fix_us_wave6.py --save     # build, then guarded_save each page

Input is wave6_accept.json, which is the 22 survivors of a four-stage filter
over the 118-url archive queue. The filtering is the substance of this wave, so
it is worth stating what each stage removed:

  1. still-on-page   Every citing page was re-fetched from the wiki and the url
                     tested for continued presence. 6 of 118 were already gone,
                     repaired by waves 1-5; the queue was built before them.
  2. throttle retry  3 passes took THROTTLED from 39 -> 17 -> 13. A throttled
                     archive.org lookup is indistinguishable from "never
                     archived" and must never be recorded as one. 8 of the
                     surviving 13 are 401/403 bot walls whose refs need no
                     repair at all, so their archive status is moot.
  3. content check   Every candidate snapshot was fetched and scored against
                     words from the citing sentence (validate_us_snaps.py). A
                     Wayback 200 is not evidence: this pass caught a capture of
                     a 404 page, a paywall interstitial, three JS shells, a
                     different article at the same url, and -- the reason this
                     stage exists -- a *domain squat*, where energyportal.eu had
                     become a Greek sports-betting site and Wayback had
                     faithfully captured the spam.
  4. deep check      PDFs and short-sentence cases that stage 3 could not read
                     (deep_validate_us.py, pdftotext for the PDFs). Rescued Eos
                     and Annova; confirmed the gasworld paywall rejection.

Second gate. For a faithful archive capture of the *same* url the editor cited,
the gate is satisfied by construction -- it is that document, as cited. That is
why these are the safest class in the project and why the work went into proving
the capture really is the document. Where a capture turned out to be something
else, it is in wave6_reject.json with the reason, so a later pass cannot
silently re-accept it.

One claim-vs-source gap found and NOT papered over: Oregon LNG's ODFW pdf is a
genuine capture of the cited document, but the document is comments on an Army
Corps Clean Water Act permit application and never mentions FERC, while the
sentence claims a formal FERC application in October 2008. The link repair is
still right; the sourcing gap goes to HUMAN-REVIEW.md as a researcher item.

Mechanics: the swap merges rather than replaces. For {{cite}} templates the dead
url stays in url= and the snapshot goes to archive-url/archive-date/
url-status=dead -- provenance is kept and it renders correctly. Bare [url text]
links have nowhere to put it, so there the url is replaced outright, which loses
nothing because a Wayback url embeds the original it captured. That logic is
fix_latam_small.apply_archive, reused here rather than reimplemented.
"""
import json
import os
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402
from fix_latam_small import apply_archive, find_ref_by_url  # noqa: E402
from scan_background_refs import URL_RE  # noqa: E402

OUTDIR = "us_wiki_w6"
SRC = "wave6_accept.json"
SUMMARY = "background: point dead citation links at archived copies"


def editable_refs(text, url):
    """Every non-autoref ref whose extracted urls include exactly `url`.

    find_ref_by_url refuses a url cited by more than one editable ref, which is
    right for a *relocation* -- wave 4's Port Arthur case proved that two refs
    sharing a shortlink can have claims that do not both survive the move. An
    archive swap is different in kind: it points at the same document the ref
    already cites, so it is claim-neutral and every citing ref can take it. Two
    urls here need this (Oxnard x3, the Sabine Pass Bloomberg piece x4).

    Deliberately equality-on-extracted-urls, not substring, for the reason
    find_ref_by_url gives: one cited url is often a prefix of another.
    """
    out = []
    for m in fixlib.REF_RE.finditer(text):
        ref = m.group(0)
        if "autoref_" in ref[:40]:
            continue
        # same rstrip as find_ref_by_url, so the two agree on what "cites" means
        if url in [u.rstrip(".,);") for u in URL_RE.findall(ref)]:
            out.append(ref)
    return out


def main(argv):
    save = "--save" in argv
    diag = json.load(open("diag_us.json"))
    accept = json.load(open(SRC))

    s = gw.session()
    fixes, skipped = {}, []
    for row in accept:
        url, snap = row["url"], row["snapshot"]
        pages = sorted({c[1] for c in (diag[url].get("cites") or [])})
        for page in pages:
            text = gw.page_text(s, page)
            # find_ref_by_url excludes autoref_* by design and exits when that
            # leaves nothing. That is a legitimate outcome here, not an error:
            # the archive queue was seeded from a page-wide url scan, so it
            # carries urls whose ONLY citation is a bot-owned autoref in the
            # ownership/timeline tables (bit.ly/2mJLxsQ on Bienville FSRU is
            # one). Those are out of scope -- the tracker bot rewrites them --
            # so record and move on rather than abort the wave.
            try:
                refs = [find_ref_by_url(text, url)]
            except SystemExit as e:
                refs = editable_refs(text, url)
                if not refs:
                    skipped.append((page, url, f"not in an editable ref ({e})"))
                    continue
                # More than one editable ref cites this url. Oxnard's three are
                # byte-identical, so a ref-text marker cannot pick one out; and
                # every ref in both multi-ref cases is a bare [url text] link,
                # for which apply_archive's whole action IS replacing the url.
                # swap_all does exactly that across all non-autoref refs and
                # nowhere else, so use it instead of per-ref markers. A cite
                # template here would need fields added rather than a url
                # rewritten, which swap_all cannot express -- refuse loudly
                # rather than half-apply it.
                if any("{{" in r for r in refs):
                    skipped.append((page, url, f"{len(refs)} refs incl. a cite "
                                    "template; needs per-ref handling"))
                    continue
                fixes.setdefault(page, []).append(
                    (f"archive x{len(refs)}", None,
                     ("swap_all", url, snap)))
                continue
            for ref in refs:
                if ref is None:
                    skipped.append((page, url, "no unique non-autoref ref"))
                    continue
                new_ref = apply_archive(ref, url, snap)
                if new_ref is None:
                    skipped.append((page, url,
                                    "ref already carries an archive-url"))
                    continue
                fixes.setdefault(page, []).append(
                    ("archive", ref, ("full", new_ref)))

    n = sum(len(v) for v in fixes.values())
    print(f"{len(fixes)} pages, {n} fixes", file=sys.stderr)
    for page, url, why in skipped:
        print(f"SKIP {page}: {why}\n     {url}", file=sys.stderr)

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
