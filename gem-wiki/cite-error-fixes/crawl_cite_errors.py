#!/usr/bin/env python3
"""Crawl unique gem.wiki pages from the GEM LNG export and flag MediaWiki cite errors."""
import csv
import html
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

EXPORT = sys.argv[1] if len(sys.argv) > 1 else "gem_export.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "cite_error_results.json"
# This crawler hits gem.wiki article HTML rather than the API, but the firewall
# treats it the same: it needs the shared UA (the "baird-wiki" token is what the
# Cloudflare bypass rule matches) and it must respect the same rate limit. Both
# come from ../gemwiki.py — see ../README.md.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gemwiki as gw  # noqa: E402

UA = gw.USER_AGENT

ERR_SPAN = re.compile(
    r'<span[^>]*mw-ext-cite-error[^>]*>(.*?)</span>', re.DOTALL
)
TAG = re.compile(r"<[^>]+>")


def load_urls(path):
    urls = {}
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            u = row[2].strip()
            if u:
                urls.setdefault(u, set()).add((row[3], row[11]))  # terminal_name, country
    return urls


def fetch(url, retries=2):
    # percent-encode non-ASCII path chars; '%' kept safe so already-encoded URLs pass through
    safe_url = quote(url, safe=":/%?&=#")
    last = None
    for attempt in range(retries + 1):
        try:
            gw.throttle()  # shared ceiling; this runs under a thread pool
            req = Request(safe_url, headers={"User-Agent": UA})
            with urlopen(req, timeout=30) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except HTTPError as e:
            return e.code, ""
        except (URLError, TimeoutError, OSError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
    return None, str(last)


def check(url):
    status, body = fetch(url)
    rec = {"url": url, "http_status": status}
    if status != 200:
        rec["fetch_problem"] = body if status is None else f"HTTP {status}"
        return rec
    errs = []
    for m in ERR_SPAN.finditer(body):
        txt = html.unescape(TAG.sub("", m.group(1))).strip()
        txt = re.sub(r"\s+", " ", txt)
        errs.append(txt)
    if errs:
        rec["cite_error_count"] = len(errs)
        # dedupe preserving order
        seen, uniq = set(), []
        for e in errs:
            if e not in seen:
                seen.add(e)
                uniq.append(e)
        rec["cite_errors"] = uniq
    return rec


def main():
    urls = load_urls(EXPORT)
    print(f"{len(urls)} unique wiki URLs", flush=True)
    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(check, u): u for u in sorted(urls)}
        for fut in as_completed(futs):
            rec = fut.result()
            u = futs[fut]
            names = sorted(urls[u])
            rec["terminals"] = [n for n, _ in names]
            rec["countries"] = sorted({c for _, c in names})
            results.append(rec)
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(urls)}", flush=True)
    results.sort(key=lambda r: r["url"])
    flagged = [r for r in results if r.get("cite_error_count")]
    problems = [r for r in results if r.get("fetch_problem")]
    with open(OUT, "w") as f:
        json.dump(
            {"total_pages": len(results), "pages_with_cite_errors": len(flagged),
             "fetch_problems": len(problems), "results": results},
            f, indent=1, ensure_ascii=False,
        )
    print(f"\n{len(flagged)} pages with cite errors, {len(problems)} fetch problems")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
