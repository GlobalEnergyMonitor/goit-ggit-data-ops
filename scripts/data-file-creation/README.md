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
  [gem-tracker-constants](../../gem-tracker-constants/) (in this repo)
- **`FILTER_STATUS`** / **`FILTER_COUNTRIES`** — optional row filters

Outputs are written to `data-files/`.

## CI map build

[`.github/workflows/build-map-data.yml`](../../.github/workflows/build-map-data.yml)
runs the CLI in map-only mode and publishes the result by force-pushing a
single-commit orphan branch of this repo, `map-data` (so history never grows
with data), which the
[goit-ggit-cycle-maps](https://github.com/GlobalEnergyMonitor/goit-ggit-cycle-maps)
GOIT map fetches at runtime via `raw.githubusercontent.com` (free,
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

- Python with `pandas`, `geopandas`, `shapely`, `pygsheets`, `openpyxl`
  (pinned in [`requirements.txt`](requirements.txt))
- `gem-tracker-constants` (lives in this repo at
  [`../../gem-tracker-constants/`](../../gem-tracker-constants/), installed by
  the notebook's first cell) — single source of truth for fuel buckets and
  status orderings, shared with the QC summary sheets in this repo so release
  totals match QC summary totals
- `GDRIVE_API_CREDENTIALS` environment variable pointing at a Google service
  account with access to the tracker sheets
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
