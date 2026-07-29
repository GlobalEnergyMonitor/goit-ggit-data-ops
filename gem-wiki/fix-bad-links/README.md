# fix-bad-links — Background-citation repair for LNG terminal wiki pages

Checks every citation in the **Background section** of GEM.wiki LNG terminal
pages and repairs broken or drifted references. Scope is **every country in
the LNG update assignments sheet** — [SCOPE.md](SCOPE.md) is the full
swept/not-swept ledger, [COVERAGE.md](COVERAGE.md) is the per-batch record.
The sheet's `Complete?` column is not a filter: it tracks the researcher's data
update, not whether the citations resolve (queueing on it left Italy, Spain and
Germany unswept until 2026-07-28). Refs the sweep could not settle (bot walls,
login-only pages, dead refs needing a replacement source) are queued for a
person in [HUMAN-REVIEW.md](HUMAN-REVIEW.md).

Everything except this README and COVERAGE.md lives in `working-files/`:
the scripts (`fixlib.py`, `scan_background_refs.py`, per-country fix specs),
scan/diagnosis output, and the `<slug>_old.wiki`/`<slug>_new.wiki` page
dumps. Run scripts from inside `working-files/`.

## Workflow (per country)

1. **Enumerate pages** from the **union** of `Category:LNG Terminals in
   <Country>` (`scan_background_refs.py` expands a category title) and the
   `Wiki` column of a fresh LNG export (`python3
   ../../../gem-db-ops/gem_query.py --all-fields lng -o gem_lng.csv`).
   The category alone under-counts — an uncategorized page is invisible to it.
   That gap hid Oristano FSRU and Taranto LNG Terminal (Italy) and left five
   pages unchecked inside "done" countries: Vlora (Albania), Cong Thanh / Dung
   Quat / Hiep Phuoc (Vietnam), Summit Matarbari (Bangladesh), all swept
   2026-07-28. Pass the extras to the scanner as plain page titles.
2. **Scan** — `python3 scan_background_refs.py "Category:LNG Terminals in
   <Country>"` writes `scan_<country>.json` (gitignored data): per ref, an
   HTTP verdict (OK / SOFT404 / BROKEN / CHECK / MALFORMED / REUSE), plus
   relevance flags (DRIFT / WEAK — page loads but no longer mentions the
   terminal) and same-URL duplicate refs.
