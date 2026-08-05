# subnational — aligning GOIT/GGIT locations with the GEM subnational standard

GEM adopted an ISO 3166-2–based subnational standard in April 2026. Trackers
inside the SQL database were migrated automatically; GOIT and GGIT are outside
it, so ours have to be aligned by hand — via the **subnational lookup
microservice** the data team (D.) built, plus the naming-conventions sheet.

This folder holds the client, the reference data, and the per-tracker
reconciliation work. Data outputs live in `working-files/` (gitignored).

Colleagues are referred to by initials — this repo is public. The
initials↔person mapping is deliberately not in this repo.

## What we have to align

| Tracker | Location fields | Coordinates available |
|---|---|---|
| LNG terminals (GGIT) | `State/Province` etc. | `Latitude`/`Longitude` — direct point lookup |
| Pipelines (GOIT + GGIT) | `StartState/Province`, `EndState/Province` (plus `StartLocation`/`EndLocation`, prefecture, country, region) | no coordinate columns — endpoints have to be derived from the route linestrings in `goit-ggit-pipeline-routes` |

Terminals are the easy case and should go first. Pipelines are the reason
T.H. wanted this: a route is a line, so "the" subnational unit is really a
start unit and an end unit, and some routes branch to several endpoints. See
[Open questions](#open-questions).

## The service

Django + PostGIS app on Heroku, source at
[GlobalEnergyMonitor/subnational_lookup](https://github.com/GlobalEnergyMonitor/subnational_lookup)
(private). Two endpoints, both `GET` (single) and `POST` (batch):

- `POST /api/subnational-lookup/` — coordinates → the boundary they fall in.
  Inside a boundary → `contains_coordinates: true`. Within 1 km of one →
  nearest boundary with `contains_coordinates: false` and `distance_m`.
  Further out → `{"error": "not found"}` for that point (batch still 200s).
- `POST /api/subnational-check/` — `subnational_code` + coordinates →
  `is_in_subnational_boundary`. Use this to validate values we already have.

Responses carry `alpha_3_code`, `subdivision_name`, `category_name`,
`subdivision_name_local_variation`, `name_source`, `subnational_code`,
`other_code`, `geom_source`. Geometry is never returned.

Batch responses are **positional** — results come back in request order, and
`id` is echoed only if you send it. Always send an `id`; `subnational_api.py`
also hard-fails if the result count doesn't match the request count.

### Credentials

The app URL and API key were shared by T.H. via 1Password on 2026-07-21
(share links expire after 30 days — ask them to reshare if it's dead). Store
both in the macOS keychain, the same pattern `gem-wiki/cite-error-fixes/` uses:

```bash
security add-generic-password -s gem-subnational-api -a "<app-url>" -w "<api-key>"
```

The URL goes in the account field, the key in the password field.
`subnational_api.py` reads both and never prints the key.

### Usage

```python
from subnational_api import lookup, check

lookup([{"id": "T1234", "lat": 51.5, "long": -0.12}])
check([{"id": "T1234", "subnational_code": "GB-ENG", "lat": 51.5, "long": -0.12}])
```

Both batch in chunks of 500 and retry on 429/5xx.

## Reference data

**[GEM Naming Conventions — Regions, countries & subdivisions](https://docs.google.com/spreadsheets/d/1mtlwSJfWy1gbIwXVgpP3d6CcUEWo2OM0IvPD6yztGXI/edit?gid=1911684152#gid=1911684152)**,
`Country subdivisions` tab — 3,789 rows, one per subnational unit:

`ISO 3166-1 alpha-3 · GEM subnat code · Subnational name · Subnational name
variations · Category · Latest ISO update · Boundary source · Latitude ·
Longitude`

The `Subnational name variations` column is the name→code crosswalk for records
with no usable coordinates; `Latitude`/`Longitude` are approximate centroids,
useful as a fallback but not for validation. The same table ships as
`country_subdivisions.csv` in the service repo.

GEM deviates from ISO 3166-2 in three places (Monaco, Norway, Western Sahara),
and recognizes Kosovo, Palestine, Taiwan and Western Sahara as countries, with
Crimea/Donbass as Ukraine — see the sheet's `Notes` tab.

## Boundary geometries

`Boundary source` in the sheet names six upstream providers:

| Source | Rows | Countries |
|---|---|---|
| GADM | 2,559 | 151 |
| COD-AB (OCHA/HDX) | 503 | 21 — AZE BDI CUB ESH ETH KAZ KIR LKA MAR MDV MRT NAM NPL PHL PSE QAT SLB SLE STP THA UGA |
| WOF (Who's On First) | 452 | 12 — CYP FIN GRC IND ISR LUX MLT SRB SVN SYC TWN XXK |
| Kontur | 258 | 16 — DZA ESP GBR GNQ GRL IDN IRL LVA MLI MNE PAK PAN PRK SAU SGP YEM |
| Geonorge (Kartverket) | 15 | NOR |
| Marine Regions | 2 | MEX, USA (EEZ polygons) |

The six are already merged into one GeoPackage — **there is no need to
re-assemble them from upstream**. The composite lives in the data team's Drive,
in `Mapping/subnational boundaries/`:

- `subnat_bound_2026-04-23_1146.gpkg` (901 MB, file id `1svHixe6jif0tb18tQOHU2QeQT5lDglld`)
  — single `land` layer, ~3,796 MULTIPOLYGON features in EPSG:4326, columns
  `source · alpha_3_code · Other code · Other name · GEM subnat code · geometry`.
  This is what gets loaded into the service's PostGIS table.
- `eez_iso_countries_2026-04-23_1146.gpkg` (166 MB, file id `1d5Lq8FHkswOnjPZeZtncStMVm56_rS5w`)
  — the EEZ/Marine Regions polygons.
- `subnat-boundaries-postgis.ipynb` — the Colab notebook documenting the
  `ogr2ogr` load into the Heroku PostGIS instance.

**Do not put the raw gpkg in this repo.** At 901 MB it is far too big to
commit, and the repo sits inside Dropbox, so a local copy syncs. Keep it
outside the repo (`~/subnational-boundaries/` or similar) and point scripts at
it via an env var, or work against the API and skip the geometry entirely.

A simplified derivative (`ST_SimplifyPreserveTopology`, as the Colab notebook
suggests) would be small enough to keep locally if we want offline lookups or
map overlays — worth doing once, not per use.

## Open questions

- **Code format.** The sheet and the live API return ISO 3166-2 style codes
  (`GB-ENG`, `AF-BDS`); the service README's examples show `GBR-ENG`. The live
  service is the authority — confirm with D. before hardcoding either.
- **Pipeline endpoints.** First/last vertex of the route linestring is the
  obvious source of start/end coordinates, but branching routes have several
  endpoints and multi-part geometries have no guaranteed vertex order. Decide
  the rule (and how to represent a branch) before running a bulk pass.
  T.H. flagged this on 2026-06-18 and offered a working session.
- **Where the standardized values land.** New `StartSubnationalCode`/
  `EndSubnationalCode` columns in the tracker sheet, or overwrite the existing
  `State/Province` values with standard names? This decides whether it's a
  release-download schema change (and a data-dictionary update).
- **Migration timing.** T.H. asked about a September conversation on 2027
  migration plans — GOIT/GGIT are candidates to move into the database, which
  would make this alignment a prerequisite rather than a one-off.

## Plan

1. **Get credentials into the keychain** and run the smoke test
   (`python3 subnational_api.py`).
2. **LNG terminals first** — pull `Latitude`/`Longitude` from the tracker
   sheet, batch-lookup, and produce a per-terminal report: current
   `State/Province` vs. returned `subdivision_name`/`subnational_code`, flagged
   as match / name-variation match / mismatch / not-found. This validates the
   whole approach against a dataset with real point coordinates.
3. **Cross-check existing province values** with `/api/subnational-check/` once
   a name→code mapping exists, so we can tell "wrong name" from "wrong
   coordinates".
4. **Pipelines** — derive endpoints from `goit-ggit-pipeline-routes`, resolve
   the branching question, then run the same report for start and end.
5. **Wire into the release flow** — once the columns exist, add a check to
   `releases/qc/data-release-qc.py` so a release can't ship a subnational value
   that doesn't validate.

## Email thread

T.H., "Applying the GEM Subnational Standard for trackers outside the
database" (2026-06-10 → 2026-07-22). Also mentioned there: an
[Asana form](https://form.asana.com/?k=aQK1Pj5wIZ-a7zrNrsyt6A&d=1200305284526705)
for having the data team return a standardized file, if we'd rather hand off a
release than script it.
