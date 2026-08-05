#!/usr/bin/env python3
"""Helpers for building and saving Background-citation fixes.

A per-country fix run is a small throwaway script (working file, not
committed) shaped like:

    import fixlib, gemwiki as gw
    fixes = {
        "Krk FSRU": ("edit summary, all lowercase", [
            # (label, marker, action) — marker must identify exactly ONE
            # non-autoref <ref> in the page
            ("lngworldnews dead -> archive", "unique-url-fragment",
             ("swap", "http://old-url", "https://web.archive.org/...")),
            ("giignl 2023 -> standard format", "old-giignl-fragment",
             ("full", fixlib.giignl(fixlib.G2023, 2023, name=":2"))),
        ]),
    }
    s = gw.session()
    diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}
    # review the printed old->new pairs, then:
    s = gw.session(login=True)
    for t, (summ, fx) in fixes.items():
        fixlib.guarded_save(s, t, *diffs[t], summary=summ)

guarded_save re-fetches the live page and ABORTS if it changed since the
diff was built. After saving, run cite_errors() and require 0.
"""
import re
import sys

sys.path.insert(0, sys.path[0] + "/../..")
import gemwiki as gw

REF_RE = re.compile(r"<ref[^>/]*?(?:/>|>.*?</ref>)", re.DOTALL | re.IGNORECASE)

# GIIGNL annual report PDFs (Webflow CDN behind giignl.org/annual-report)
CDN = "https://cdn.prod.website-files.com/67bdb9fc993751711c5f54fd/"
G2020 = CDN + "67d40f92d6ed82e473b54f8e_GIIGNL-2020-Annual-Report.pdf"
G2021 = CDN + "67d40f93805223c8ccba8ef7_GIIGNL-2021-Annual-Report.pdf"
G2022 = CDN + "67d40f9112efb57309cae007_GIIGNL-2022-Annual-Report.pdf"
G2023 = CDN + "67d40f91fd8b5ad05589ef9e_GIIGNL-2023-Annual-Report.pdf"
G2024 = CDN + "6854051dda46281e5ec60285_GIIGNL%20Annual%20Report%202024.pdf"
G2025 = (CDN + "685278fda1e68e3b4324e2cf_0432365c1c5b8fb129ae8055cca8cb9b_"
         "%23GIIGNL%20-%20Livre%202025-20250610-Simple.pdf")


def giignl(year_url, year, name=None, page=None, accessed="July 21, 2026"):
    """Standard-format GIIGNL annual report ref."""
    nm = f' name="{name}"' if name else ""
    pg = f" (p {page})" if page else ""
    return (f"<ref{nm}>GIIGNL. [{year_url} The LNG Industry: GIIGNL Annual "
            f"Report {year}]{pg}. Accessed {accessed}.</ref>")


def find_ref(text, marker):
    """Return the unique non-autoref <ref>...</ref> containing marker."""
    hits = [m.group(0) for m in REF_RE.finditer(text) if marker in m.group(0)]
    hits = [h for h in hits if "autoref_" not in h[:40]]
    if len(hits) != 1:
        raise SystemExit(f"marker not unique ({len(hits)} hits): {marker!r}")
    return hits[0]


def drop_ref(text, ref):
    """Remove `ref` from `text`, closing the gap it leaves behind.

    Used for the drop-as-redundant repair and for banned sources (the
    abarrelfull/wikidot mirrors). Refuses a named ref that is reused
    elsewhere as `<ref name=x />`: removing the definition would turn every
    reuse into a cite error, which is exactly what the post-save check exists
    to catch -- better to fail here.
    """
    m = re.match(r'<ref\s+name\s*=\s*"?([^"\s>]+)"?\s*>', ref, re.I)
    if m:
        name = re.escape(m.group(1))
        reuses = re.findall(r'<ref\s+name\s*=\s*"?' + name + r'"?\s*/\s*>',
                            text, re.I)
        if reuses:
            raise SystemExit(f"ref name={m.group(1)!r} is reused {len(reuses)}x"
                             " -- move the definition instead of dropping it")
    i = text.index(ref)
    head, tail = text[:i], text[i + len(ref):]
    # A dropped ref usually sat between a sentence end and the next sentence, so
    # the removal leaves a double space (or a trailing space before a newline).
    # Only the seam is touched -- a page-wide whitespace pass would collapse the
    # aligned spacing wiki tables use.
    if head.endswith((" ", "\t")) and tail[:1] in (" ", "\t"):
        tail = tail.lstrip(" \t")
    stripped = tail.lstrip(" \t")
    if stripped[:1] in ("\n", ""):          # ref was last on its line
        head, tail = head.rstrip(" \t"), stripped
    return head + tail


