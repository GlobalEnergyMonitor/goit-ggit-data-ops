# GOIT / GGIT data ops

Data-release production, QC, and admin scripts for the Global Energy Monitor pipeline and LNG terminal trackers:

- **GOIT**: Global Oil Infrastructure Tracker (crude oil, refined products, NGL pipelines)
- **GGIT**: Global Gas Infrastructure Tracker (gas pipelines and LNG terminals)

This repo is the merge of the former `goit-ggit-qc`, `goit-ggit-data-requests`, and `gem-tracker-constants` repos (June 2026); all histories are preserved.

Most scripts are Jupyter notebooks. Data files (`.xlsx`, `.csv`, `.geojson`, `.json`, and release artifacts) are not committed, apart from the small files a map figure needs to be rebuilt (see [dataviz/README.md](dataviz/README.md)). Published tracker data is available from [globalenergymonitor.org](https://globalenergymonitor.org/).

## Setup

```bash
conda env create -f environment.yml    # or install the same into an existing env
conda activate goit-ggit-data-ops
pip install pre-commit && pre-commit install   # strips outputs from updates/ notebooks at commit
```

## Access

Most scripts here read from or write to GEM's internal tracker data and need GEM staff credentials. No credentials are stored in this repository, and nothing here grants access to GEM systems. GEM staff should see `README.internal.md` (kept locally, not committed) or ask the repo maintainer.

## Folder map

```
gem-tracker-constants/                canonical fuel buckets + status orderings
                                      (installable package: pip install -e ./gem-tracker-constants)
updates/                              annual update cycles (the research phase before a release)
├── UPDATE-CHECKLIST.md               reusable cycle checklist
├── researcher-allocation/            researcher allocation calculations, by year
├── qc/                               backend QC checks (tracker_qc.py)
└── YYYY-qN-<tracker>/                one folder per cycle (docs + progress/QC notebooks)
releases/                             the release phase (freeze, export, QC, publish)
├── RELEASE-CHECKLIST.md              reusable release checklist
├── owner-parent/                     owner/parent attribution for pipelines + terminals
├── downloads/                        export tracker data to release download files
├── qc/                               pre-distribution checks for release download files
└── summary-sheets/                   per-release summary tables (one folder per release)
route-lengths/                        pipeline length + per-country ratio calculation
writing-and-analysis/                 per-release briefings, announcements, figures
dataviz/                              kit for static maps in GEM house style (template, style rules, export)
gem-wiki/                             GEM.wiki maintenance scripts
subnational/                          aligning tracker locations with the GEM subnational standard
maps/                                 local working area for tracker test maps
_archive/                             deprecated notebooks and pre-2023 work
```

Anything under an `_archive/` folder is kept for historical reference and is not part of the active workflow.

## Typical release workflow

The yearly rhythm has two phases: the **annual update** (researchers revise the tracker country by country; run it from [updates/UPDATE-CHECKLIST.md](updates/UPDATE-CHECKLIST.md)), then the **release** (freeze, export, QC, publish).

For a new release, work through [releases/RELEASE-CHECKLIST.md](releases/RELEASE-CHECKLIST.md): copy it into the release folder and check items off so progress is visible. The high-level sequence:

1. **Backend QC sweep**: run `updates/qc/tracker_qc.py` (see that folder's README) and check the pipeline routes for data errors before anything reads from them.
2. **Length estimation**: `route-lengths/` (see its README).
3. **Owner/parent attribution**: the relevant CURRENT notebook in `releases/owner-parent/`.
4. **Import + snapshot**: bring the owner/parent results into the tracker and take a release snapshot. The remaining steps read from that snapshot.
5. **Release downloads**: export the download files (xlsx/geojson/gpkg/shp) from `releases/downloads/`.
6. **Release download QC**: run `releases/qc/data-release-qc.py` against the download files. Fix anything it flags at the source and re-export until clean.
7. **Summary sheets**: create a new `releases/summary-sheets/YYYY-qN-<tracker>/` folder, copy the most recent prior release notebook as the starting point, and run it against the snapshot.

## Conventions

- One folder per release under `releases/summary-sheets/`, named `YYYY-qN-<tracker>` (e.g. `2026-q2-oil-pipelines`).
- In folders with several notebooks, the active "latest" ones have `CURRENT` in the filename; single-notebook folders use the plain name.
- Deprecated work goes under `_archive/` (or a per-folder `_archive/`).
- Fuel buckets and status lists come from the in-repo [gem-tracker-constants](gem-tracker-constants/) package, so release totals match QC totals. Never re-declare fuel lists inline.

## Security

Never commit credentials, tokens, `.env` files, or service-account keys. If you find a security issue in this repo, report it privately to Global Energy Monitor rather than opening a public issue.