3. **Diagnose each flag** — `python3 diagnose_flags.py -o diag_<batch>.json
   scan_<country>.json ...` (browser-header retry + a fast Wayback lookup per
   flagged URL; always pass the batch's own scan files, the bare form
   re-diagnoses every country ever scanned), then
   `python3 wb_fill.py diag_<batch>.json` to resolve the archives properly.
   Never trust an HTTP status alone:
   - **An empty Wayback result can just be rate-limiting.** Throttled,
     archive.org answers the availability API with an empty
     `archived_snapshots` and CDX with a 503 HTML page — both indistinguishable
     from "never archived". Every one of the 106 Italy/Spain lookups came back
     empty on 2026-07-28 and every one was in fact archived. `wb_fill.py`
     retries with backoff, falls back to CDX (newest 200, then newest 301/302)
     and marks a lookup `THROTTLED` rather than recording a false negative.
   - **A shortlink and its target are two different questions.** Every bit.ly
     ref in the Spain batch still redirected fine; the 404s were at the far
     end. Resolve the shortlink first (`final_url` in the diagnosis), then
     judge — and swap in the resolved target either way, since the redirect is
     one service outage from taking the citation with it.
   - 401/403/429 usually means bot-blocking, not a dead link — verify via a
     Wayback snapshot's *content* (keyword counts), retry with full browser
     headers, and only repair if confirmed dead. If alive, leave untouched.
   - 200 can still be a soft 404 or a redirect-to-homepage drift.
   - **3xx is not a death certificate.** Bot/JS challenges answer 307 to a
     script and 200 to a browser — every `atlanticlng.com` ref in the LatAm
     batch scanned as `BROKEN 307` yet loads fine with the right title
     (2026-07-27). Re-fetch redirects by hand before repairing.
   - **SOFT404 verdicts need eyes, never automation.** All six in the LatAm
     batch were false positives: the pattern matched `404 */ .error` inside a
     site's *stylesheet* (gnlglobal) and a boilerplate "no longer available"
     string in page furniture (trinidadexpress), while the articles were live
     with correct titles (2026-07-27). Treat SOFT404 as "look at this", not as
     a repair trigger.
   - A URL that failed once may just have been having a bad day — re-check
     live before repairing (Andrés's aesmcac.com went 503 → 200).
   - **Cap archive.org consumers at three, total.** Two concurrent CDX jobs is
     already enough to start collecting `THROTTLED` results, which then have to
     be re-run — so parallelism past ~3 makes the sweep slower, not faster.
     `cdx_leftover.py` runs the residue pass at `max_workers=2`;
     `cdx_focus.py` is the deliberately slow single-threaded check (4 s between
     requests, appends to `cdx_focus.jsonl`) for the handful of URLs where a
     negative has to be trustworthy. Its docstring states the reason: a
     negative from a bulk sweep only means anything if archive.org was actually
     answering at the time.
   - **A *run* of consecutive failures is a rate limit, not a pile of dead
     snapshots — and archive.org signals it as a TCP `Connection refused`, not
     a 429.** Post-save verification of the 29 archives this batch introduced
     sailed through 19 at 3 s intervals and then refused every one of the last
     10 in a row, single-threaded. Taken at face value that reads as ten broken
     citations. Re-running them at 20 s intervals after a two-minute cool-down
     cleared them. So: single-threaded and 3 s apart is *not* automatically
     safe for a long serial sweep, and any failure that arrives as part of an
     unbroken tail is presumed throttled until re-checked slowly.
     (`verify_new_archives.py` does the sweep, `recheck_archives.py` the slow
     retry; the latter annotates each recovered row rather than overwriting the
     history of the failure.)
   - **Read the `.jsonl`, not the `.log`, for progress.** `cdx_leftover.log` is
     written through `| tail -100`, so the shell buffers it and the file looks
     frozen while the job is running fine. The `.jsonl` is appended per result.
   - **CDX prefix search with a regex filter is the last resort worth trying**
     before declaring a URL unarchived. When the exact URL has no capture, the
     document is often archived at a *different* path on the same host:

     ```sh
     curl -sS -A "GEM research <contact>" -G \
       --data-urlencode "url=<host>/*" \
       --data-urlencode "fl=timestamp,original,statuscode" \
       --data-urlencode "collapse=urlkey" \
       --data-urlencode "limit=50000" \
       --data-urlencode "filter=original:.*<needle>.*" \
       'https://web.archive.org/cdx/search/cdx'
     ```

     `-G` plus `--data-urlencode` is **required**, not stylistic: a raw `[Tt]`
     in a query string makes curl fail with `bad range in URL`. This is what
     found Zaule's Gas Natural press release (archived as a Spanish-language
     PDF on the company's own file server, under a path nothing linked to) and
     Gascan's `/web-es/proyectos` page after `/web-en/projects` proved to have
     no captures at all. A page that only ever existed in another language is
     still the same document.
4. **Repair, in this preference order** (codified in the `fix_*.py`
   docstrings): **relocation** — the same document live at a new publisher URL
   → **archive** — a content-validated Wayback snapshot → **drop as
   redundant** — the dead ref sits beside a live citation of the same fact →
   **re-sourcing** — a *different* document stating the claim. Re-sourcing is
   genuinely last: it silently changes what backs the sentence, so it needs the
   substitute checked against the claim, not just against the topic. Cite
   GIIGNL reports in the standard format (`fixlib.giignl`). Deduplicate
   same-URL refs into named refs.
   - **A 200 capture is not automatically a usable one.** Check the body, not
     the status and title: Andrés's aes.com capture is navigation and footer
     with no article text, and its argusmedia capture replays Argus's own
     "the article you are searching for was not found" page. Both look like
     healthy 200s. A JS-rendered page archives as its boilerplate — every
     bayern-innovativ capture in the Germany batch replays only the Impressum.
   - **Live sites soft-404 too, and some do it for any slug.** euro-petrole
     returns HTTP 200 for a URL invented on the spot and serves an unrelated
     article, so a "working" euro-petrole link proves nothing; bnnbloomberg.ca
     answers 200 with an empty shell. Grep the body for the claimed value
     before accepting any substitute.
   - **Before dropping a ref as redundant, read what the companion actually
     serves — not its `<title>`.** Redundancy is a property of the *sentence's*
     claims, not of the two refs' topics, so the companion has to be checked
     claim by claim. Gioia Tauro is the cautionary tale in both directions: the
     dead auction notice was first ruled un-droppable because Staffetta
     Quotidiana looked headline-only, but that was an extraction artifact — the
     repeated `<title>` was all the first grep caught. Staffetta in fact sends a
     full teaser paragraph ahead of the subscriber gate, carrying the stake, the
     date, the increments and the docket number, so the drop was right after
     all. Strip tags and read the body; a subscriber gate is not the same as no
     public text. (It did surface a real prose discrepancy — the page's €6.8M
     against the teaser's 6,9 — which is a separate HUMAN-REVIEW item.)
   - **Watch Unicode in URLs.** offshore-energy.biz's canonical Brunsbüttel
     path uses a **combining diaeresis** (`brunsbu%CC%88ttel`, u + U+0308) and
     answers 200; the precomposed `%C3%BC` and plain-ASCII forms both 404.
   - **Look for a scheme migration before calling a host's article dead.** Four
     turned up in one batch: Montel `/en/story/<slug>/<id>` →
     `/en/news/<id>/<slug>`; gasworld `/<slug>/<id>.article` →
     `/story/<slug>/<id>.article`; Bayern Innovativ `/en/page/<slug>` →
     `/en/emagazine/detail/en/page/<slug>`; Finnish Gas Association
     `/sites/default/files/pdf/esitykset/…` → `/wp-content/uploads/…`. One
     working example generalizes to every dead ref on that host.
   - **SEC.gov needs a contact-info User-Agent *and* redirect-following**:
     `curl -sSL -A "GEM research <contact>"`.
   - **Merge, don't overwrite.** For `{{cite}}` templates, leave the original
     in `url=` and record the snapshot in `archive-url` / `archive-date` /
     `url-status=dead` (see `apply_archive` in `fix_latam_small.py`) — a URL
     believed dead today can come back, and the original is the citation's
     provenance. Bare `[url text]` links have no field for it, so there the
     URL is replaced; nothing is lost because a Wayback URL embeds the
     original. Skip refs whose `archive-url` is already populated.
   - Validate before saving: parse the new wikitext via `action=parse` and
     compare its `mw-ext-cite-error` count against the old text, so a
     malformed template is caught before it reaches the wiki, not after.
4b. **Writing for a human?** Never hand over a bare scanner `[n]`. That index
   counts `<ref>`s inside Background only; the wiki's rendered footnote numbers
   count the whole page and start with the auto-generated infobox/table refs, so
   the two never line up (Andrés scanner `[8]` = displayed footnote `[19]`).
   Identify a ref by URL, `<ref name=...>`, and the sentence it supports.
5. **Build + save** — author a per-country fix spec using `fixlib.py`
   (see the docstring): marker-locates each ref uniquely, writes
   `<slug>_old.wiki` / `<slug>_new.wiki`, and the guarded save re-fetches
   the live page and ABORTS if it changed since the diff was built.
   After saving, re-parse the page and confirm zero `mw-ext-cite-error`.
6. **Verify what you just wrote, then record it.** Re-fetch every archive URL
   the batch introduced (`verify_new_archives.py` → `recheck_archives.py`) —
   a snapshot that was reachable while you were researching can be refused by
   the time it is on the page, and it is cheaper to find that out now than for
   a reader to. Then record the country in COVERAGE.md (date, pages, revision numbers) and
   flip its row in SCOPE.md. Anything left unsettled goes to HUMAN-REVIEW.md
   with two or three ready-made search queries per item.

### Which script to reach for

`working-files/` accumulates one-off `fix_<country>.py` specs, which is fine —
they are the audit trail. The *reusable* tools are:

| Script | Use |
|---|---|
| `scan_background_refs.py` | step 2 — the scan |
| `diagnose_flags.py` | step 3 — browser retry + fast Wayback lookup |
| `wb_fill.py` | step 3 — resolve archives properly (backoff, CDX fallback, `THROTTLED`) |
| `cdx_leftover.py` | step 3 — CDX-only residue pass, `max_workers=2` |
| `cdx_focus.py` | step 3 — slow single-threaded check when a negative must be trustworthy |
| `worklist.py` | step 3 — join scan + diagnoses into a per-page, per-ref worklist |
| `verify_snaps.py` | step 4 — content-validate candidate snapshots |
| `dump_refs.py` | step 4 — print Background refs matching a regex, across pages |
| `fixlib.py` | step 5 — build + guarded-save (`build`, `guarded_save`, `cite_errors`, `giignl`) |
| `save_isg.py` | step 5 — guarded-save several countries' pickled diffs in one run |
| `verify_new_archives.py` | step 6 — post-save sweep of every archive URL the batch introduced |
| `recheck_archives.py` | step 6 — slow retry of that sweep's failures, to tell throttling from rot |

The earlier `wb_acv.py`, `wb_brazil.py`, `verify_latam_snaps.py` and
`verify_snapshots.py` are superseded by `wb_fill.py` and `verify_snaps.py` —
kept for provenance, not for reuse.

`fixlib.build` only rewrites `<ref>` spans. That was the whole reason section 4
of HUMAN-REVIEW.md filled up with claim-vs-source mismatches rather than dead
links — the tooling could see that a sentence disagreed with its own citation
and could do nothing about it.

`fixlib.build_prose` (added 2026-07-29) closes that gap, deliberately narrowly.
Use it **only where the fix is one-way**: the sources agree with each other and
disagree with the sentence, so there is exactly one direction the correction can
go — a date the cited article predates, a figure the only reachable source
contradicts. Its fixes are `(label, old_text, new_text)` and `old_text` must
occur exactly once on the page, which is the only guard against a date fix
landing somewhere else entirely; quote enough of the sentence to be sure.

Everything softer still goes to HUMAN-REVIEW.md — but "no source at all" is not
by itself a reason to park something. Go looking first: of the three such claims
in section 4, two had perfectly good sources that nobody had searched for. Park
it only once the search has actually failed.

When it does fail, say what failing means. If a **direct quotation**'s only home
on the indexed web is gem.wiki itself, that is a finding, not a dead end: the
quote cannot be cited and must go, but the occasion it came from usually can be
sourced, so rewrite it as reported speech rather than deleting the paragraph. Do
not translate a foreign-language source back into English and leave the result
inside quotation marks — that manufactures a quote. And read the found source
for *everything* it settles, not just the clause you went in for: the Brunsbüttel
hunt turned up a CEO/CFO error in the same sentence that no one had flagged.

One thing worth checking whenever a prose figure turns out to be wrong: whether
the same figure is also in the tracker database. Often it is not (the wiki
Background carries history the tracker has no field for — an EU grant, a vessel's
arrival, a 2005 proposal with no GEM record), and sometimes the database was
right all along and the wiki was the lone outlier. Say which, rather than leaving
it open.

## Scope and policies

- Background sections only, delimited by the `==Background==` heading up to the
  next `==` heading (that is what `background_section()` matches — *not* the
  "COMMENT 3" marker, which sits just above the heading).
- Refs named `autoref_*` are auto-generated from the tracker database and are
  out of scope: they are regenerated, so editing them by hand is wasted. Scope
  them out **by the `autoref_` name**, never by position — the generated
  infobox/tables that define them sit near the top of the wikitext, *above*
  Background, and `<ref name="autoref_N" />` reuses appear inside Background
  itself. `fixlib.find_ref` and `find_ref_by_url` both filter on the name.
- Refs that are dead with no archive and no verifiable replacement are left
  as-is and noted in COVERAGE.md.
- "No replacement found" via WebSearch is not proof none exists — the API's
  index/ranking differs from plain Google (e.g. LinkedIn Pulse posts rank on
  Google but barely surface in WebSearch; that's how the Karwar syndicated
  copy was missed, 2026-07-23). Before declaring a ref unrecoverable, hand
  the reviewer 2–3 ready-made Google queries (headline fragments, dollar
  figures, both figure variants if sources disagree) so a quick browser
  search can catch what the API missed.
- **When the WebSearch budget runs out, search anyway.** `WebFetch` against
  `https://html.duckduckgo.com/html/?q=…` or `https://lite.duckduckgo.com/lite/?q=…`
  returns parsed results and does not draw on that budget; plain `curl` to the
  same URLs does not work (DDG answers 202 with a challenge) and Mojeek comes
  back empty. This is also a *different* index, so it is worth a try even when
  WebSearch is available — the Dow Jones report that closed the Brunsbüttel
  quote surfaced on the DDG lite endpoint after WebSearch had found nothing.
  Try the claim's own distinctive wording first: if the only hit is gem.wiki,
  the claim has no independent source and you have your answer.
- Edits authenticate via the bot password in `../../.env` relative to
  `working-files/` (i.e. `gem-wiki/.env`, never committed).
- Per-edit approval exception (user-approved 2026-07-21): this project runs
  autonomously — no per-edit approval needed. Escalate to the user only for
  URLs needing a human browser check or genuinely new situations.
- Scan output, page dumps, extracted Background text and run logs are working
  data, not source: `*.json` is gitignored repo-wide and
  `working-files/.gitignore` covers the rest (`*.wiki`, `*_bg.txt`, `*.jsonl`,
  `*.log`, `*.err`). The per-country fix specs (`fix_<country>.py`) are the
  record of what each batch changed and stay visible.