def build(s, title, fixes, outdir="."):
    """Apply fixes to the live text; write <slug>_old/_new.wiki; return
    (old, new). Each fix: (label, marker, ("swap", old_url, new_url) |
    ("swap_all", old_url, new_url) | ("full", new_ref_text) | ("drop",))."""
    slug = re.sub(r"[ \-/]", "_", title)
    old = gw.page_text(s, title)
    new = old
    print("=" * 70)
    print(f"PAGE: {title}  ({len(fixes)} fixes)")
    for label, marker, action in fixes:
        if action[0] == "swap_all":
            # For a host migration where the SAME dead url is defined by more
            # than one <ref> on the page (find_ref would refuse it). Rewrites
            # the url inside every non-autoref ref and NOWHERE else: the same
            # url often also appears in an autoref in the ownership table, which
            # the tracker bot overwrites and this project must not touch.
            _, u_old, u_new = action
            hits = [m.group(0) for m in REF_RE.finditer(new)
                    if u_old in m.group(0) and "autoref_" not in m.group(0)[:40]]
            if not hits:
                raise SystemExit(f"url in no editable ref: {label}")
            for h in hits:
                new = new.replace(h, h.replace(u_old, u_new), 1)
            skipped = new.count(u_old)
            print(f"\n--- {label}\n  OLD: {u_old}\n  NEW: {u_new} "
                  f"({len(hits)} ref(s)" +
                  (f", {skipped} autoref occurrence(s) left alone)" if skipped
                   else ")"))
            continue
        ref = find_ref(new, marker)
        if new.count(ref) != 1:
            raise SystemExit(f"ref text not unique in page: {label}")
        if action[0] == "drop":
            new = drop_ref(new, ref)
            print(f"\n--- {label}\n  OLD: {ref[:400]}\n  NEW: (dropped)")
            continue
        if action[0] == "swap":
            _, u_old, u_new = action
            if u_old not in ref:
                raise SystemExit(f"url not in ref: {label}")
            new_ref = ref.replace(u_old, u_new)
        else:
            new_ref = action[1]
        new = new.replace(ref, new_ref, 1)
        print(f"\n--- {label}\n  OLD: {ref[:400]}\n  NEW: {new_ref[:400]}")
    with open(f"{outdir}/{slug}_old.wiki", "w") as f:
        f.write(old)
    with open(f"{outdir}/{slug}_new.wiki", "w") as f:
        f.write(new)
    print()
    return old, new


def build_prose(s, title, fixes, outdir="."):
    """Like build(), but for the prose itself rather than a <ref> span.

    Use ONLY for a claim the sources contradict outright -- a wrong date, a
    wrong figure -- where the citation is fine and the sentence is not. Every
    other kind of mismatch belongs in HUMAN-REVIEW.md; this is not a licence
    to rewrite text the tooling cannot verify.

    Each fix is (label, old_text, new_text). old_text must occur exactly once
    in the page, so quote enough of the sentence to be unambiguous -- the
    uniqueness check is the only thing standing between a date fix and a
    silent edit somewhere else on the page.
    """
    slug = re.sub(r"[ \-/]", "_", title)
    old = gw.page_text(s, title)
    new = old
    print("=" * 70)
    print(f"PAGE: {title}  ({len(fixes)} prose fixes)")
    for label, o, n in fixes:
        c = new.count(o)
        if c != 1:
            raise SystemExit(f"prose text not unique ({c} hits): {label}")
        new = new.replace(o, n, 1)
        print(f"\n--- {label}\n  OLD: {o}\n  NEW: {n}")
    with open(f"{outdir}/{slug}_old.wiki", "w") as f:
        f.write(old)
    with open(f"{outdir}/{slug}_new.wiki", "w") as f:
        f.write(new)
    print()
    return old, new


def guarded_save(s, title, old, new, summary):
    """Save only if the live page still matches `old`."""
    current = gw.page_text(s, title)
    if current != old:
        print(f"ABORT {title}: page changed since diff was built")
        return None
    r = gw.edit_page(s, title, text=new, summary=summary)
    res = r.get("edit", r)
    print(f"SAVED {title}: rev {res.get('newrevid')} ({res.get('result')})")
    return res


def cite_errors(s, title):
    """Count mw-ext-cite-error occurrences in the rendered page."""
    data = gw.get(s, action="parse", page=title, prop="text",
                  formatversion="2")
    return data["parse"]["text"].count("mw-ext-cite-error")
