#!/usr/bin/env python3
"""Print Background-section <ref> texts matching a pattern, for given pages.

  python3 dump_refs.py giignl "Adriatic LNG Terminal" "Panigaglia LNG Terminal"

The first argument is a case-insensitive regex, so several unrelated dead hosts
can be swept in one pass: `'nasdaq|bnnbloomberg|abarrelfull'`. A plain string
still works -- it is just a regex that happens to have no metacharacters.
"""
import re
import sys

sys.path[:0] = [".", "../.."]
import gemwiki as gw  # noqa: E402
from scan_background_refs import background_section  # noqa: E402

REF = re.compile(r"<ref[^>]*?(?:/>|>.*?</ref>)", re.S | re.I)


def main(argv):
    needle = re.compile(argv[0], re.I)
    s = gw.session()
    for title in argv[1:]:
        bg = background_section(gw.page_text(s, title))
        if not bg:
            print(f"### {title}: NO BACKGROUND")
            continue
        hits = [(i, m.group(0)) for i, m in enumerate(REF.finditer(bg), 1)
                if needle.search(m.group(0))]
        print(f"### {title}")
        for i, t in hits:
            print(f"[{i}] {t}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
