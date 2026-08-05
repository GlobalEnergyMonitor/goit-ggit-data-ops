#!/usr/bin/env python3
"""Re-judge DRIFT/WEAK relevance flags against the terminal's *Chinese* name.

  python3 cjk_relevance.py scan_china.json gem_lng.csv China -o cjk_china.json

Why this exists. `scan_background_refs.name_keywords()` derives its relevance
keywords from the wiki page *title*, ascii-folded — "caofeidian", "binzhou".
A Chinese-language source writes the same terminal as 曹妃甸 / 滨州 and never
contains the transliteration, so the keyword check cannot hit and the ref is
flagged DRIFT (no keyword, no LNG vocabulary) or WEAK (LNG vocabulary only,
which for a `.cn` host usually means the page happened to contain the ASCII
string "lng"). In the China batch that is 182 of 334 flagged-OK refs — the
flag is measuring the language of the source, not the health of the citation.

So take the keywords from the tracker instead: `LocalNames`/`OtherNames` in the
GEM export carry the Chinese name for all 90 China pages. Generic tokens
(接收站 "receiving terminal", 液化天然气, 一期) are dropped **by frequency**,
not by a hand-written stoplist — any token appearing on more than MAX_PAGES
distinct pages is vocabulary, not an identifier. That keeps the filter honest
in a language the author of this script does not read.

The tracker name alone is still not enough, and getting this wrong is what made
the first run's verdicts worthless. Chinese names are written
**<operator><place>** — 国家管网漳州 is "PipeChina Zhangzhou" — while the
article names only the place, so the full token never appears in the body and a
perfectly good ref reads as drift. Three derivations recover the place, in
increasing order of certainty:

  1. strip a leading operator, found by frequency (a leading run that begins
     names on more than MAX_PAGES pages is an operator, not a place);
  2. take the longest common **suffix** of two names of the same terminal
     (国家管网漳州 / 中国石化漳州 → 漳州) — suffix, because the place is last;
  3. romanize substrings and keep those matching the wiki title's own ascii
     words (粤电惠州 → 惠州 == "huizhou"). This is the only one that *proves*
     its token, and it is the only thing that works for a one-off operator
     where there is neither a frequent prefix nor a second name to compare.

(3) needs `pypinyin`; without it the script still runs on (1) and (2).

Output is {url: {...}} with `cjk_hits` and `verdict`:

  CONFIRMED  the body contains a distinctive Chinese name for this terminal —
             the original DRIFT/WEAK is a false positive, leave the ref alone
  NO_CJK_KW  the page had no distinctive Chinese token to test with; the
             original flag stands unresolved, decide it by hand
  STILL_OFF  fetched fine and contains neither the ASCII nor the Chinese
             name — a real drift candidate, worth a look

CONFIRMED is a reason to *stop* looking at a ref, never a reason to edit one.
This script fetches publisher hosts only and never touches archive.org.
"""
import collections
import csv
import itertools
import json
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path[:0] = [".", "../.."]
import scan_background_refs as sbr  # noqa: E402

try:
    from pypinyin import lazy_pinyin
except ImportError:                                   # optional dependency
    lazy_pinyin = None


def romanize(s):
    """Pinyin for `s`, toneless and unspaced -- 惠州 -> "huizhou"."""
    if lazy_pinyin is None:
        return ""
    return "".join(lazy_pinyin(s)).lower()


CJK = re.compile(r"[一-鿿]{2,}")
MAX_PAGES = 5           # a token on more than this many pages is generic
WORKERS = 12
NAME_COLS = ("LocalNames", "OtherNames", "TerminalName", "UnitName")


def page_title(wiki_url):
    return urllib.parse.unquote(wiki_url.rsplit("/", 1)[-1]).replace("_", " ")


