#!/usr/bin/env python3
"""Structural guard over the wave-6 diffs. Run after fix_us_wave6.py (no --save)
and before saving anything; exits non-zero on any violation.

Wave 6 only ever does one of two things, so the guard asserts exactly that and
treats anything else as a failure:

  A  bare [url text] link -- the url is replaced by its Wayback snapshot, so the
     changed line gains `web.archive.org/web/<ts>/` and loses nothing else.
  B  {{cite}} template -- the dead url STAYS in url= and archive-url/
     archive-date are filled in and url-status flipped to dead.

Rather than try to reverse the edit, `canon` reduces BOTH sides to a form that is
blind to exactly those two changes and to nothing else, and the two must come out
identical. Symmetric normalization is the point: an edit anywhere outside the
archive fields and the snapshot prefix survives into the comparison and fails.

Two normalizations are needed that the first cut of this script got wrong, both
found by it failing on real wave-6 output:

  archive fields  The three fields may be absent (Jordan Cove, NOLA, Qilak --
                  apply_archive appends them) or already present but EMPTY with
                  url-status=live (Alaska LNG -- apply_archive fills them in).
                  Both are edit B, so canon drops the fields outright and does it
                  to BOTH sides; reversing the edit on the new side only, which
                  is what the first cut did, reads a pre-existing empty field as
                  deleted text. apply_archive refuses a ref whose archive-url is
                  already populated, and check 5 below re-asserts that here so
                  dropping the fields can never mask an overwrite.
  :80             A CDX snapshot url embeds the original AS CAPTURED, which for
                  old http captures usually means an explicit `host:80`
                  (w-advisory.com:80, inglesideenergycenter.com:80). That is the
                  same url -- :80 is the http default port -- so the guard
                  normalizes the redundant default port away rather than
                  flagging it.

Checks, per page:
  1  line count identical (nothing added or dropped)
  2  <ref> and </ref> counts identical, per page and per changed line
  3  canon(old) == canon(new) for every changed line
  4  no autoref_ line is touched at all
  5  no changed line had a POPULATED archive-url before the edit
  6  every snapshot url added embeds an original that the old line actually
     cited -- i.e. we archived the url that was there, not some other one
"""
import difflib
import glob
import os
import re
import sys

SNAP = re.compile(r"https?://web\.archive\.org/web/\d{14}(?:id_)?/")
# field AND value; `[^|}\n]*` stops at the next pipe or the template's close
FIELD = re.compile(r"\|\s*(?:archive-url|archive-date|url-status)\s*="
                   r"[^|}\n]*")
POPULATED = re.compile(r"\|\s*archive-url\s*=\s*(?=[^|}\s])")
PORT = re.compile(r"(?i)\b(http://[^\s|\]}]*?):80(?=[/\s|\]}]|$)"
                  r"|\b(https://[^\s|\]}]*?):443(?=[/\s|\]}]|$)")
# a snapshot url plus the original it embeds
EMBED = re.compile(r"https?://web\.archive\.org/web/\d{14}(?:id_)?/"
                   r"(https?://[^\s|\]}]+)")


def canon(line):
    """Blind to wave 6's two edits and to nothing else."""
    line = FIELD.sub("", line)           # B: drop the archive fields entirely
    line = SNAP.sub("", line)            # A: strip the snapshot prefix
    return PORT.sub(lambda m: m.group(1) or m.group(2), line)


def main():
    news = sorted(glob.glob(f"{OUTDIR}/*_new.wiki"))
    if not news:
        sys.exit("no _new.wiki files in " + OUTDIR)
    bad, checked, touched, snaps = [], 0, 0, 0
    for new_p in news:
        old_p = new_p.replace("_new.wiki", "_old.wiki")
        if not os.path.exists(old_p):
            bad.append(f"{new_p}: no matching _old.wiki")
            continue
        old = open(old_p).read().splitlines()
        new = open(new_p).read().splitlines()
        page = os.path.basename(new_p)[:-9].replace("_", " ")
        if old == new:
            continue
        checked += 1
        if len(old) != len(new):
            bad.append(f"{page}: line count {len(old)} -> {len(new)}")
            continue
        if (o := "\n".join(old)).count("<ref") != \
                (n := "\n".join(new)).count("<ref") or \
                o.count("</ref>") != n.count("</ref>"):
            bad.append(f"{page}: ref count changed")
        for i, (a, b) in enumerate(zip(old, new), 1):
            if a == b:
                continue
            touched += 1
            if "autoref_" in a or "autoref_" in b:
                bad.append(f"{page}:{i}: autoref line modified")
                continue
            if a.count("<ref") != b.count("<ref") or \
                    a.count("</ref>") != b.count("</ref>"):
                bad.append(f"{page}:{i}: ref count changed on line")
                continue
            added = EMBED.findall(b)
            if not added:
                bad.append(f"{page}:{i}: changed but no snapshot url added")
                continue
            snaps += len(added)
            if POPULATED.search(a):
                bad.append(f"{page}:{i}: old line already had an archive-url")
            # 6: the snapshot must be OF the url that was cited here
            flat = PORT.sub(lambda m: m.group(1) or m.group(2), a)
            for orig in added:
                o1 = PORT.sub(lambda m: m.group(1) or m.group(2), orig)
                if o1.rstrip("/") not in flat and \
                        o1.rstrip("/").replace("https://", "http://") not in \
                        flat.replace("https://", "http://"):
                    bad.append(f"{page}:{i}: snapshot is of a url the old line "
                               f"did not cite: {o1[:120]}")
            if canon(a) != canon(b):
                bad.append(f"{page}:{i}: change is not purely an archive add")
                sm = difflib.SequenceMatcher(None, canon(a), canon(b))
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    if tag != "equal":
                        bad.append(f"      {tag}: {canon(a)[i1:i2]!r} -> "
                                   f"{canon(b)[j1:j2]!r}")
    print(f"{checked} pages changed, {touched} lines touched, "
          f"{snaps} snapshot urls added")
    if bad:
        print(f"\nGUARD FAIL ({len(bad)}):")
        for b in bad:
            print("  " + b)
        sys.exit(1)
    print("GUARD PASS -- every changed line is an archive addition of the url "
          "it already cited, and nothing else")


OUTDIR = "us_wiki_w6"

if __name__ == "__main__":
    main()
