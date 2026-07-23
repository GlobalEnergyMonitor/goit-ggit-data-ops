#!/usr/bin/env python3
"""Scan Background-section citations of gem.wiki LNG terminal pages.

Usage:
  python3 scan_background_refs.py "Category:LNG Terminals in Greece"
  python3 scan_background_refs.py "Krk FSRU" "Adria LNG Terminal"

For every <ref> in each page's Background section, reports:
  - an HTTP verdict: OK / SOFT404 / BROKEN / CHECK (401/403/429, likely
    bot-blocked — needs archive verification, not automatic repair) /
    MALFORMED (no URL) / REUSE (self-closing named ref)
  - relevance flags on OK HTML pages: DRIFT (no terminal-name keyword and no
    LNG vocabulary — likely redirect-to-homepage) / WEAK (LNG vocabulary but
    no terminal name) / PDF-UNCHECKED
  - same normalized URL cited in >= 2 separate refs (dedup candidates)

Writes JSON to stdout; redirect to a gitignored scan_<country>.json.
Verdicts are leads, not conclusions — see README step 3.
"""
import json
import re
import sys
import unicodedata

sys.path.insert(0, sys.path[0] + "/../..")
import gemwiki as gw

import requests

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/126.0.0.0 Safari/537.36")

SOFT404_PATTERNS = re.compile(
    r"(page (you requested )?(was |could )?not (be )?found|"
    r"404[^0-9]{0,20}(error|not found)|not found[^<]{0,20}404|"
    r"page doesn.?t exist|no longer available|"
    r"page introuvable|page non trouv|contenu introuvable)",
    re.I,
)
LNG_WORDS = ["lng", "liquefied natural gas", "gnl", "regasification",
             "regasificat", "fsru", "floating storage"]
STOPWORDS = {"lng", "terminal", "fsru", "of", "the", "de", "port", "energy"}

REF_RE = re.compile(r"<ref[^>/]*?(/>|>.*?</ref>)", re.DOTALL)
URL_RE = re.compile(r"https?://[^\s|<>\]\}\"']+")
TAG_RE = re.compile(r"<[^>]+>")


def background_section(text):
    m = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)", text)
    return m.group(1) if m else None


def name_keywords(title):
    """Terminal-name keywords derived from the page title (ascii-folded)."""
    folded = unicodedata.normalize("NFKD", title).encode("ascii", "ignore")
    words = re.findall(r"[a-z]+", folded.decode().lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def norm_url(u):
    u = re.sub(r"^https?://(www\.)?", "", u.rstrip(".,);"))
    return u.rstrip("/").lower()


def fetch(url):
    try:
        r = requests.get(url, headers={"User-Agent": BROWSER_UA}, timeout=30,
                         allow_redirects=True, stream=True)
        ctype = r.headers.get("content-type", "").split(";")[0]
        body = b""
        if "html" in ctype:
            body = r.raw.read(400000, decode_content=True)
        r.close()
        return r.status_code, r.url, ctype, body.decode("utf-8", "replace")
    except requests.RequestException as e:
        return None, url, "", str(e)[:120]


def scan_page(s, title):
    text = gw.page_text(s, title)
    section = background_section(text)
    if section is None:
        return {"error": "no Background section"}
    refs = [m.group(0) for m in REF_RE.finditer(section)]
    keywords = name_keywords(title)
    results, by_url, checked = [], {}, {}
    last_end = 0
    for i, m in enumerate(REF_RE.finditer(section), 1):
        ref = m.group(0)
        context = re.sub(r"\s+", " ", section[last_end:m.start()]).strip()[-160:]
        last_end = m.end()
        if ref.endswith("/>"):
            results.append({"n": i, "verdict": "REUSE", "context": context})
            continue
        urls = [u.rstrip(".,);") for u in URL_RE.findall(ref)]
        if not urls:
            results.append({"n": i, "verdict": "MALFORMED",
                            "wikitext": ref[:200], "context": context})
            continue
        for u in urls:
            by_url.setdefault(norm_url(u), []).append(i)
            if norm_url(u) not in checked:
                checked[norm_url(u)] = fetch(u)
            status, final_url, ctype, body = checked[norm_url(u)]
            rec = {"n": i, "url": u, "status": status, "context": context}
            if status is None:
                rec.update(verdict="BROKEN", error=body)
            elif status in (401, 403, 429):
                rec["verdict"] = "CHECK"
            elif status != 200:
                rec["verdict"] = "BROKEN"
            elif body and SOFT404_PATTERNS.search(body):
                rec.update(verdict="SOFT404",
                           tell=SOFT404_PATTERNS.search(body).group(0)[:60])
            else:
                rec["verdict"] = "OK"
                if "web.archive.org" in u:
                    pass
                elif "html" not in ctype:
                    rec["flag"] = "PDF-UNCHECKED"
                else:
                    low = TAG_RE.sub(" ", body).lower()
                    if not any(w in low for w in keywords):
                        rec["flag"] = ("WEAK" if any(w in low for w in LNG_WORDS)
                                       else "DRIFT")
                if final_url != u:
                    rec["final_url"] = final_url
            results.append(rec)
    dups = {k: sorted(set(v)) for k, v in by_url.items()
            if len(set(v)) >= 2 and "web.archive.org" not in k}
    return {"refs": len(refs), "keywords": keywords,
            "duplicates": dups, "results": results}


def main(args):
    s = gw.session()
    titles = []
    for a in args:
        if a.startswith("Category:"):
            titles += [p["title"] for p in gw.query_all(
                s, "categorymembers", list="categorymembers",
                cmtitle=a, cmlimit="500", cmnamespace="0")]
        else:
            titles.append(a)
    report = {}
    for t in titles:
        report[t] = scan_page(s, t)
        print(f"done: {t}", file=sys.stderr, flush=True)
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
