#!/usr/bin/env python3
"""Regenerate HUMAN-REVIEW.md section 5 (United States) from the working files.

Written because the hand-written version of that section listed refs without
their URLs -- a checklist you have to go hunting through is not a checklist.
Every item this emits carries its **full, unbroken, clickable URL** on a line of
its own, plus the page(s) citing it and the sentence it supports, so nothing has
to be looked up in diag_us.json or on the wiki.

Data in:  diag_us.json (status, archive, cites), scan_us.json (citing sentence),
          wb_still_live.json (the 112-URL archive queue), wave6_accept.json,
          wave6_reject.json.
Prose in: NOTES below -- per-URL findings from the diagnosis, keyed by a
          distinctive substring of the URL so nothing is retyped.
Out:      us_section5.md, spliced into HUMAN-REVIEW.md by splice_us_review.py.
"""
import collections
import json
import textwrap
from urllib.parse import urlsplit


def wrap(text, indent=6):
    """Wrap prose to the file's ~79-col style. Never used on a URL line: a URL
    that has to be reassembled from two lines is the defect this file exists to
    fix."""
    return textwrap.fill(text, 79, initial_indent=" " * indent,
                         subsequent_indent=" " * (indent + 2))

D = json.load(open("diag_us.json"))
SCAN = json.load(open("scan_us.json"))
QUEUE = json.load(open("wb_still_live.json"))
ACCEPT = {r["url"] for r in json.load(open("wave6_accept.json"))}
REJECT = {r["url"]: r["why"] for r in json.load(open("wave6_reject.json"))}

# the URL-normalization false positive: the scanner's rstrip(".,);") ate the
# closing paren, so it is in the queue but was never broken. Kept out of 5h.
PAREN_ARTIFACT = "en.wikipedia.org/wiki/Elba_Island_(Georgia"

CTX = {}
for _page, _v in SCAN.items():
    for _r in _v.get("results", []):
        _u = _r.get("url")
        if _u:
            CTX.setdefault((_page, _u), (_r.get("context") or "").strip())


def pages(url):
    out = []
    for c in D[url]["cites"]:
        if c[1] not in out:
            out.append(c[1])
    return out


def host(url):
    return urlsplit(url).netloc.replace("www.", "")


def supports(url):
    for p in pages(url):
        c = CTX.get((p, url))
        if c:
            return c
    return ""


def quote(url, cap=170):
    """The citing sentence as a quoted fragment. The scanner's context is a
    window, so it often starts or ends mid-sentence -- say so with ellipses
    rather than pretending it is a whole sentence."""
    s = supports(url)
    if not s:
        return None
    if len(s) > cap:
        s = s[:cap].rsplit(" ", 1)[0] + " …"
    if s[0].islower():
        s = "…" + s
    if s[-1] not in ".!?\"”…":
        s += " …"
    return s


def wb(url):
    w = D[url].get("wayback")
    return None if not w or w == "THROTTLED" else w


def throttled(url):
    return D[url].get("wayback") == "THROTTLED"


def label(url):
    """Human-facing page list."""
    p = pages(url)
    if len(p) == 1:
        return f"**{p[0]}**"
    return " · ".join(f"**{x}**" for x in p) + f" (one ref, {len(p)} pages)"


