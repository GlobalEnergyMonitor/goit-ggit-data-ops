# fix-bad-links — Background-citation repair for LNG terminal wiki pages

Checks every citation in the **Background section** of GEM.wiki LNG terminal
pages and repairs broken or drifted references. Coverage is tracked per
country in [COVERAGE.md](COVERAGE.md). The queue comes from the LNG update
assignments sheet: countries the researcher is working on but has not yet
finished (Complete? = FALSE). Refs the sweep could not settle (bot walls,
login-only pages, dead refs needing a replacement source) are queued for a
person in [HUMAN-REVIEW.md](HUMAN-REVIEW.md).

Everything except this README and COVERAGE.md lives in `working-files/`:
the scripts (`fixlib.py`, `scan_background_refs.py`, per-country fix specs),
scan/diagnosis output, and the `<slug>_old.wiki`/`<slug>_new.wiki` page
dumps. Run scripts from inside `working-files/`.

## Workflow (per country)

1. **Enumerate pages** from `Category:LNG Terminals in <Country>`
   (`scan_background_refs.py` does this when given a category title).
2. **Scan** — `python3 scan_background_refs.py "Category:LNG Terminals in
   <Country>"` writes `scan_<country>.json` (gitignored data): per ref, an
   HTTP verdict (OK / SOFT404 / BROKEN / CHECK / MALFORMED / REUSE), plus
   relevance flags (DRIFT / WEAK — page loads but no longer mentions the
   terminal) and same-URL duplicate refs.
3. **Diagnose each flag.** Never trust an HTTP status alone:
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
4. **Repair, archive-first**: Wayback snapshot of the original URL
   (verify the snapshot's content actually supports the sentence) →
   relocated live copy of the same document → new source verified to
   support the claim. Cite GIIGNL reports in the standard format
   (`fixlib.giignl`). Deduplicate same-URL refs into named refs.
   - **A 200 capture is not automatically a usable one.** Check the body, not
     the status and title: Andrés's aes.com capture is navigation and footer
     with no article text, and its argusmedia capture replays Argus's own
     "the article you are searching for was not found" page. Both look like
     healthy 200s.
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
6. **Record** the country in COVERAGE.md (date, pages, revision numbers).

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
