# GOIT / GGIT data ops

Data-release production, QC, and admin scripts for the Global Energy Monitor
pipeline and LNG terminal trackers:

- **GOIT** — Global Oil Infrastructure Tracker (crude oil, refined products, NGL pipelines)
- **GGIT** — Global Gas Infrastructure Tracker (gas pipelines + LNG terminals)

This repo is the merge of the former `goit-ggit-qc`,
`goit-ggit-data-requests`, and `gem-tracker-constants` repos (June 2026);
all histories are preserved.

Most scripts are Jupyter notebooks. Data files (`.xlsx`, `.csv`, `.geojson`,
`.json`) are gitignored — keep them in their notebook's folder locally. The
exception is `releases/downloads/data-files/`, where `.gpkg`/`.zip`
release artifacts are committed deliberately (see that folder's README).

## Setup

```bash
conda env create -f environment.yml    # or install the same into an existing env
conda activate goit-ggit-data-ops
pip install pre-commit && pre-commit install   # strips outputs from updates/ notebooks at commit
```

### Google Sheets access — unsettled (2026-07-31)

The `gem-analysis` service account was **deleted**, so `GDRIVE_API_CREDENTIALS`,
`gem_tracker_constants.sheets`, and every `pygsheets.authorize` call in this repo
no longer work.

- **Interactive reads** go through the `gws` CLI against the work profile
  (`~/.config/gws-gem`, read-only scopes). `route-lengths/sheets_client.py` is the
  pattern new code should follow — it isolates auth behind one function.
- **Writes** still require explicit per-edit approval, as always.
- **Writes** go through `gws-gem-write` and are used by exactly one thing:
  `route-lengths/`, which writes its two backend tabs. That works because it is
  run by hand — the token never leaves the machine.
- **Headless/CI access has no replacement credential.** Until one is chosen,
  `.github/workflows/build-map-data.yml`, `releases/downloads/pipeline_exports.py`,
  the `updates/` cycle notebooks, and the `dashboards/` apps are broken.

## Folder map

```
gem-tracker-constants/                canonical fuel buckets + status orderings
                                      (installable package: pip install -e ./gem-tracker-constants)
updates/                              annual update cycles (the research phase before a release)
├── UPDATE-CHECKLIST.md               reusable cycle checklist
├── asana-templates.md                Asana/update-sheet/Drive spin-up templates
├── researcher-allocation/            researcher allocation calculations, by year
└── YYYY-qN-<tracker>/                one folder per cycle (docs + progress/QC notebooks)
releases/                              the release phase (freeze, export, QC, publish)
├── RELEASE-CHECKLIST.md              reusable release checklist
├── owner-parent/                     owner/parent attribution for pipelines + terminals
├── downloads/                        export tracker sheets to release download files
│   └── data-files/                   release artifacts (.gpkg/.zip committed)
├── qc/                               pre-distribution checks for release download files
└── summary-sheets/                   per-release summary tables (one folder per release)
    ├── 2023-q4-egt/
    ├── 2023-q4-gas-pipelines/
    ├── 2023-q4-lng-terminals/
    ├── 2024-q2-africa-energy-pipelines/
    ├── 2024-q2-oil-pipelines/
    ├── 2024-q3-lng-terminals/
    ├── 2024-q4-gas-pipelines/
    ├── 2025-q1-euro-gas-tracker/
    ├── 2025-q1-oil-pipelines/
    ├── 2025-q4-gas-pipelines/
    ├── 2026-q2-oil-pipelines/
    └── _archive/                     2022–2023 releases (pre-folder-per-release convention)
route-lengths/                        pipeline length + per-country ratio calculation
                                      (writes two backend tracker tabs; run by hand)
writing-and-analysis/                 per-release briefings, announcements, figures
└── <release-subfolder>/              e.g. june-2026-goit-release/
gem-wiki/                             GEM.wiki API queries + edits (edit history,
                                      cite-error cleanups; see gem-wiki/README.md)
subnational/                          aligning tracker locations with the GEM subnational
                                      standard (lookup-microservice client; see its README)
maps/                                 local working area for tracker test maps
                                      (see maps/README.md; maps/interim-maps/ is a
                                      separate gitignored clone of the data team's repo)
_archive/                             deprecated notebooks, pre-2023 work, old R code,
                                      wiki-page-cleanup-automation
```

Anything under a `_archive/` folder is kept for historical reference and is not part of the active workflow.

## Typical release workflow

The yearly rhythm has two phases: the **annual update** (researchers revise
the live tracker sheet country by country — run it from
[updates/UPDATE-CHECKLIST.md](updates/UPDATE-CHECKLIST.md)), then the
**release** (freeze, export, QC, publish — below).

For a new quarterly release, work through [releases/RELEASE-CHECKLIST.md](releases/RELEASE-CHECKLIST.md) —
copy it into the release folder and check items off so progress is visible.
The high-level sequence:

1. **Backend QC sweep** — check the tracker Google Sheet and `goit-ggit-pipeline-routes` for data errors before anything reads from them.
2. **Length estimation** — `route-lengths/` (`python route_lengths.py`, or the
   `estimate-length.ipynb` wrapper). Writes its two backend tabs directly, so
   step 4 no longer involves pasting lengths in; see `route-lengths/README.md`
3. **Owner/parent attribution** — pick the relevant CURRENT notebook in `releases/owner-parent/`:
   - `GOIT-GGIT-owner-parent-importing-ownership-tracker-CURRENT.ipynb` (pipelines)
   - `GGIT-terminals-owner-parent-scripts-CURRENT.ipynb` (LNG terminals)
4. **Import + snapshot** — paste the length and owner/parent results back into the tracker sheet, then copy the sheet into the release's Google Drive folder. The remaining steps read from that snapshot.
5. **Release downloads** — export the download files (xlsx/geojson/gpkg/shp) with `releases/downloads/convert-ggit-goit-to-tracker-release-downloads.ipynb` (see that folder's README).
6. **Release download QC** — run `releases/qc/data-release-qc.py` against the download files (see that folder's README). Fix anything it flags at the source and re-export until clean.
7. **Summary sheets** — create a new `releases/summary-sheets/YYYY-qN-<tracker>/` folder, copy the most recent prior release notebook as the starting point, and run it against the snapshot.

## Conventions

- One folder per release under `releases/summary-sheets/`, named `YYYY-qN-<tracker>` (e.g. `2026-q2-oil-pipelines`).
- In folders with several notebooks, the active "latest" ones have `CURRENT` in the filename (e.g. `releases/owner-parent/`); single-notebook folders use the plain name.
- Deprecated work goes under `_archive/` (or a per-folder `_archive/` for topic-specific archives).
- Fuel buckets and status lists come from the in-repo [gem-tracker-constants](gem-tracker-constants/) package (`pip install -e ./gem-tracker-constants`) — the release downloads and QC summary sheets filter on the same buckets, so release totals match QC totals. Formerly a standalone repo, merged June 2026; old release notebooks may still pin `v0.x` tags from `bairdlangenbrunner/gem-tracker-constants`.