# --- per-URL findings, keyed by a distinctive substring of the URL ----------
NOTES = {
    # 5h -- publisher-level facts that shape the search for a replacement
    "kallanishenergy.com": "522 Cloudflare gateway timeout, not a 404 — the "
        "publisher is alive and this may simply recover.",
    "construction-ic.com": "A login redirect (`ReturnUrl=`), so this never was "
        "a citable public URL. Needs a different source, not a repair.",
    "nasdaq.com/articles/u.s.-approves": "The CDX index *advertises* a June "
        "2024 capture, but Wayback returns 404 when it is requested — an "
        "indexed capture it cannot serve. Not usable.",
    "ieefa.org": "IEEFA is alive and reorganized its URLs; a title search will "
        "very likely find this.",
    "legistarwebproduction": "A Legistar agenda attachment — the item itself "
        "should still exist in the city's Legistar portal.",
    "ccbiznews.com": "The one URL whose archive status is still unknown after "
        "four passes (see 5e). Also fails to connect live.",
    "cameronlng.com": "Sempra's own newsletter PDF; the file is gone from "
        "cameronlng.com and was never captured.",
    "eversheds-sutherland.com": "Law-firm blog post; the firm is alive, so a "
        "title search on their site is the first thing to try.",
    "hvllc.com": "Haddington Ventures press release. Also see 5e — this page "
        "additionally cites `killajoules.wikidot.com`.",
    "rgvforlng.com": "Advocacy site reprinting a Brownsville Herald story; the "
        "Herald original is the better target.",
    "money.usnews.com": "US News syndicated Reuters copy; the Reuters original "
        "is the thing to find.",
    "nola.com": "The Times-Picayune's old `index.ssf` URL scheme is retired "
        "wholesale; nola.com's own search is the way in.",
    "kpb.us": "Kenai Peninsula Borough mayor's page; the borough site was "
        "restructured.",
    # 5g -- the live-200 group
    "wsj.com": "WSJ paywall.",
    "subscriber.politicopro.com": "Politico Pro subscriber wall.",
    "ijglobal.com": "IJGlobal subscriber wall. No context recorded by the "
        "scanner for this one.",
    "seekingalpha.com/news/3452513": "Seeking Alpha bot wall.",
    "seekingalpha.com/news/3259917": "Seeking Alpha bot wall.",
    "seekingalpha.com/news/3523505": "Seeking Alpha bot wall.",
    "seekingalpha.com/news/3473279": "Seeking Alpha bot wall.",
    "fileID=9673760": "FERC eLibrary shell — the live URL returns 200, so it "
        "works for a reader; only a script cannot read it.",
    "bit.ly/2nOu7Lj": "Shortlink resolves fine.",
    "bit.ly/2niBu0B": "Shortlink resolves fine, but its target no longer says "
        "what the sentence claims — this is the \"Project Schedule\" case in 5e.",
    # 5a -- bot walls worth a word
    "query.nytimes.com": "A pre-2010 NYT `fullpage.html` permalink. These "
        "mostly still resolve for a human; if it does not, the article is "
        "findable in the NYT archive by date.",
    "maritime.dot.gov": "MARAD's pending-applications index — a live index "
        "page, not an article, so it may no longer *list* West Delta even "
        "though it loads.",
    "spglobal.com/commodity-insights": "Note the URL's percent-encoded query "
        "is lowercased; the path itself is intact.",
    # 5a -- soft 404s
    "energyintel.com/0000018c": "Opaque ID, so the headline cannot be inferred "
        "from the URL. Subscription site. Cited on both pages for the same "
        "claim.",
    "energyintel.com/0000018d": "Same publisher, same opaque-ID situation. "
        "Note the \"Deflin\" typo in the wiki sentence while you are there.",
    "pressherald.com": "Portland Press Herald, \"Would-be LNG developer pulls "
        "plug on Calais project,\" 14 Dec 2010. Resolves to itself at 200 with "
        "`calais` present — almost certainly just the paper's paywall shell.",
    "kcby.com": "KCBY, \"FERC says it will deny all requests for rehearing of "
        "Jordan Cove.\"",
    "fool.com": "Motley Fool, 11 Dec 2019.",
}

PUBLISHER = {
    "reuters.com": "Reuters blocks datacenter traffic wholesale; every other "
        "batch in this project hit the same wall (see the France and Brazil "
        "rows in COVERAGE.md). **One check settles all 22.**",
    "businesswire.com": "Press releases — these effectively never disappear, "
        "and Business Wire keeps them indefinitely at a stable URL.",
    "bizjournals.com": "American City Business Journals paywall.",
}

OUT = []
W = OUT.append


def item(url, extra=None, box=True):
    """One checklist entry: page(s), status, the URL on its own line, the
    sentence it supports. The URL is never wrapped, truncated or backticked --
    it has to be clickable and copy-pasteable as-is."""
    tick = "- [ ] " if box else "- "
    st = D[url].get("retry_status")
    st = "no connection" if st is None else f"HTTP {st}"
    arc = "archive: none"
    if wb(url):
        arc = "archive: exists"
    elif throttled(url):
        arc = "archive: unknown (throttled)"
    W(f"{tick}{label(url)} — {st}, {arc}")
    W(f"      {url}")
    q = quote(url)
    if q:
        W(wrap(f'supports: “{q}”'))
    note = extra or next((v for k, v in NOTES.items() if k in url), None)
    if note:
        W(wrap(note))
    if wb(url) and url in REJECT:
        W("      capture:")
        W(f"      {wb(url)}")
        W(wrap(f"rejected because: {REJECT[url]}"))
    elif wb(url) and url not in ACCEPT:
        W("      capture:")
        W(f"      {wb(url)}")
    W("")


