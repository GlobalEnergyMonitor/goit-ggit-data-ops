# GGIT gas pipelines — summary sheets, November 2026 release

Production run for the November 2026 GGIT gas-pipelines release. Builds the gas tabs of the
official GEM summary-tables workbook
([`1NbEpGt2K5nY…`](https://docs.google.com/spreadsheets/d/1NbEpGt2K5nY0XTSB_vlOyw9Ug8ZmvvOaRPuO9TgISIw/edit)).

The method is documented in full in `../2026-q2-oil-pipelines/README.md` — **read that
first.** This folder is a fork of the notebook validated there, with the same eight sheets,
the same fuel buckets, the same cost model, and the same tunable parameters. Only three
things differ, all described below: how the Sheet is read, how the header row is found, and
**the capex tabs are now fuel-filtered**.

## Files

| File | Tracked? | What it is |
|---|---|---|
| `GGIT-pipelines-summary-sheets-Nov2026-release.ipynb` | yes | the notebook; committed output-free until the real run |
| `GGIT-Summary-Sheets-Gas-{YYYY-MM-DD}.xlsx` | no (gitignored) | notebook output, one per run |

## Running it

Set the three knobs in the config cell, then Restart & Run All:

- `FUEL_TYPE` — `"Gas"` for this release. (`"Oil"` / `"NGL"` still work; that's the GOIT run.)
- `SPREADSHEET_KEY` — **must be repointed at the Nov 2026 snapshot before publication.** It
  currently points at the rolling live backend (`1foPLE6K…`) so the notebook can be
  previewed mid-cycle, and prints a loud warning while it does. Past snapshots are listed in
  the config cell for reference.
- `REGION_NAME` — `"Global"`, or a tracker code (`"AsiaGasTracker"`, `"EuroGasTracker"`,
  `"AfricaGasTracker"`, `"LatinAmericaTracker"`). One run per region.

`MIN_REGION_DATAPOINTS` / `MIN_SUBREGION_DATAPOINTS` (both `3`) sit in the cost cell rather
than the config cell — they are a standing methodology rule, not a per-run knob. See
[section 4](#4-a-cost-average-needs-at-least-3-datapoints) before changing either.

## What differs from the June 2026 GOIT notebook

### 1. Reads go through `gem-db-ops` / `gws`, not `pygsheets`

The `gem-analysis` service account was deleted on 2026-07-31, so
`pygsheets.authorize(service_account_env_var="GDRIVE_API_CREDENTIALS")` — the load cell in
every pre-August notebook — cannot work. This notebook reads through the sibling
`gem-db-ops` repo instead, which wraps the read-only `gws-gem` profile:

```python
sys.path.insert(0, str((Path.cwd() / "../../../../gem-db-ops").resolve()))
import gem_sheets
gem_sheets.read_tab_values(title, sheet_key)
```

**Call `read_tab_values(title, sheet_key)` directly. Do not route these reads through the
`gem_sheets.py` CLI:** `--sheet-key` is silently ignored for its four registered tabs
(`Gas pipelines`, `Oil/NGL pipelines`, `Pipeline operators/owners`, `Hydrogen pipelines`),
because `resolve_tab` returns a `SheetTab` that already carries `PIPELINES_SHEET_KEY` and
`pull_tab` uses that in preference to the flag. Asking the CLI for a snapshot silently
hands back the rolling backend. This produced a ~1.2% error before it was spotted; the
notebook avoids the CLI entirely.

Only three tabs are read: `Gas pipelines`, `Country ratios by pipeline`, and
`Country dictionary`. The June notebook's input list also names `Pipeline operators/owners`
and `Parent metadata (3/3)`; neither is needed, because the km-by-owner sheet is built from
the `Parent` column on the ratios tab.

### 2. The header row is detected, not pinned

The June notebook used pygsheets' `start="A2"`/`"A3"` offsets, and its own comments record
that those drifted twice in a month (the ratios tab gained an A1 run-stamp row on
2026-08-05; the Country dictionary lost its banner on 2026-08-02). `read_tab` instead scans
the first eight rows for one containing a required set of column names, and raises a
`KeyError` naming the missing columns if it can't find one. A banner row appearing or
disappearing upstream no longer shifts every column silently. Against the live backend on
2026-09-02 it resolved to rows 2 / 1 / 0 respectively.

Column renames across releases are handled the same way, via `COLUMN_ALIASES`: the backend
renamed `Countries` → `CountriesOrAreas` between the Dec 2024 and Nov 2025 snapshots, and
either name resolves to the canonical one.

### 3. The capex tabs are fuel-filtered — **not comparable with published tables**

This is the one deliberate methodology change, and it matters for anyone comparing releases.

Published GGIT gas capex tables through the **November 2025** release summed **every fuel**
into the "gas pipelines" capex tabs — oil, NGL, LPG, CO2 and naphtha rows included. The
cause was in the Nov 2025 notebook (`../2025-q4-gas-pipelines/…-costs.ipynb`, cells 70 and
72): the `CostUSDEstimate` assignment and the capex pivot both ran on the unfiltered
`country_ratios_df`, while the kilometre tabs in the same notebook correctly used the
gas-only `country_ratios_fuel_df`. So the km tables were gas; the capex tables were all
pipelines.

The June 2026 GOIT notebook already fixed this by pivoting on `country_ratios_df_subset`,
and this fork inherits the fix. Size of the effect, recomputed from the release snapshots:

| Release | figure | as published (all fuels) | gas only |
|---|---|---|---|
| Nov 2025 | US in-development capex, US$ bn | 82.82 | 65.05 |
| Nov 2025 | global in-development capex, US$ bn | 714.6 | 554.1 |
| Dec 2024 | US in-development capex, US$ bn | 48.80 | 35.54 |
| Dec 2024 | global in-development capex, US$ bn | 762.0 | 513.4 |

The last code cell before the save (`SHOW_UNFILTERED_CAPEX = True`) prints both bases plus a
by-fuel breakdown of what the old method was picking up, so the delta goes into the release
notes rather than being rediscovered. Set it to `False` to skip.

**Flag this in the release notes.** A year-on-year comparison against any published gas
capex figure before the 2026 tables is apples-to-oranges.

### 4. A cost average needs at least 3 datapoints

**Standing rule, set 2026-09-02:** no published cost-per-km average may rest on fewer than
3 unique pipelines. `MIN_REGION_DATAPOINTS = MIN_SUBREGION_DATAPOINTS = 3`; a level below
the threshold inherits the tier above it (subregion → region → global) instead of
publishing its own mean. The two constants are one rule split by tier — keep them in step.

The case that prompted it: Nov 2025 applied no threshold at all, only a fallback for
subregions with *zero* datapoints, and so published **Melanesia at US$0.48M/km off a single
pipeline** against Oceania's US$2.68M/km — a fivefold understatement carried into that
release's capex. The June 2026 GOIT notebook did have thresholds, but at 5/5, and its
README documented the subregion one as 3; that mismatch is now resolved in favour of 3.

Scale of the effect: on both the Nov 2025 snapshot and the current backend, **no subregion
sits in the 3–4 datapoint band** — the smallest non-zero samples are Melanesia (1) and then
South-eastern Asia (8) — so the threshold binds only on Melanesia, Micronesia and Polynesia,
and the choice between 3 and 5 is numerically a no-op today. It is a policy guard against
the next thin subregion, not a change to current figures.

**Applied retroactively to Nov 2025 on 2026-09-04.** Global in-development capex moved
554.1 → 554.8, all of it Papua New Guinea (0.15 → 0.86), and Melanesia's cost per km
0.48 → 2.68. Rewritten in the published summary tables (`Pipeline capex estimates by
region` / `… by country/area`, plus a Changelog row), the wiki cost-estimates page, and
`../2025-q4-gas-pipelines/dashboard-refresh/`. Every Nov 2025 figure quoted elsewhere in
this README is the **pre-restatement** no-threshold basis — read 554.1 as 554.8, 396.2 as
396.9, 350.8 as 351.9 and 3,774.0 as 3,775.5 when comparing against the published tables.

June 2026 oil/NGL was restated the same day, and there the rule moves real money in the
other direction — six sparse levels stop inheriting and publish their own, cheaper means,
taking oil operating capex 1,053.7 → 1,047.4 and NGL operating 182.9 → 162.3 US$ bn. See
`../2026-q2-oil-pipelines/README.md`.

The `DataPoints` column is preserved in both `Cost per km by …` tabs, and the notebook
prints each suppressed subregion with its sample size, so the rule is auditable per run.

## Run of 2026-09-02 — live backend, corrected basis

Executed end to end against the **live rolling backend** (`1foPLE6K…`), not a release
snapshot, to get current capex on the fixed fuel-filtered basis. Provisional, not
publishable — see the guard note below. 4,353 gas rows → 4,314 after the row and fuel
filters; 7,112 ratio rows; 299 countries; 152 countries with non-zero capex; 1.517 M km
tracked; 896 projects / 211.5 K km in development. Output:
`GGIT-Summary-Sheets-Gas-2026-09-02.xlsx` (gitignored).

Global capex, US$ bn, gas only, compared with the Nov 2025 release **recomputed on the same
gas-only basis** (not the published all-fuel numbers):

| status | Nov 2025 (gas only) | live 2026-09-02 | delta |
|---|---|---|---|
| proposed | 396.2 | 425.1 | +28.9 |
| construction | 157.9 | 164.2 | +6.3 |
| **in development** | **554.1** | **589.3** | **+35.3** |
| shelved | 108.2 | 110.8 | +2.6 |
| cancelled | 350.8 | 341.4 | −9.4 |
| operating | 3,774.0 | 3,800.0 | +26.0 |
| idle | 9.2 | 9.4 | +0.2 |
| mothballed | 40.1 | 40.8 | +0.7 |
| retired | 13.1 | 14.9 | +1.8 |

Largest country movements in in-development capex, US$ bn: United States 65.05 → 82.76
(+17.7), Kazakhstan 11.53 → 22.51 (+11.0), China 84.73 → 92.73 (+8.0), Russia 61.95 → 67.19
(+5.2); India 29.85 → 23.99 (−5.9) and Iran 27.40 → 23.27 (−4.1) fell.

Two caveats on reading those deltas:

- **They mix project changes with cost-model recalibration.** The trimmed cost window moved
  (2.5%/97.5% quantiles 140,433 / 19,991,836 at Nov 2025 vs 134,910 / 18,641,825 today), so
  every subregional mean per-km cost shifted slightly and every estimated row moved with it.
  A country whose pipelines didn't change can still show a small delta.
- **The US now reads 82.76 on the gas-only basis, against 82.82 published for Nov 2025 on
  the all-fuel basis.** That near-identity is a coincidence of two offsetting changes and
  will be misread as "no change" by anyone comparing the two published tables. The
  like-for-like move is 65.05 → 82.76, a 27% increase in US gas-pipeline capex.

The pipes-vs-ratios consistency guard **fires** on the rolling backend (proposed +78 km,
construction +202 km, operating +1,168 km against a 25 km tolerance). That is the guard
working, not a notebook bug — the ratios tab is regenerated as part of cutting a release, so
mid-cycle the two tabs legitimately disagree, and the figures above inherit that gap. The
run above was executed with errors allowed so the downstream cells would still produce the
tables. It must pass on the Nov 2026 snapshot before anything is published; if it doesn't,
the backend ratios refresh hasn't run. The failure output names the offending pipelines,
which on the live data are mostly duplicate/renamed pairs that cancel out.

## Open before publishing

- Repoint `SPREADSHEET_KEY` at the Nov 2026 snapshot and confirm the guard passes.
- Decide whether the gas capex tabs ship on the corrected gas-only basis (default here) or
  the historical all-fuel basis, and note the choice in the release notes either way.
- The notebook never writes to Google Sheets. Pasting results into the published workbook
  needs explicit per-edit approval.
