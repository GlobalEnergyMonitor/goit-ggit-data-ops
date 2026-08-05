# dashboards/ — GOIT & GGIT dashboard scripts

Imported 2026-07-16 from the standalone `goit-dashboard` and `ggit-dashboard` repos
(Plotly/Dash apps, originally written ~May 2023, Heroku-deployed — hence the
Procfile/runtime.txt). Those repos are now considered frozen; this is the working home
for dashboard code going forward.

Layout:
- `goit/` — GOIT (oil/NGL pipelines) dashboard app. Its `notebooks/` contained only
  stale `.ipynb_checkpoints`, which were not carried over.
- `ggit/` — GGIT (gas pipelines + LNG terminals) dashboard app and the May 2023
  notebook it grew out of.

**Both apps are broken as of 2026-07-31**: they authenticate with
`pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')`, and that
service account (`gem-analysis`) was deleted. Repointing them at the `gws` read
path (see `route-lengths/sheets_client.py`) is unstarted.

Both `app.py` files read pre-aggregated *summary tables* from Google Sheets; the raw
per-project aggregation logic (e.g. the status-by-year "buildout" series) lives in
`ggit/notebooks/app-May2023-ggit-dashboard-using-summary-tables.ipynb`
(`fig_year_counts()` and neighbors).

## Buildout-by-year methodology (as implemented in the notebook)

For each status series, filter projects to their *current* status, then group by that
status's own year column and aggregate:

| Series | Filter | Grouped by |
|---|---|---|
| Proposed | `Status == Proposed` | `ProposalYear` |
| Construction | `Status == Construction` | `ConstructionYear` |
| Operating | `Status == Operating` | `StartYearEarliest` |
| Shelved | `Status == Shelved` | `ShelvedYear` |
| Cancelled | `Status == Cancelled` | `CancelledYear` |

No other processing — a project appears only in its current-status series (a
now-operating terminal does not appear in "proposed", even though it has a
ProposalYear). This is what the "actively in-development" note on the public
LNG Terminals Dashboard research page describes.

**Known wart (2026-07-16):** the notebook's terminal *capacity* columns are built
with `.count()` rather than `.sum()` (`fig_year_counts()`, "…terminal capacity"
columns). Unused in the project-count figure, but do not reuse without fixing —
and check whether the 2024 research-page figures inherited it.