def cjk_keywords(csv_path, country):
    """page title -> distinctive Chinese tokens, generic vocabulary removed."""
    raw = collections.defaultdict(set)
    for r in csv.DictReader(open(csv_path)):
        if (r.get("Country/Area") or "").strip() != country:
            continue
        w = (r.get("Wiki") or "").strip()
        if not w:
            continue
        t = page_title(w)
        for col in NAME_COLS:
            raw[t].update(CJK.findall(r.get(col) or ""))

    freq = collections.Counter(tok for toks in raw.values() for tok in set(toks))
    generic = {t for t, n in freq.items() if n > MAX_PAGES}

    # Chinese tracker names are written <operator><place> -- 国家管网漳州 is
    # "PipeChina Zhangzhou", 中石化舟山六横 is "Sinopec Zhoushan Liuheng". The
    # article names the *place* and rarely the operator, so the full token never
    # matches and the ref reads as drift. The identifying half is therefore the
    # SUFFIX, not the prefix. Operators repeat across terminals, so find them by
    # frequency -- any leading run that starts names on more than MAX_PAGES
    # distinct pages is an operator -- and strip it. Still no Chinese word list.
    lead = collections.Counter()
    for toks in raw.values():
        seen = set()
        for k in toks:
            for L in range(2, 7):
                if len(k) > L + 1:
                    seen.add(k[:L])
        lead.update(seen)
    operators = {p for p, n in lead.items() if n > MAX_PAGES}

    out = {}
    for t, toks in raw.items():
        keep = {k for k in toks if k not in generic}
        for k in list(keep):
            # Strip the longest operator prefix this name carries.
            for L in range(6, 1, -1):
                if len(k) > L + 1 and k[:L] in operators:
                    if k[L:] not in generic:
                        keep.add(k[L:])
                    break
        # Two names of one terminal agree on the place at the *end*
        # (国家管网漳州 / 中国石化漳州 -> 漳州); take that too.
        for a, b in itertools.combinations(sorted(keep), 2):
            i = 0
            while i < min(len(a), len(b)) and a[-1 - i] == b[-1 - i]:
                i += 1
            if i >= 2 and a[-i:] not in generic:
                keep.add(a[-i:])
        # Last resort, and the only one that *proves* the token it derives: a
        # one-off operator (粤电惠州, 京能曹妃甸) is too rare for the frequency
        # filter and leaves a single name, so there is no pair to compare. But
        # the wiki title already romanizes the place -- "Huizhou LNG Terminal" --
        # so romanize each substring and keep the one that matches. 粤电惠州 ->
        # 惠州 == "huizhou". No guessing: a hit is a confirmed transliteration.
        ascii_kw = set(sbr.name_keywords(t))
        if ascii_kw:
            for k in list(keep):
                for L in (2, 3, 4):
                    for i in range(len(k) - L + 1):
                        sub = k[i:i + L]
                        if sub in generic or sub in keep:
                            continue
                        if romanize(sub) in ascii_kw:
                            keep.add(sub)
        out[t] = sorted(keep, key=len, reverse=True)
    return out, generic


def targets(scan_path):
    """(url, page) for every OK ref carrying a relevance flag."""
    d = json.load(open(scan_path))
    seen = set()
    for page, rep in d.items():
        for r in rep.get("results", []):
            u = r.get("url")
            if (r.get("verdict") == "OK" and r.get("flag") in ("DRIFT", "WEAK")
                    and u and (u, page) not in seen):
                seen.add((u, page))
                yield u, page, r["n"], r["flag"]


def main(argv):
    out_path = "cjk_relevance.json"
    if "-o" in argv:
        i = argv.index("-o")
        out_path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    scan_path, csv_path, country = argv[0], argv[1], argv[2]

    kws, generic = cjk_keywords(csv_path, country)
    print(f"{len(kws)} pages with Chinese names; "
          f"{len(generic)} generic tokens dropped", file=sys.stderr)

    work = list(targets(scan_path))
    print(f"{len(work)} flagged refs to re-judge", file=sys.stderr)

    out, done = {}, 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(sbr.fetch, u): (u, p, n, fl) for u, p, n, fl in work}
        for f in as_completed(futs):
            u, p, n, fl = futs[f]
            done += 1
            try:
                status, final, ctype, body = f.result()
            except Exception as e:
                status, final, ctype, body = None, u, "", f"{type(e).__name__}"
            keys = kws.get(p, [])
            hits = [k for k in keys if body and k in body]
            if not keys:
                verdict = "NO_CJK_KW"
            elif hits:
                verdict = "CONFIRMED"
            elif status != 200:
                verdict = "NO_CJK_KW"          # could not test; not a drift claim
            else:
                verdict = "STILL_OFF"
            out.setdefault(u, []).append(
                {"page": p, "n": n, "flag": fl, "status": status,
                 "cjk_keys": keys, "cjk_hits": hits, "verdict": verdict})
            print(f"[{done}/{len(work)}] {verdict:10s} {p} [{n}]",
                  file=sys.stderr, flush=True)

    json.dump(out, open(out_path, "w"), indent=1, ensure_ascii=False)
    tally = collections.Counter(r["verdict"] for v in out.values() for r in v)
    print(f"wrote {out_path}: {tally.most_common()}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
