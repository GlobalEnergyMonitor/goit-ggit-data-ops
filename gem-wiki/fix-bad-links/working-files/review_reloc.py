#!/usr/bin/env python3
"""Print a reviewable dossier for every RELOCATED claim in a reloc_*.json.

  python3 review_reloc.py reloc_company_a.json [reloc_*.json ...]

The subagents answer "is this the same document, live elsewhere?". That is the
right question but not the whole gate: a corporate page can relocate cleanly and
still no longer support the sentence citing it (a living project-overview page
moves on from the plan it described in 2017). So before anything is saved, put
the replacement next to the paragraph it has to hold up and read both.

Prints, per claim: the citing paragraph, every editable ref containing the url,
how many times the url appears in Background (>1 needs `swap_all`), and the
agent's replacement/title/evidence.
"""
import json
import re
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402
from scan_background_refs import background_section  # noqa: E402

_BG = {}


def flat(x):
    return re.sub(r"\s+", " ", x)


def bg(s, page):
    if page not in _BG:
        _BG[page] = background_section(gw.page_text(s, page)) or ""
    return _BG[page]


def main(argv):
    s = gw.session()
    for path in argv:
        rows = json.load(open(path))
        hits = [r for r in rows if r.get("verdict") == "RELOCATED"]
        print("#" * 70)
        print(f"# {path}: {len(hits)} RELOCATED of {len(rows)}")
        for r in hits:
            url = r["url"]
            for page in dict.fromkeys(r.get("pages") or []):
                text = bg(s, page)
                refs = [m.group(0) for m in fixlib.REF_RE.finditer(text)
                        if url in m.group(0)
                        and "autoref_" not in m.group(0)[:40]]
                i = text.find(url)
                a = text.rfind("\n\n", 0, i)
                a = 0 if a < 0 else a + 2
                b = text.find("\n\n", i)
                b = len(text) if b < 0 else b
                print("=" * 70)
                print(f"{page}   [{len(refs)} editable ref(s), "
                      f"{text.count(url)} occurrence(s)]")
                print(f"  OLD: {url}")
                print(f"  NEW: {r.get('replacement')}   "
                      f"({r.get('http_status')}) {r.get('title')}")
                print(f"  EVID: {str(r.get('evidence'))[:220]}")
                for h in refs:
                    print("  REF: " + flat(h)[:220])
                print("  PARA: " + flat(text[a:b])[:420])


if __name__ == "__main__":
    main(sys.argv[1:])
