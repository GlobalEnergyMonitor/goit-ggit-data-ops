#!/usr/bin/env python3
"""Emit a per-URL research dossier for a set of dead refs, grouped by host.

  python3 dossier.py diag_us.json urls.json out_dir/

`urls.json` is a JSON list of the URLs to write up (usually the dead subset of
the diagnosis). For each one the dossier carries what a researcher needs and
nothing else: the citing page, the scanner ref index, the ref's own wikitext,
the paragraph it sits in (so redundancy against a companion ref is judgeable),
and the observed status. Grouped by host because that is the unit that
generalizes — one relocation pattern usually fixes every ref on a host
(README step 3, "look for a scheme migration").

The page text is fetched once per page, not once per ref.
"""
import json
import os
import re
import sys
from urllib.parse import urlsplit

sys.path[:0] = [".", "../.."]
import gemwiki as gw  # noqa: E402
from scan_background_refs import background_section  # noqa: E402

REF = re.compile(r"<ref[^>]*?(?:/>|>.*?</ref>)", re.S | re.I)


def para_of(bg, url):
    i = bg.find(url)
    if i < 0:
        return None
    a = bg.rfind("\n\n", 0, i)
    a = 0 if a < 0 else a + 2
    b = bg.find("\n\n", i)
    b = len(bg) if b < 0 else b
    return re.sub(r"\s+", " ", bg[a:b]).strip()


def ref_of(bg, url):
    for m in REF.finditer(bg):
        if url in m.group(0):
            return re.sub(r"\s+", " ", m.group(0))
    return None


def main(argv):
    diag_path, urls_path, out_dir = argv[0], argv[1], argv[2]
    diag = json.load(open(diag_path))
    urls = json.load(open(urls_path))
    os.makedirs(out_dir, exist_ok=True)

    by_page = {}
    for u in urls:
        for c in diag[u]["cites"]:
            by_page.setdefault(c[1], []).append(u)

    s = gw.session()
    bgs = {}
    for p in sorted(by_page):
        bgs[p] = background_section(gw.page_text(s, p)) or ""
        print(f"fetched {p}", file=sys.stderr)

    groups = {}
    for u in urls:
        groups.setdefault(urlsplit(u).netloc.lower().replace("www.", ""), []).append(u)

    index = []
    for host, hurls in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        slug = re.sub(r"[^a-z0-9]+", "-", host).strip("-")
        path = os.path.join(out_dir, f"{slug}.md")
        with open(path, "w") as fh:
            fh.write(f"# {host} — {len(hurls)} dead ref(s)\n")
            for u in sorted(hurls):
                r = diag[u]
                fh.write(f"\n## {u}\n")
                fh.write(f"- observed: retry_status={r.get('retry_status')}"
                         f" final_url={r.get('final_url')}\n")
                for _country, page, n, verdict, _flag in r["cites"]:
                    bg = bgs.get(page, "")
                    fh.write(f"- cited on **{page}** ref [{n}] ({verdict})\n")
                    rw = ref_of(bg, u)
                    if rw:
                        fh.write(f"  - wikitext: `{rw}`\n")
                    pa = para_of(bg, u)
                    if pa:
                        fh.write(f"  - paragraph: {pa}\n")
        index.append((len(hurls), host, path))
        print(f"wrote {path} ({len(hurls)})", file=sys.stderr)

    with open(os.path.join(out_dir, "INDEX.md"), "w") as fh:
        for n, host, path in index:
            fh.write(f"- {n:3} {host} → {os.path.basename(path)}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