# --- classify the 112-URL queue -------------------------------------------
cls = collections.defaultdict(list)
for u in QUEUE:
    rs = D[u].get("retry_status")
    if u in ACCEPT:
        cls["accepted"].append(u)
    elif u in REJECT:
        cls["reject"].append(u)
    elif rs in (401, 403, 429):
        cls["botwall"].append(u)
    elif rs == 200:
        cls["live200"].append(u)
    elif PAREN_ARTIFACT in u:
        cls["paren"].append(u)
    else:
        cls["dead"].append(u)

# already repaired as a plain relocation in wave 4 (rev 1206896), so it is not
# an open item even though it still carries the SOFT404 flag from the scan
SOFT404_FIXED = "bit.ly/2nQXtIO"

soft404 = [u for u, r in D.items()
           if "SOFT404" in json.dumps(r) and u not in ACCEPT
           and SOFT404_FIXED not in u
           and not any(u in v for v in cls.values())]

assert sum(len(v) for v in cls.values()) == 112, \
    {k: len(v) for k, v in cls.items()}


def by_page(urls):
    return sorted(urls, key=lambda u: (pages(u)[0].lower(), u))


# =========================================================================
W("""## 5. United States (compiled 2026-07-28, rewritten 2026-07-29)

108 pages, 1232 Background refs. **68 pages edited across six waves, 0 cite
errors anywhere** — revs 1206820–1206907 (waves 1–5) and 1206935–1206952
(wave 6, the archive wave, saved 2026-07-29). **Open items below.**

Every ref listed in this section carries its **full URL on its own line**, plus
the page citing it and the sentence it supports. Nothing here needs to be looked
up in `working-files/` or on the wiki — click the URL and the item is settled.
(The `supports:` quote is a text window around the ref, so it often starts or
ends mid-sentence; ellipses mark where.)

The archive wave started from a 118-URL queue and ended with 20 snapshots on 18
pages. What happened to the other 98 is the useful part of this section, because
**73 of them need no repair at all**. Six had already been fixed by waves 1–5
(the queue was built before them), leaving 112 live:

| Disposition | n | No repair needed? | Where |
|---|---|---|---|
| content-validated snapshot, swapped in | 20 | — applied | revs 1206935–1206952 |
| bot-walled (401/403), no archive | 42 | ✅ alive, publisher blocks bots | 5a |
| live 200 — paywall or JS shell | 10 | ✅ alive as cited | 5a |
| only cited by a bot-owned `autoref_*` | 2 | ✅ out of scope | 5f |
| URL-normalization false positive | 1 | ✅ never broken | 5f |
| had a capture, but it is not the document | 16 | ❌ | 5g |
| genuinely dead, no usable archive | 21 | ❌ | 5h |
| | **112** | | |

(20 URLs became 22 ref-fixes because two captures are cited on two pages each —
the Bloomberg Sabine Pass piece and the S&P Bluewater piece.)

The 42 bot walls are the single biggest group and the most important thing not to
mistake for rot: a 401/403 to a script is a publisher refusing automation, not a
dead page.

**A caution that applies to every list below:** don't identify a ref by a bare
`[n]`. That index is the *scanner's* — the nth `<ref>` in Background, reuses
included, counting from 1 — and is not the footnote number a reader sees. Refs
here are identified by URL, page, and the sentence they support.
""")

# ---- 5a ------------------------------------------------------------------
W(f"""### 5a. A click settles it — {len(cls['botwall']) + len(cls['live200']) + len(soft404)} refs, none expected to need repair

Nothing in 5a is known to be broken. Every one of these returns either a bot
wall (401/403) or a live 200 that a script cannot read — a paywall shell, a
JavaScript-rendered page, or a soft 404. A script cannot tell any of them from
rot, and a human with a browser settles each in seconds. **The expected outcome
for almost all of them is "alive, fine as cited."**
""")

