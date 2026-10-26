# data file creation (release downloads)

Notebook for producing data-release downloads and ad-hoc data requests from
GEM's [Global Oil Infrastructure Tracker (GOIT)](https://globalenergymonitor.org/projects/global-oil-infrastructure-tracker/)
and [Global Gas Infrastructure Tracker (GGIT)](https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/).

(Formerly the standalone `goit-ggit-data-requests` repo, merged into this repo
in June 2026.)

## Module, notebook, and CLI

All export logic lives in [`pipeline_exports.py`](pipeline_exports.py): it
exports pipeline (and optionally LNG terminal) data from the tracker Google
Sheets to Excel / GeoJSON / GeoPackage / zipped Shapefile, joining route
geometries from the `goit-ggit-pipeline-routes` repo.

[`convert-ggit-goit-to-tracker-release-downloads.ipynb`](convert-ggit-goit-to-tracker-release-downloads.ipynb)
is a thin interactive wrapper around the module (same flow, cell by cell).
The module is also a CLI:

```bash
# full release exports (xlsx/geojson/gpkg/shp) into data-files/
python pipeline_exports.py --pipeline-type Oil-NGL --simplify-fuels Oil-and-NGL

# interim-map geojson only (what CI runs; handoff schema, null geometries
# dropped, '; ' country separator)
python pipeline_exports.py --pipeline-type Oil-NGL --simplify-fuels Oil-and-NGL \
    --map-only --map-output out/goit_map_latest.geojson
```

Configuration (notebook Configuration cell, or the matching CLI flags):

- **`PIPELINE_TYPE`** — `'Oil-NGL'` | `'Oil'` | `'NGL'` | `'Gas'` | `'Gas-Hydrogen'` | `'Hydrogen'` | `'Oil-and-Gas'`
- **`SIMPLIFY_FUELS`** — `None` | `'Oil'` | `'NGL'` | `'Oil-and-NGL'` | `'Gas'`;
  relabels fuels for the simplified release downloads using the canonical
  `OIL_FUEL_OPTIONS` / `NGL_FUEL_OPTIONS` buckets from
  [gem-tracker-constants](../../gem-tracker-constants/) (in this repo).
  GGIT outputs carry lowercase fuel labels (`gas`, `hydrogen`) from Nov 2026,
  with or without simplification. Every output also drops the
  `SYSTEM/NETWORK INFO` rows (network summary rows; `SYSTEM/NETWORK ROUTE`
  rows are kept)
- **`FILTER_STATUS`** / **`FILTER_COUNTRIES`** — optional row filters

Outputs are written to `data-files/`.

## LNG terminals

[`terminal_exports.py`](terminal_exports.py) builds the LNG terminal downloads (xlsx, geojson, gpkg, zipped shapefile) from the website's `lng-export-*.csv`, not from a Sheet. LNG rows only (the NH3 / LH2 / eLNG / Oil rows are dropped, decided for Oct 2026), and the six alternative-fuel columns (LH2, NH3, SyntheticLNG, RetrofitProposed, AltFuelPrelimAgreement, AltFuelCallMarketInterest) are removed from every file along with their data-dictionary rows (`DROP_COLUMNS`). The xlsx About sheet (copyright, acronyms, data dictionary) is carried over from the previous release's xlsx via `--template`, with the dates refreshed and four renamed variables fixed. Rows without coordinates stay in the xlsx and are left out of the GIS files. Shapefile field names are the fixed `SHAPEFILE_FIELDS` map taken from the Sept 2025 shapefile. Release notes are optional (`--release-notes`, one line per line).

```bash
python terminal_exports.py --csv ../summary-sheets/2026-q4-lng-terminals/GEM-GGIT-LNG-Terminals-2026-q4.csv \
    --template data-files/templates/GEM-GGIT-LNG-Terminals-2025-09.xlsx --release-month 2026-10
```

## CI map build

[`.github/workflows/build-map-data.yml`](../../.github/workflows/build-map-data.yml)
runs the CLI in map-only mode twice — GOIT (`goit_map_latest.geojson`) and
GGIT gas pipelines (`ggit_map_latest.geojson`) — and publishes both files by
force-pushing a single-commit orphan branch of this repo, `map-data` (so
history never grows with data), which the
[goit-ggit-interim-maps](https://github.com/GlobalEnergyMonitor/goit-ggit-interim-maps)
maps fetch at runtime via `raw.githubusercontent.com` (free,
CORS-enabled, ~5 min cache). Never commit to `map-data` by hand — it is
overwritten on every build. Triggers: `repository_dispatch`
(`routes-normalized`, fired by goit-ggit-pipeline-routes after it updates its
`normalized` branch), a daily cron (catches sheet-only edits), and manual
`workflow_dispatch` (with `upload: false` for dry runs and `dest_branch` for
test branches). Guardrails in `write_map_geojson()` refuse to publish a
degraded build (too few features / too small a file) or one raw can't serve
(>95 MB; GitHub's blob limit is 100 MB). The only repo secret is
`GDRIVE_API_CREDENTIALS` (service-account JSON content) — publishing uses the
workflow's own `GITHUB_TOKEN`.

## Requirements

- Python with `pandas`, `geopandas`, `shapely`, `openpyxl`, plus `pygsheets`
  for CI (pinned in [`requirements.txt`](requirements.txt))
- `gem-tracker-constants` (lives in this repo at
  [`../../gem-tracker-constants/`](../../gem-tracker-constants/), installed by
  the notebook's first cell) — single source of truth for fuel buckets and
  status orderings, shared with the QC summary sheets in this repo so release
  totals match QC summary totals
- Sheet access: locally, the `gws` CLI with the read-only work profile
  (`~/.config/gws-gem`; override with `PIPELINE_EXPORTS_GWS_CONFIG_DIR`). When
  `GDRIVE_API_CREDENTIALS` is set (CI), the module reads through `pygsheets`
  with that service account instead, so leave it unset in a local shell
- A local checkout of `goit-ggit-pipeline-routes` (path set via
  `PIPELINE_ROUTES_PATH` in the Configuration cell)

## Related repos

- [`goit-ggit-pipeline-routes`](https://github.com/GlobalEnergyMonitor/goit-ggit-pipeline-routes) — per-pipeline route geometries (`<ProjectID>.geojson`)
- [`gem-tracker-constants`](../../gem-tracker-constants/) — canonical fuel buckets and status orderings (now part of this repo; merged June 2026)

## Notes on data files

Release artifacts (`.gpkg`, `.zip`) in `data-files/` are committed
deliberately as part of a release; intermediate formats (`.xlsx`, `.geojson`,
`.csv`) are gitignored. Keep individual committed files under GitHub's 100 MB
hard limit.
