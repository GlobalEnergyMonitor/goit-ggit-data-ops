#!/usr/bin/env python
"""Read-only lookups against GEM.wiki.

  python wiki_query.py history "Trans Mountain Pipeline" [--limit N]
  python wiki_query.py contribs SomeUsername [--limit N]
  python wiki_query.py recent [--limit N]
  python wiki_query.py search "cite error" [--limit N]

All subcommands run anonymously (no .env needed).
"""

import argparse
from itertools import islice

import gemwiki


def _fmt_size(item):
    if "sizediff" in item:
        return f"{item['sizediff']:+d}"
    if "newlen" in item and "oldlen" in item:
        return f"{item['newlen'] - item['oldlen']:+d}"
    return str(item.get("size", ""))


def _print_rows(rows, columns):
    rows = list(rows)
    if not rows:
        print("(no results)")
        return
    widths = [max(len(r[i]) for r in rows) for i in range(len(columns) - 1)]
    for row in rows:
        cells = [c.ljust(w) for c, w in zip(row, widths)] + [row[-1]]
        print("  ".join(cells))
    print(f"({len(rows)} rows)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, arg in [("history", "title"), ("contribs", "user"),
                      ("recent", None), ("search", "text")]:
        p = sub.add_parser(name)
        if arg:
            p.add_argument(arg)
        p.add_argument("--limit", type=int, default=50,
                       help="max rows to print (default 50)")
    args = parser.parse_args()

    s = gemwiki.session()

    if args.command == "history":
        items = gemwiki.page_revisions(s, args.title)
        rows = [(i["timestamp"], i.get("user", "?"), _fmt_size(i),
                 i.get("comment", "")) for i in islice(items, args.limit)]
        _print_rows(rows, ["timestamp", "user", "size", "comment"])
    elif args.command == "contribs":
        items = gemwiki.user_contribs(s, args.user)
        rows = [(i["timestamp"], i["title"], _fmt_size(i),
                 i.get("comment", "")) for i in islice(items, args.limit)]
        _print_rows(rows, ["timestamp", "title", "sizediff", "comment"])
    elif args.command == "recent":
        items = gemwiki.recent_changes(s)
        rows = [(i["timestamp"], i.get("user", "?"), i["title"],
                 i.get("comment", "")) for i in islice(items, args.limit)]
        _print_rows(rows, ["timestamp", "user", "title", "comment"])
    elif args.command == "search":
        items = gemwiki.search(s, args.text)
        rows = [(i["title"], i.get("snippet", "")
                 .replace('<span class="searchmatch">', "[")
                 .replace("</span>", "]"))
                for i in islice(items, args.limit)]
        _print_rows(rows, ["title", "snippet"])


if __name__ == "__main__":
    main()
