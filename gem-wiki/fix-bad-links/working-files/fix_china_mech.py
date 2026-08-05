#!/usr/bin/env python3
"""China batch, step 5 -- the deterministic URL-surgery repairs.

  python3 fix_china_mech.py            # build + print every old->new pair
  python3 fix_china_mech.py --save     # build, then guarded_save each page

These are not link-rot repairs and needed no research: the URL in the wikitext
is malformed, and the correct URL is recoverable from the malformed one alone.
Found by pattern-matching every China Background ref rather than by any HTTP
verdict -- a scanner that only asks "does this URL resolve" cannot see them.

  sohu-doubled   5 refs / 5 pages. The path carries the host twice --
                 `sohu.com/a/www.sohu.com/a/<id>` -- so the ref has been dead
                 since it was pasted. Stripping the duplicate yields a live,
                 on-topic article on all five; each was fetched and its Chinese
                 headline checked against the terminal (e.g. Ganyu ->
                 "开工！江苏华电赣榆LNG接收站项目正式动工").

Deliberately NOT here, because unwrapping alone would leave a dead link and the
repair is "unwrap *and* archive" -- they wait for the archive pass:
  - 2 translate.google.com wrappers (Fuqing, Wuhu): the real URL is in `u=`,
    and both targets are themselves dead/bot-walled.
  - 2 webcache.googleusercontent.com refs (Tianjin Beijing Gas, Qidong): Google
    retired its cache outright, so these can never resolve again; the original
    URL is embedded after `cache:<hash>:`.
  - 2 qcc.com/weblogin?back=... login-wall URLs (Fujian, Shenzhen Diefu): the
    firm page is in `back=`, but qcc.com serves a JS shell to a script, so the
    replacement cannot be content-validated from here.
"""
import json
import os
import re
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

OUTDIR = "china_wiki"

SOHU_DOUBLED = re.compile(
    r"^https?://(?:www\.)?sohu\.com/a/(?:https?://)?(?:www\.)?sohu\.com/a/(.+)$")

# page -> the malformed url in its wikitext (verified live after repair)
DOUBLED = {
    "Ganyu LNG Terminal":
        "https://www.sohu.com/a/www.sohu.com/a/647967672_121119270",
    "Wuhan LNG Terminal":
        "https://www.sohu.com/a/www.sohu.com/a/603475551_121123900",
    "Zhangjiagang LNG Terminal":
        "https://www.sohu.com/a/www.sohu.com/a/547872657_121124362",
    "Yantai LNG Terminal":
        "https://www.sohu.com/a/www.sohu.com/a/214158437_463997",
    "Yingkou LNG Terminal":
        "https://www.sohu.com/a/www.sohu.com/a/725415666_120407443",
}

SUMMARY = "background: fix sohu urls that repeat the hostname in the path"


def repair(url):
    m = SOHU_DOUBLED.match(url)
    if not m:
        raise SystemExit(f"not a doubled sohu url: {url}")
    return f"https://www.sohu.com/a/{m.group(1)}"


def main(argv):
    save = "--save" in argv
    s = gw.session()

    fixes = {}
    for page, url in sorted(DOUBLED.items()):
        fixes[page] = [("sohu url doubled host -> single", url,
                        ("swap", url, repair(url)))]

    print(f"{len(fixes)} pages, {sum(len(v) for v in fixes.values())} fixes\n",
          file=sys.stderr)

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