W(f"""#### The {len(cls['botwall'])} bot-walled refs — 401/403 and no Wayback capture

Nothing automated can settle these: the publisher refuses the fetch *and* there
is no archive to fall back on. They are grouped by publisher because that is the
level the behaviour lives at — one spot-check per publisher is worth far more
than that many individual clicks — but every URL is listed in full so you
never have to reconstruct one.
""")
byh = collections.defaultdict(list)
for u in cls["botwall"]:
    byh[host(u)].append(u)
for h in sorted(byh, key=lambda x: (-len(byh[x]), x)):
    urls = by_page(byh[h])
    codes = sorted({D[u]["retry_status"] for u in urls})
    code = f"all {codes[0]}" if len(codes) == 1 else "/".join(map(str, codes))
    W(textwrap.fill(
        f"**{h} — {len(urls)} ref{'s' if len(urls) > 1 else ''}, {code}.**"
        + (" " + PUBLISHER[h] if h in PUBLISHER else ""), 79))
    W("")
    for u in urls:
        item(u)

W(f"""#### The {len(cls['live200'])} refs that return a live 200

These resolve. They were flagged only because the fetched body carries no
readable article text — a subscriber wall, a client-rendered shell, or a
shortlink whose target a script would not follow. Confirm the page is the cited
document and tick it off.
""")
for u in by_page(cls["live200"]):
    item(u)

W(f"""#### The {len(soft404)} soft 404s

Each returns **200 with the expected keywords present** and has a Wayback
snapshot, so the likely answer in every case is "alive, behind a paywall or JS
shell." They are listed because a soft 404 is precisely the thing a script
cannot tell from a real page — not because they look dead. (A sixth soft 404,
`bit.ly/2nQXtIO` on Bay Crossing LNG Terminal, was a plain relocation and is
already fixed — rev 1206896.)
""")
for u in by_page(soft404):
    item(u)

open("us_section5a.md", "w").write("\n".join(OUT))
print("wrote us_section5a.md")

# ---- 5g / 5h (generated separately so the hand-written 5b-5f can sit
#      between them untouched) --------------------------------------------
OUT2 = []
W = OUT2.append
W(f"""### 5g. Had a capture, but the capture is not the document ({len(cls['reject'])})

**A Wayback 200 is not evidence.** Every candidate snapshot in the archive wave
was fetched and read against the sentence citing it before being used; these
{len(cls['reject'])} failed that check and were **not** applied. Each is listed
with its live URL, the capture that was rejected, and why — so a later pass
cannot silently re-accept it. (`working-files/wave6_reject.json` is the
machine-readable copy.) Five distinct failure modes turned up, and the last two
are the reason the check exists at all:

- **capture of a 404 page** — Wayback faithfully archived the publisher's own
  error page.
- **paywall interstitial** — the capture is the "subscribe to continue" shell.
- **JS shell** — the publisher renders client-side, so the capture has no article
  text and never can.
- **a different article at the same URL** — the URL was recycled.
- **domain squat** — `energyportal.eu` is now a Greek sports-betting site, and
  Wayback archived the spam exactly as it found it.

Two of the {len(cls['reject'])} need **no repair at all** — the live URLs return
200 and FERC eLibrary is simply not archivable — and are recorded only so they
are not re-flagged. One more is a pre-existing weak citation rather than link
rot. Those three are marked; the rest are dead links whose only capture is
unusable, so they belong with 5h in practice.
""")
for u in by_page(cls["reject"]):
    item(u, box="fileID=1145" not in u and "fileID=1158" not in u)

W(f"""### 5h. Confirmed dead, no usable archive — need a replacement source ({len(cls['dead'])})

Each of these returns a hard failure live **and** has no Wayback capture that can
be served, so nothing automated can recover them. They are the batch's genuine
residue and the only US items that need research rather than a click.

Four publisher-level facts are worth having before you start: `lngglobal.com` ×2
(today's site is unrelated, its sitemap starts December 2025 — see 5b),
`nasdaq.com` ×3 (article URLs expire by policy, and Nasdaq syndicates Reuters
copy, so the original Reuters piece is usually findable), `tradewindsnews.com`
(hard paywall, no captures) and `bit.ly` ×4 — a dead shortlink with no capture is
unrecoverable in principle, because the target is unknowable.
""")
for u in by_page(cls["dead"]):
    item(u)

open("us_section5gh.md", "w").write("\n".join(OUT2))
print("wrote us_section5gh.md")
print("counts:", {k: len(v) for k, v in cls.items()}, "soft404:", len(soft404))
