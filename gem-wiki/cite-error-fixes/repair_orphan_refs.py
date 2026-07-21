"""Build (and optionally save) an orphaned-ref repair for one gem.wiki page.

Recovers full <ref name=X>...</ref> definitions from page history and re-inserts
them at the first self-closing <ref name=X /> use in the current text. Read-only
by default: writes before/after/diff artifacts and validates via render preview.
Pass --save to actually submit the edit (requires prior human review of the diff).
"""
import argparse
import difflib
import json
import re
import sys
import urllib.parse

from wiki_session import WikiSession, UA

USE_NAME = re.compile(r'<ref name\s*=\s*"?\'?([^"\'>/ ]+)"?\'?\s*/\s*>')
# empty definition <ref name=X></ref> — the bot pass sometimes leaves this husk
# instead of deleting the definition outright; MediaWiki renders it as "no text
# was provided", so treat it as an orphaned use (repairable the same way)
EMPTY_DEF_NAME = re.compile(r'<ref name\s*=\s*"?\'?([^"\'>/ ]+)"?\'?\s*>\s*</ref>')
FULL_DEF = re.compile(r'<ref name\s*=\s*"?\'?([^"\'>/ ]+)"?\'?\s*>(.*?)</ref>', re.S)
ANCHOR_LEN = 60
EDIT_SUMMARY = "restore orphaned ref definitions lost in the 2025-10-16 tracker update (fix cite errors)"


def use_pat(name):
    n = re.escape(name)
    return re.compile(
        r'<ref name\s*=\s*"?\'?%s"?\'?\s*/\s*>|<ref name\s*=\s*"?\'?%s"?\'?\s*>\s*</ref>'
        % (n, n))


def def_pat(name):
    # non-empty body required — an empty husk in history is not a donor
    return re.compile(r'<ref name\s*=\s*"?\'?%s"?\'?\s*>\s*(?!</ref>).*?</ref>'
                      % re.escape(name), re.S)


def orphan_names(text):
    defined = {n for n, body in FULL_DEF.findall(text) if body.strip()}
    uses = set(USE_NAME.findall(text)) | set(EMPTY_DEF_NAME.findall(text))
    return sorted(uses - defined)


def build_repair(s, title):
    """Returns dict with repaired text + audit info, or a failure reason. No writes."""
    cur = s.call(action="query", prop="revisions", titles=title,
                 rvprop="ids|timestamp|content", rvslots="main", curtimestamp=1)
    page = list(cur["query"]["pages"].values())[0]
    if "missing" in page:
        return {"title": title, "skip": "page_missing"}
    rev = page["revisions"][0]
    current = rev["slots"]["main"]["*"]
    base = {"title": title, "pageid": page["pageid"], "base_revid": rev["revid"],
            "base_timestamp": rev["timestamp"], "start_timestamp": cur["curtimestamp"]}

    orphans = orphan_names(current)
    if not orphans:
        return {**base, "skip": "no_orphans"}

    hist = s.call(action="query", prop="revisions", titles=title, rvlimit=100,
                  rvprop="ids|timestamp|user|comment")
    revs = list(hist["query"]["pages"].values())[0]["revisions"]

    donor_text_cache = {}

    def rev_text(revid):
        if revid not in donor_text_cache:
            d = s.call(action="query", prop="revisions", revids=revid,
                       rvprop="content", rvslots="main")
            donor_text_cache[revid] = list(d["query"]["pages"].values())[0][
                "revisions"][0]["slots"]["main"]["*"]
        return donor_text_cache[revid]

    # find newest historical revision holding each missing definition
    donors = {}
    for r in revs[1:]:
        missing = [n for n in orphans if n not in donors]
        if not missing:
            break
        t = rev_text(r["revid"])
        for n in missing:
            m = def_pat(n).search(t)
            if m:
                donors[n] = {"def": m.group(0), "revid": r["revid"],
                             "timestamp": r["timestamp"], "user": r.get("user")}

    # anchors computed on the ORIGINAL current text (adjacent refs otherwise
    # false-fail after the first insertion shifts their context)
    def ws(s):
        return re.sub(r"\s+", " ", s)

    plan, failures = [], []
    for n in orphans:
        if n not in donors:
            failures.append((n, "NO_DONOR"))
            continue
        um = use_pat(n).search(current)
        anchor = current[max(0, um.start() - ANCHOR_LEN):um.start()]
        donor_t = rev_text(donors[n]["revid"])
        # exact match, else whitespace-normalized (bot pass reflows blank lines
        # around headings; prose must still match verbatim modulo whitespace)
        if anchor not in donor_t and ws(anchor) not in ws(donor_t):
            failures.append((n, f"ANCHOR_MISMATCH vs donor rev {donors[n]['revid']}"))
            continue
        plan.append((n, donors[n]))
    if failures:
        return {**base, "skip": "needs_manual", "failures": failures,
                "repairable": [n for n, _ in plan]}

    # splice all definitions in one pass over the ORIGINAL text: every span is a
    # first self-closing use computed on `current`, so by construction the edit
    # replaces only those tokens with their full definitions and touches nothing else
    splices = sorted(
        ((use_pat(n).search(current).span(), d["def"]) for n, d in plan),
        key=lambda x: x[0][0])
    repaired, pos = [], 0
    for (a, b), full in splices:
        repaired.append(current[pos:a])
        repaired.append(full)
        pos = b
    repaired.append(current[pos:])
    repaired = "".join(repaired)

    if orphan_names(repaired):
        return {**base, "skip": "orphans_remain_after_repair"}

    p = s.call(action="parse", text=repaired, title=title,
               contentmodel="wikitext", prop="text")
    preview_errors = p["parse"]["text"]["*"].count("mw-ext-cite-error")
    live = s.call(action="parse", page=title, prop="text")
    live_errors = live["parse"]["text"]["*"].count("mw-ext-cite-error")
    return {**base, "current": current, "repaired": repaired,
            "plan": [(n, d["revid"], d["timestamp"]) for n, d in plan],
            "preview_cite_errors": preview_errors, "live_cite_errors": live_errors}


