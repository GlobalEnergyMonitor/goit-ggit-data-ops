# GGIT gas pipelines release checklist — November 2026

Copied from [../../RELEASE-CHECKLIST.md](../../RELEASE-CHECKLIST.md) on 2026-10-23. Check items off as they are done so the state of the release is visible to anyone who opens this folder.

```
Release:          2026-q4-gas-pipelines
Release month:    2026-11                  (stamp used in download filenames; confirm at freeze)
Tracker sheet:    1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek  ("Pipelines (Gas/Oil/NGL) - main", tab "Gas pipelines")
Release snapshot: TBD (step 6)
Data freeze:      TBD (Asana "Prep for GGIT pipelines update - Q3 2026": start 2026-10-09, due 2026-11-10)
Update cycle:     ../../../updates/2026-q3-gas-pipelines/
Run by:           Baird
```

---

## 1. One-time machine setup

- [x] Python environment with `pandas`, `geopandas`, `shapely`, `openpyxl`
- [x] `gem-tracker-constants` installed editable from this repo
- [x] Local checkout of `goit-ggit-pipeline-routes` (up to date with origin on 2026-10-23)
- [x] Sheet reads through `gws-gem` work: `updates/qc/tracker_qc.py --tracker ggit` read the live tab on 2026-10-23
- [x] Confirm `route-lengths/route_lengths.py --dry-run` reads the sheet (2026-10-27, through `gws-gem`)
- [x] Downloads export reads through `gws-gem` (2026-10-26). A full Gas export ran that way, and the oil and gas map files matched the service-account run feature for feature. Unset `GDRIVE_API_CREDENTIALS` locally, or it takes the service-account path

## 2. Pre-flight

- [ ] Wind-down of the update cycle is done (`updates/2026-q3-gas-pipelines/CHECKLIST.md` section 4): research summaries, carry-over moved to the future-tasks Asana project
- [ ] Data-freeze point agreed with everyone still editing; record it in the header
- [ ] `git pull` in `goit-ggit-pipeline-routes` on freeze day
- [x] Release folder exists: `releases/summary-sheets/2026-q4-gas-pipelines/`
- [x] Checklist copied in, header filled

## 3. Backend QC sweep — tracker sheet and pipeline routes

`python updates/qc/tracker_qc.py --tracker ggit --cycle-start 2026-07-06`

- [ ] Sweep comes back with no FAIL. First run, 2026-10-23: 24 FAIL / 103 WARN checks. **Run of 2026-10-26: 6 FAIL / 95 WARN**. Later that day 2 FAIL / 92 WARN, after the year-range check was dropped (far-future years are not errors) and the P2196 and P5796 diameter units were fixed. Before that, after the status, fuel, length, Egypt/Jordan region, unit, month, URL and WKT fixes (sheet batch 1, 85 cells), fuel matching that ignores case (gem-tracker-constants 0.7.0) and the SYSTEM/NETWORK INFO rule (0.8.0). Still open, all research calls:
  - [x] P2196 and P5796: `Diameter` with no unit (`40`, `38-45`), fixed 2026-10-26
  - [ ] P1000 and P7999: mapped route but `RouteAccuracy = "no route"`. Fix both `RouteType` and `RouteAccuracy`; unbuilt pipelines cap at `medium`
  - [ ] P2041 and P7830: `Fuel = oil` on the gas tab. The export leaves them out; move them to the oil tab or set them to N/A
- [x] SYSTEM/NETWORK INFO rows (15 on the gas tab) are dropped from the downloads, map and summary sheets (ruling 2026-10-26). The backend QC lists them as a NOTE. Dropping them removes about 77,000 km, mostly US mainlines that have no segment rows (Columbia, Gulf South, Transco, Florida Gas, Northwest), plus their routes from the map. SYSTEM/NETWORK ROUTE rows are kept
- [ ] Work through the WARNs, or note why they are acceptable for this release
- [ ] Reconcile routes against `goit-ggit-pipeline-routes` (the step 4 run reports both directions)
- [ ] Fix everything found in the source (sheet or routes repo)

## 4. Length estimation

`route-lengths/` — see `route-lengths/README.md`.

- [x] Boundary layer present
- [ ] Run against the live tracker sheet after the freeze; PROBLEMS list is clean. A pre-freeze run on 2026-10-27 (routes at `b5b3601e`) was clean and was written to both tabs; the only change from 2026-10-23 was dropping P4449's 0 km placeholder row. The 119 `LengthMergedKm = 0` and 50 blank rows did not clear and will not: they have no route file and no known length, so they need research, not this step. On 2026-10-28 the length and route rule was applied by hand to 65 cells. Expansion-only rows with no length got `0`. Three pipe rows had a placeholder `0`, which was blanked. Atlantic Bridge got 6.3 mi on both P7820 and P0154, which look like duplicates. Fifteen expansion-only rows that have a known length became "Not mapped". P8085 and P8086 became "no route". After this, there are 133 zero rows and 34 blank ones
- [ ] `unattributed_km` ~0; `overlap_km` only on named joint areas
- [ ] `--write` to push both tabs into the tracker sheet (the two output tabs are the approved auto-write carve-out; see `route-lengths/CLAUDE.md`)

