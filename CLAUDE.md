# goit-ggit-data-ops

Data-release production, QC, and admin scripts for GEM's GOIT/GGIT trackers.
Merge of the former `goit-ggit-qc`, `goit-ggit-data-requests`, and
`gem-tracker-constants` repos (June 2026); all histories are preserved. See
README.md for the folder map and the typical release workflow.

## Key facts

- Notebooks are often open in Jupyter while a Claude session runs — re-read
  a notebook from disk before editing, and prefer telling the user about
  needed edits over NotebookEdit if they are actively running it (a Jupyter
  save would clobber file edits).
- Committed notebook outputs are deliberate only for release-record notebooks
  (summary sheets, estimate-length). `updates/` cycle notebooks must be
  committed output-free — a `.pre-commit-config.yaml` nbstripout hook enforces
  this for anyone who has run `pre-commit install`.
- Shared pygsheets auth + the canonical live pipelines-sheet key live in
  `gem_tracker_constants.sheets` (`get_sheet(key)`, `PIPELINES_SHEET_KEY`,
  `SERVICE_ACCOUNT_EMAIL`) — use these in new notebooks instead of
  re-declaring the auth boilerplate or hardcoding the key again.
- Fuel buckets and status lists come from the `gem-tracker-constants` package,
  which lives in this repo at `gem-tracker-constants/` (install with
  `pip install -e ./gem-tracker-constants`). Never re-declare fuel lists
  inline — edit the package's YAML data and run its tests instead. The release
  downloads and QC summary sheets filter on the same buckets so release totals
  match QC totals. Old release notebooks may still pin `v0.x` tags from the
  pre-merge standalone repo (`bairdlangenbrunner/gem-tracker-constants`).
- Data files (`.xlsx`, `.csv`, `.geojson`, `.json`) are gitignored repo-wide.
  Exception: `releases/downloads/data-files/` commits `.gpkg`/`.zip`
  release artifacts deliberately — see the CLAUDE.md in that folder. Don't
  add data files to commits unless asked — releases are the user's call.
- `updates/` holds annual update cycles (the researcher-driven phase before
  a release): per-cycle folders with docs plus progress/QC notebooks, run
  from `updates/UPDATE-CHECKLIST.md`. Cycle notebooks must stay strictly
  read-only against Google Sheets.
