# maps/

Local working area for building/testing GEM tracker maps against our own data,
outside the once-a-year data-team sync.

## What's here

- The researcher-facing test map site lives in **its own repo**,
  `GlobalEnergyMonitor/goit-ggit-cycle-maps` (created 2026-07-15), cloned
  locally at `~/Dropbox/_git_ALL/_github-repos-gem/goit-ggit-cycle-maps/`
  (moved out of this folder 2026-07-15). It's a trimmed snapshot of the
  interim-maps app shell with just the `goit` and `ggit` trackers,
  auto-deployed to GitHub Pages on every push to `main`:
  - https://globalenergymonitor.github.io/goit-ggit-cycle-maps/trackers/goit/
  - https://globalenergymonitor.github.io/goit-ggit-cycle-maps/trackers/ggit/
  To change what a map shows, edit the `geojson:` URL in
  `trackers/<name>/config.js` and push (see its README). Note: GitHub push
  protection flags the public Mapbox `pk.` token in `site-config.js` as a
  secret — false positive, unblock via the URL in the push error if it recurs.
- `interim-maps/` — clone of `GlobalEnergyMonitor/interim-maps` (its own git repo;
  the parent repo just sees this folder as untracked). This is the data team's
  **active refactor/staging** map repo (commits through July 2026), *not* the live
  site — kept here as the reference/upstream for the app shell. The live site is
  `GlobalEnergyMonitor/maps` (branch `gitpages-production`) — don't test there.
  `preview-maps` / `testing-maps` are stale (Mar / Jan 2026).

## How the map app works (interim-maps)

Pure static frontend — no data-prep pipeline lives in the repo:

- `src/` — shared app shell: `index.html` + `site.js` (Mapbox GL map, table, filters,
  detail cards) + `site.css` + `countries.json`.
- `site-config.js` — sitewide defaults (Mapbox token/style, color palette, field-name
  map, radius/linewidth scaling). A tracker `config.js` overrides these.
- `trackers/<name>/config.js` — one file per tracker. Points `geojson:` at a hosted
  data file and defines table columns, search fields, filters, status→color, detail
  view, geometry types. Pipeline trackers: `trackers/goit/` and `trackers/ggit/`.
- Each tracker page loads, in order: `../../site-config.js` → `./config.js` →
  `../../src/site.js`. Merged config drives the map.
- **Data is loaded at runtime from a URL** in `config.js` — currently DigitalOcean
  Spaces, e.g. `.../interim_maps/goit_map_2026-06.geojson` (~212 MB). To use our own
  data we just repoint that URL (local file or our own upload).
- `scripts/build-pages.mjs` copies `src/` + `site-config.js` + each `trackers/*/config.js`
  into `_dist/` for GitHub Pages; `.github/workflows/pages.yml` deploys on push to `main`.

## Run locally

```
cd interim-maps
python server.py
# → http://localhost:8080/maps/trackers/goit/   (oil pipelines)
# → http://localhost:8080/maps/trackers/ggit/   (gas / LNG)
```

Note: `server.py` sets `BASE_PATH = "/maps"`, so the URL is `/maps/trackers/<name>/`
(the README in interim-maps still shows the old `/trackers/<name>/` path). Node is
only needed for the Pages build, not for local serving.

## GOIT feature schema (properties expected by trackers/goit/config.js)

Live `goit_map_2026-06.geojson` features are `LineString` with these 27 properties:

```
project-id, fuel, subnational, country-area1, url, name, unit-name, status, owner,
parent, start-year, capacity, region, region2, capacity-display, capacity-table,
tracker-custom, tracker-acro, tracker-display, units-of-m, capacity-scaled,
status-display, name-search, owner-search, parent-search, all-countries,
location-display
```

Any test geojson we generate here must expose the fields the config references
(`name, owner, parent, status, all-countries, subnational, capacity-display,
units-of-m, start-year, fuel, url, location-display`).

## To point the test maps at our own cycle data

Done via `goit-ggit-cycle-maps` (see above). The remaining data-side work:

1. Generate a geojson matching the schema above (our release notebooks already
   produce GOIT geojson; add the map-specific display/search fields).
2. Host it: <100 MB → commit it under `trackers/<name>/` in the cycle-maps repo
   and reference by relative path; larger → upload to DigitalOcean Spaces
   (needs data-team keys; CORS on `publicgemdata` is already open).
3. Update `geojson:` in `trackers/<name>/config.js`, push — Pages redeploys in
   ~30 s. Caution: the repo and Pages site are public, so pre-release data
   becomes unlisted-but-public.
