# goit-ggit-data-ops

Data-release production, QC, and admin scripts for GEM's GOIT/GGIT trackers.
Merge of the former `goit-ggit-qc`, `goit-ggit-data-requests`, and
`gem-tracker-constants` repos (June 2026); all histories are preserved. See
README.md for the folder map and the typical release workflow.

## Key facts

- **This repo is PUBLIC on GitHub** (verified 2026-07-28; it was private when
  the 2026-07-21 exception was granted, and that exception no longer holds).
  The global "never name individual researchers in committed content" rule
  applies in full: use initials, not full names, in commits, docs, and notes.
  Researchers are referred to by initials in
  `gem-wiki/fix-bad-links/SCOPE.md`; the initials↔person mapping is
  deliberately not in this repo. Get surnames from the `gem-desk` repo if you
  need to derive initials — the LNG assignments sheet has first names only,
  and inventing a surname initial from it is how SCOPE.md ended up
  misattributing seven of nine researchers (corrected 2026-07-28).
- Notebooks are often open in Jupyter while a Claude session runs — re-read
  a notebook from disk before editing, and prefer telling the user about
  needed edits over NotebookEdit if they are actively running it (a Jupyter
  save would clobber file edits).
- Committed notebook outputs are deliberate only for release-record notebooks
  (summary sheets). `updates/` cycle notebooks must be
  committed output-free — a `.pre-commit-config.yaml` nbstripout hook enforces
  this for anyone who has run `pre-commit install`.
- **Google Sheets auth is broken repo-wide** (2026-07-31): the `gem-analysis`
  service account was deleted, taking `GDRIVE_API_CREDENTIALS`,
  `gem_tracker_constants.sheets`, and every `pygsheets.authorize` call with it.
  New code reads via the `gws` CLI (`~/.config/gws-gem`, read-only) —
  `route-lengths/sheets_client.py` is the pattern to copy, and it keeps auth
  behind one function so the eventual CI credential is a one-place change.
  `gem_tracker_constants.sheets` is still the home of `PIPELINES_SHEET_KEY`;
  its `authorize`/`get_sheet` are dead. Existing notebooks are unfixed —
  repoint one when you next touch it, don't do a blanket rewrite.
- **Reads come from `gem-db-ops`; writes stay here.** The sibling `gem-db-ops` repo
  is the single source of truth for pulling GEM data — pipelines Sheet
  (`ggit/pull.py`, `goit/pull.py`, `--with-owners`) and read-only Postgres
  (`lng/pull.py`, `gogpt/pull.py`, `goget/pull.py`). When repointing a notebook or
  writing new code, call one of those (or `python ../gem-db-ops/gem_sheets.py --tab
  ggit -o …` for an arbitrary tab) rather than hand-rolling another Sheets/Postgres
  read; column-index maps come from `gem-db-ops/gem_colmap.py`. `route-lengths/`
  keeps the ONLY write path (`sheets_client.py` + `sheet_writer.py`, `gws-gem-write`,
  per-edit approval) — never add a write to gem-db-ops.
