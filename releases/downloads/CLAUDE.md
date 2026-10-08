# data-file-creation (formerly goit-ggit-data-requests)

Exports GOIT/GGIT pipeline (and LNG terminal) data from the tracker Google
Sheets into release downloads (xlsx/geojson/gpkg/shp) and the interim-map
geojson. See this folder's README.md for setup and configuration.

## Key facts

- All logic lives in `pipeline_exports.py` (library + CLI). The notebook
  `convert-ggit-goit-to-tracker-release-downloads.ipynb` is a thin wrapper
  around it — make logic changes in the module, not in notebook cells. The
  CI map build (`.github/workflows/build-map-data.yml`, repo root) imports
  the same module, so module changes affect both.
- The notebook is often open in Jupyter while a Claude session runs — re-read
  it from disk before editing, and prefer telling the user about needed edits
  over NotebookEdit if they are actively running it (a Jupyter save would
  clobber file edits). Editing `pipeline_exports.py` is safe in that situation
  (the notebook autoreloads it).
- Fuel buckets and status lists come from the `gem-tracker-constants` package,
  which lives in this repo at `gem-tracker-constants/` (repo root; merged in
  June 2026, installed by the notebook's first cell). Never re-declare fuel
  lists inline — edit the package's YAML data and run its tests instead. The
  QC summary sheets in this repo filter on the same buckets so release totals
  match QC totals.
- Route geometries are read from a local checkout of
  `goit-ggit-pipeline-routes` (`PIPELINE_ROUTES_PATH` in the config cell).
- **A "NO-ROUTE CONFLICT" warning is a sheet bug, not an exporter bug.** It
  means a row is `RouteAccuracy = no route` while a real geometry sits in the
  routes repo; `enforce_no_route_null_geometry()` then nulls it, so a route
  that exists never reaches the downloader. Fix it in the sheet, not in code,
  and change **both** `RouteType` ("Not mapped (but could be …)" →
  "Mapped route (at any accuracy)") and `RouteAccuracy` — changing only the
  accuracy leaves the row self-contradictory. Grade from the data
  dictionary's own `RouteAccuracy` definitions, and mind the cap it states:
  **unbuilt pipelines (proposed/shelved/cancelled/under construction) cap at
  `medium`** — a georeferenced 3,000-point route on a *proposed* pipeline is
  still `medium`, not `high`. Four gas rows were fixed this way on
  2026-09-14 (P2995 high, P3185 low, P6531 medium-by-cap, P6623 medium).
  The mirror-image case — no geometry on disk but an accuracy grade set —
  gets a null-geometry stub committed to the routes repo instead.
- `data-files/` holds release artifacts. `.gpkg`/`.zip` are
  committed deliberately (kept under GitHub's 100 MB limit); `.xlsx`,
  `.geojson`, `.csv` are gitignored. Don't add data files to commits unless
  asked — releases are the user's call.