def save_edit(s, r):
    token = s.csrf_token()
    res = s.call(action="edit", title=r["title"], text=r["repaired"],
                 summary=EDIT_SUMMARY, nocreate=1, maxlag=5,
                 basetimestamp=r["base_timestamp"],
                 starttimestamp=r["start_timestamp"], token=token)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("title")
    ap.add_argument("--save", action="store_true",
                    help="submit the edit (only after the diff has been reviewed)")
    ap.add_argument("--artifacts-dir", default=".")
    args = ap.parse_args()

    s = WikiSession()
    s.login()
    r = build_repair(s, args.title)
    if r.get("skip"):
        print(json.dumps({k: v for k, v in r.items() if k not in ("current", "repaired")},
                         indent=2, default=str))
        sys.exit(1)

    slug = args.title.replace(" ", "_").replace("/", "-")
    before = f"{args.artifacts_dir}/{slug}.before.wikitext"
    after = f"{args.artifacts_dir}/{slug}.after.wikitext"
    diff = f"{args.artifacts_dir}/{slug}.diff"
    open(before, "w").write(r["current"])
    open(after, "w").write(r["repaired"])
    udiff = "".join(difflib.unified_diff(
        r["current"].splitlines(keepends=True), r["repaired"].splitlines(keepends=True),
        fromfile=f"{args.title} (live rev {r['base_revid']})",
        tofile=f"{args.title} (repaired)"))
    open(diff, "w").write(udiff)

    print(f"page: {r['title']} (base rev {r['base_revid']}, {r['base_timestamp']})")
    print(f"definitions restored: {len(r['plan'])}")
    for n, revid, ts in r["plan"]:
        print(f"  {n:8s} <- donor rev {revid} ({ts})")
    print(f"live cite errors:    {r['live_cite_errors']}")
    print(f"preview cite errors: {r['preview_cite_errors']}")
    print(f"artifacts: {before} / {after} / {diff}")

    if not args.save:
        print("\nDRY RUN — no edit submitted. Re-run with --save after reviewing the diff.")
        return
    if r["preview_cite_errors"] != 0:
        print("refusing to save: preview still has cite errors")
        sys.exit(1)
    res = save_edit(s, r)
    print(json.dumps(res, indent=2))
    e = res.get("edit", {})
    if e.get("result") == "Success":
        print(f"\nsaved: https://www.gem.wiki/Special:Diff/{e.get('newrevid')}")
        live = s.call(action="parse", page=r["title"], prop="text")
        print("cite errors on live page now:",
              live["parse"]["text"]["*"].count("mw-ext-cite-error"))


if __name__ == "__main__":
    main()