## 5. Owner/parent attribution

Notebook: `releases/owner-parent/GOIT-GGIT-owner-parent-importing-ownership-tracker-CURRENT.ipynb`

- [ ] Point the notebook at the tracker sheet, run all cells
- [ ] Missing-parents list is empty

## 6. Import results into the tracker sheet, then snapshot it

- [ ] Lengths in the sheet (step 4 `--write`)
- [ ] Owner/parent output imported
- [ ] Spot-check a few pipelines: known length vs. estimate vs. merged length
- [ ] Copy the sheet into the release's Drive folder (per-action approval) and record its key in the header
- [ ] The snapshot is readable through `gws-gem`

## 7. Release downloads

`releases/downloads/pipeline_exports.py --pipeline-type Gas` (or the notebook wrapper), pointed at the **release snapshot**.

- [ ] Configuration set: `PIPELINE_TYPE`, `SIMPLIFY_FUELS`, filters, routes path, `2026-11` stamp
- [ ] Outputs in `releases/downloads/data-files/` as `GEM-GGIT-Gas-Pipelines-2026-11.{xlsx,geojson,gpkg}` + `-shp.zip`

## 8. Release download QC

- [ ] `python releases/qc/data-release-qc.py releases/downloads/data-files/GEM-GGIT-Gas-Pipelines-2026-11` exits clean
- [ ] Fixes made at the source (live sheet **and** snapshot), export re-run; remaining WARNs explained
- [ ] Trial run on the live sheet, 2026-10-26. Fuel is all `gas` and no SYSTEM/NETWORK INFO rows remain. FAILs to clear:
  - [ ] P4483 `Capacity` is `25.8/18.7`
  - [ ] P1145, P3969 and P5023 have `CapacityUnits` but no capacity
  - [ ] P2196 and P5796 `Diameter` with no unit (fixed 2026-10-26); P6229 has a unit but no diameter
  - [ ] 12 rows where `CapacityBOEd` failed to convert: P0185, P4000, P4483, P5502, P5503, P6039, P6709, P8110, P8214, P8225, P8228, P8328
  - [ ] Start or end country missing from `CountriesOrAreas` (P0205, P0316, P0328, P1325, P4267 and others)
  - [x] 5 `Wiki` values that do not start with `http`: a leading tab or space, stripped 2026-10-26 (P3620, P3657, P7685, P7686, P7687)
  - [ ] P1000 and P7999 mapped but null geometry (same as section 3)
  - [x] Copyright month and file-creation date, fixed 2026-10-26. `Copyright - GGIT` now says November 2026, and the exporter joins each row's cells so the `=TODAY()` date in column B reaches the file

## 9. Summary sheets

Notebook: `GGIT-pipelines-summary-sheets-Nov2026-release.ipynb` (already forked; a preview ran on the live backend 2026-09-02, see README).

- [x] Notebook forked from the June 2026 GOIT notebook, reads through `gem-db-ops`
- [ ] Repoint `SPREADSHEET_KEY` from the rolling backend to the snapshot
- [ ] Pipes-vs-ratios guard passes on the snapshot (it fired on the live backend in September)
- [ ] Run `Global`, then each regional tracker (`AsiaGasTracker`, `EuroGasTracker`, `AfricaGasTracker`, `LatinAmericaTracker`)
- [ ] Decide: capex tabs on the gas-only basis (default) or the historical all-fuel basis; note it in the release notes either way
- [ ] Totals plausible against Nov 2025; row counts and km agree with the step 7 downloads
- [ ] README updated with the snapshot run
- [ ] Commit notebook + README (data files stay gitignored)

## 10. Publish and wrap up

- [ ] Paste results into the published summary-tables workbook (`1NbEpGt2K5nY…`; per-edit approval)
- [ ] Distribute the download files. Note: `.gpkg`/`-shp.zip` cannot be committed from `data-files/` until a `.gitignore` negation is added (see repo CLAUDE.md)
- [ ] Hand the summary-sheet workbooks to whoever writes the report/brief
- [ ] Add `2026-q4-gas-pipelines/` (and the other 2026 Q4 folders) to the folder map in the repo `README.md`
- [ ] Note anything that went wrong this round and fix the tooling or the root checklist
