# fix-bad-links — Background-citation repair for LNG terminal wiki pages

Checks every citation in the **Background section** of GEM.wiki LNG terminal
pages and repairs broken or drifted references. Coverage is tracked per
country in [COVERAGE.md](COVERAGE.md). The queue comes from the LNG update
assignments sheet: countries the researcher is working on but has not yet
finished (Complete? = FALSE).

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
4. **Repair, archive-first**: Wayback snapshot of the original URL
   (verify the snapshot's content actually supports the sentence) →
   relocated live copy of the same document → new source verified to
   support the claim. Cite GIIGNL reports in the standard format
   (`fixlib.giignl`). Deduplicate same-URL refs into named refs.
5. **Build + save** — author a per-country fix spec using `fixlib.py`
   (see the docstring): marker-locates each ref uniquely, writes
   `<slug>_old.wiki` / `<slug>_new.wiki`, and the guarded save re-fetches
   the live page and ABORTS if it changed since the diff was built.
   After saving, re-parse the page and confirm zero `mw-ext-cite-error`.
6. **Record** the country in COVERAGE.md (date, pages, revision numbers).

## Scope and policies

- Background sections only. Auto-generated `autoref_*` sections (below
  "COMMENT 3" in page wikitext) are out of scope.
- Refs that are dead with no archive and no verifiable replacement are left
  as-is and noted in COVERAGE.md.
- Edits authenticate via the bot password in `../../.env` relative to
  `working-files/` (i.e. `gem-wiki/.env`, never committed).
- Per-edit approval exception (user-approved 2026-07-21): this project runs
  autonomously — no per-edit approval needed. Escalate to the user only for
  URLs needing a human browser check or genuinely new situations.
- Scan output (`*.json`) and page dumps (`*.wiki`) are working data,
  gitignored repo-wide.