- **A published cost average needs at least 3 datapoints** (standing rule, set
  2026-09-02). In every capex/cost-per-km notebook,
  `MIN_REGION_DATAPOINTS = MIN_SUBREGION_DATAPOINTS = 3`; a level below the
  threshold inherits the tier above (subregion → region → global) rather than
  publishing its own mean, and the `DataPoints` column stays in the output so
  the sample size is auditable. Nov 2025 gas had no threshold and published
  Melanesia at US$0.48M/km off one pipeline; June 2026 GOIT ran 5/5 while its
  README claimed 3. It is a no-op on gas averages above the 3–4 band but it
  binds on oil/NGL: see
  `releases/summary-sheets/2026-q4-gas-pipelines/README.md` section 4 and the
  oil folder's README table. The LNG notebooks already use 3
  (`CAPEX_MIN_POINTS`). **Nov 2025 gas was restated to the rule on 2026-09-04**
  — Melanesia now inherits Oceania (US$2.68M/km), moving Papua New Guinea
  in-development capex 0.15 → 0.86 and the global total 554.05 → 554.76 US$ bn,
  in the published summary tables, the wiki cost-estimates page and the
  dashboard-refresh CSVs. **June 2026 oil/NGL was restated the same day** —
  six sparse levels now publish their own means, lowering oil operating capex
  1,053.7 → 1,047.4 and NGL operating 182.9 → 162.3 US$ bn. Its only published
  surface is the wiki's Oil section (the GOIT summary-tables workbook has never
  carried a capex tab, for any release), so that is all that was rewritten.
  Restating it first required repointing the notebook's dead
  `pygsheets.authorize` at `gem-db-ops` — done, and note that repointing a key
  means checking the header offsets in the same edit (see that folder's README).
- Fuel buckets and status lists come from the `gem-tracker-constants` package,
  which lives in this repo at `gem-tracker-constants/` (install with
  `pip install -e ./gem-tracker-constants`). Never re-declare fuel lists
  inline — edit the package's YAML data and run its tests instead. The release
  downloads and QC summary sheets filter on the same buckets so release totals
  match QC totals. Old release notebooks may still pin `v0.x` tags from the
  pre-merge standalone repo (`bairdlangenbrunner/gem-tracker-constants`).
- Data files (`.xlsx`, `.csv`, `.geojson`, `.json`) are gitignored repo-wide.
  Don't add data files to commits unless asked — releases are the user's call.
  `releases/downloads/data-files/` was documented as committing `.gpkg`/`.zip`
  release artifacts deliberately, but that has never actually worked: the
  Python-boilerplate `downloads/` rule at `.gitignore:62` swallows the whole
  tree, and the five artifacts that were tracked survived only because they
  predated it (they were deleted 2026-08-05 and the folder now tracks
  nothing). To ship artifacts from git again, add a negation for that path —
  and mind GitHub's 100 MB per-file limit.
- `gem-wiki/` holds GEM.wiki (MediaWiki) API work. **`gemwiki.py` is the one
  client — every script in that folder goes through it, so the User-Agent, the
  5 req/sec throttle and the credential lookup exist once, not per tool. Never
  hand-roll a second session, UA or auth path; non-API fetches of gem.wiki must
  still call `gemwiki.throttle()`.** Plus the `wiki_query.py` CLI. Reads are
  anonymous; edits resolve credentials via `gemwiki.credentials()` (`.env`
  first, macOS keychain second — `.env`'s `gem-wiki-api` bot password has
  strictly more grants, so that order is load-bearing; see the folder README).
  Cloudflare's Under Attack Mode (the 2026-08-07 incident) is off again as of
  2026-08-11, but keep the `baird-wiki` UA token — it's the WAF-bypass
  identity if UAM returns; if scripted access starts 403ing, check the UA
  first. Same policy as Google
  Sheets: never push a wiki edit without previewing it and getting explicit
  per-edit approval from the user. Exception (user-approved 2026-07-20):
  `gem-wiki/cite-error-fixes/` runs its gated orphaned-ref repair in
  approved batches of ~50 pages, not per edit — see that folder's README
  for the gates (project completed 2026-07-20: all 411 flagged pages fixed,
  including the manual queue; STATUS.md has the record and two follow-ups —
  a Data Team heads-up and 4 broken DB wiki links). Its `wiki_session.py` is
  now a thin shim over `gemwiki.py` (it used to carry its own urllib stack, UA
  and `citation-fixer` keychain credential) and must keep `formatversion=1` —
  its scripts parse the v1 response shape. Its `batch*_log.csv`
  files are gitignored data but are the batch driver's done-list state —
  never delete them; progress lives in `cite-error-fixes/STATUS.md`.
  Second exception (user-approved 2026-07-21): `gem-wiki/fix-bad-links/`
  repairs broken Background-section citations on LNG terminal pages fully
  autonomously — no per-edit approval; escalate only for URLs needing a
  human browser check or novel situations. Country coverage is tracked in
  `fix-bad-links/COVERAGE.md`; workflow in its README.
- `updates/` holds annual update cycles (the researcher-driven phase before
  a release): per-cycle folders with docs plus progress/QC notebooks, run
  from `updates/UPDATE-CHECKLIST.md`. Cycle notebooks must stay strictly
  read-only against Google Sheets. Backend-sheet QC checks live in exactly
  one place — `updates/qc/tracker_qc.py`, which is both the CLI and the
  engine each cycle's `mid-update-qc-sweep.ipynb` imports. Add a check
  there, never in a notebook cell, and keep every check column-presence
  guarded so the one module covers GGIT (132 cols) and GOIT (107 cols).
