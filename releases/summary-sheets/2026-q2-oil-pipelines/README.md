
   292 NGL pipeline projects tracked
 0.112 M km tracked
    38 NGL pipeline projects in development (proposed + construction)
  11.1 K km in development



 1,634 Oil pipeline projects tracked
 0.487 M km tracked
   152 Oil pipeline projects in development (proposed + construction)
  32.4 K km in development


# GOIT pipelines summary sheets — June 2026 release

Methodology for the tables produced by `GOIT-pipelines-summary-sheets-June2026-release.ipynb`.

The notebook is run **once per fuel** (`FUEL_TYPE` ∈ `{"Gas", "Oil", "NGL"}`) and once per
`REGION_NAME` filter (`"Global"` or a tracker code such as `"AsiaGasTracker"`,
`"EuroGasTracker"`, `"AfricaGasTracker"`, `"LatinAmericaTracker"`). Each run writes a single
`GOIT-Summary-Sheets-{FUEL}-{YYYY-MM-DD}.xlsx` workbook containing the sheets listed below.

## Inputs

Loaded from the Google Sheet specified by `SPREADSHEET_KEY`:

- **`Gas pipelines`** / **`Oil/NGL pipelines`** — one row per pipeline project (`pipes_df_orig`).
- **`Country ratios by pipeline`** — one row per (pipeline, country) intersection
  (`country_ratios_df`). A multi-country pipeline contributes one row per country it crosses.
- **`Pipeline operators/owners`** — operator/parent strings per project.
- **`Parent metadata (3/3)`** — parent-company metadata (HQ country, etc.).
- **`Country dictionary`** — `Country → Region → SubRegion` lookup, plus tracker-membership
  flags (`AsiaGasTracker`, etc.).

`pygsheets` returns every cell as a string. The notebook coerces the columns listed in
`NUMERIC_COLS_PIPES` / `NUMERIC_COLS_RATIOS` to numeric at load time, stripping comma
thousands-separators (e.g. `"1,236.43"`) before `pd.to_numeric(errors="coerce")`. The `--`
and `""` placeholders are then replaced with NaN.

## Fuel buckets

The buckets come from the in-repo `gem-tracker-constants` package (`FUEL_CONFIG` just maps
`FUEL_TYPE` to the imported list):

| `FUEL_TYPE` | `Fuel` values included |
| --- | --- |
| `Gas` | `Gas`, `Gas and Hydrogen` (collapsed to `Gas`) |
| `Oil` | `Oil`; `Oil, NGL`; `Oil, NGL, naphtha`; `Oil, oil products`; `Oil, condensate` |
| `NGL` | `NGL`; `NGL, oil products`; `LPG`; `Condensate/NGL` |

The Oil and NGL buckets are disjoint: the dual-fuel strings `Oil, NGL` and
`Oil, NGL, naphtha` are classified as Oil (they're labeled `Oil` in the release downloads
too), so no pipeline is counted in both per-fuel summaries.

## Region filtering

`REGION_NAME = "Global"` includes every country. Any other value (e.g. `"AsiaGasTracker"`)
must match a column in the Country dictionary; only countries flagged `Yes` for that
column are kept. Filtering is applied to `country_ratios_df_touse` and `pipes_df_touse`,
both of which feed the per-country and per-region tables.

## Sheets

### 1. `Kilometers by region`

Sum of `LengthMergedKmByCountry` from `country_ratios_df_subset` (= fuel × region filtered),
grouped by `Region`, `SubRegion`, and `Status`, reshaped wide so each status is a column.

- An `in development (proposed + construction)` column is added between `construction`
  and `shelved`.
- A `Total` row sums every region's km.
- Zero cells are blanked out for display.

### 2. `Kilometers by country`

Same calculation as the regional table, grouped by `Country` instead of `Region/SubRegion`.
Countries with zero km in every status are dropped (no point listing them).

### 3. `Kilometers by owner`

Each pipeline carries a `Parent` cell like `"TC Energy Corp [60%]; Sempra Energy [40%]"`.
The notebook splits this into one row per parent, with `FractionOwnership` parsed from
the bracketed percentages:

- empty / NaN `Parent` → one row attributed to `"unknown"` with `FractionOwnership = 1.0`
- non-researched QCC parents — a CJK character with `[100.00%]` suffix — are kept verbatim
  (no semicolon split, no further parsing)
- if some parents are missing a percentage but others have one, the leftover fraction
  `1.0 − sum(known pcts)` is divided evenly across the parents without a percentage
- if **no** percentage is given, every parent gets `1 / len(parents)`

`KmOwnership = FractionOwnership × LengthMergedKmByCountry` is then summed per
`(Parent, Status)` and reshaped wide. A `Total` row sums all parents' km in each status.

### 4. `Kilometers by start year`

For each year between `min(1980, data minimum)` and `max(2025, data maximum)`:

- **operating** column = sum of `LengthMergedKm` for pipelines whose `Status == "operating"`,
  grouped by `StartYearEarliest`
- **construction** column = same for `Status == "construction"`, grouped by `ConstructionYear`
- **proposed** column = same for `Status == "proposed"`, grouped by `ProposalYear`

Rows missing the relevant year column are excluded — they do not form a NaN group, they
are dropped before grouping. A `Total` row sums each column.

### 5. `Cost per km by region`

Mean `CostUSDPerKm` per `Region`, expressed in **USD millions per km**.

Source set: `ratios_with_cost`, the rows of `country_ratios_df` for the chosen fuel bucket
that satisfy all of

1. `CostUSDPerKm` is populated
2. `LengthKnownKmByCountry` is populated
3. `CostUSDPerKm` falls strictly between the 2.5% and 97.5% global quantiles
   (drops a handful of extreme outliers on both tails)

The means are computed **globally** — they ignore `REGION_NAME`. Narrowing the cost
estimation to a single tracker would leave too few datapoints in each subregion, so the
filter is only applied at the final capex pivot.

**Sparse-sample fallback.** A region with fewer than `MIN_REGION_DATAPOINTS` unique
pipelines (or no datapoints at all) is replaced by the **global** mean
`CostUSDPerKm`. The `DataPoints` column is preserved so you can see how many unique
projects fed each row.

### 6. `Cost per km by subregion`

Same method as the regional table, grouped by `SubRegion`.

**Sparse-sample fallback** (after the regional fallback runs). A subregion with fewer
than `MIN_SUBREGION_DATAPOINTS` unique pipelines (or no datapoints) is replaced by
the mean for its parent region. Because the region's mean may itself have been replaced
by the global mean in the previous step, a subregion in a sparse region effectively
inherits the global value.

### 7. `Capex USD billions by region`

`CostUSDEstimate` is computed on every row of `country_ratios_df_subset`:

- **Default**: `CostUSDEstimate = LengthKnownKmByCountry × subregion_mean_cost_per_km`
  where `subregion_mean_cost_per_km` comes from the table in sheet 6 (after fallbacks).
- **Override**: if the row already has both a `LengthKnownKmByCountry` *and* a
  `CostUSDPerKm` populated on the pipeline itself, that row's estimate is overwritten
  with `LengthKnownKmByCountry × CostUSDPerKm` (the actual project cost takes precedence
  over the regional average).

`CostUSDEstimate` is then summed by `Region`, `SubRegion`, `Status` and **divided by
1e9** so the table is denominated in **USD billions**. An `in development` column
(`proposed + construction`) is added; a `Total` row sums every region.

### 8. `Capex USD billions by country`

Same calculation as sheet 7, grouped by `Country` instead of `Region/SubRegion`.
Countries with zero capex in every status are dropped; zero cells are blanked out.

## Tunable parameters

All live in the top-of-notebook config block or the cost cell:

| Parameter | Default | Effect |
| --- | --- | --- |
| `FUEL_TYPE` | `"Oil"` | Which fuel bucket to release |
| `SPREADSHEET_KEY` | June 2026 GOIT key | Source Google Sheet |
| `REGION_NAME` | `"Global"` | Country filter for the per-country/per-region tables (regional cost means stay global) |
| `OUTPUT_DIR` | `Path.cwd()` | Where the Excel workbook is written |
| `RELEASE_AS_PUBLISHED` | `False` | `True` restores the `5` thresholds this release shipped at |
| `MIN_REGION_DATAPOINTS` | `3` (shipped at `5`) | Region cost mean falls back to global below this |
| `MIN_SUBREGION_DATAPOINTS` | `3` (shipped at `5`) | Subregion cost mean falls back to region below this |
| `qlo_val` / `qhi_val` (inline) | `0.025` / `0.975` | Outlier trim window for `CostUSDPerKm` |

## The datapoint threshold: shipped at 5, restated to 3

This release **ran** both thresholds at `5`; an earlier draft of this README said `3` for
the subregion one, which was never what the notebook executed. The standing rule is **3**
for both (set 2026-09-02, extended to every tracker 2026-09-03; see
`../2026-q4-gas-pipelines/README.md` section 4), and the notebook now carries `3` — so it
no longer reproduces the shipped tables. `RELEASE_AS_PUBLISHED = True` brings the `5`s
back. Unlike the gas side — where the 3-vs-5 choice is a no-op — it binds here:

| Table | Sample size | Ran at 5 | Under the standing 3 |
|---|---|---|---|
| Oil, South-eastern Asia | 4 | inherits Asia (3.07) | own mean, 1.24 |
| Oil, Southern Europe | 4 | inherits Europe (2.54) | own mean, 0.97 |
| NGL, Northern Africa | 3 | inherits Africa (2.12) | own mean, 0.52 |
| NGL, Eastern Europe | 4 | inherits Europe (2.12) | own mean, 0.96 |
| NGL region, Africa | 3 | inherits global (2.12) | own mean, 0.52 |
| NGL region, Europe | 4 | inherits global (2.12) | own mean, 0.96 |

Oil Western Europe (1) and the NGL Oceania region (1), plus every 0-datapoint subregion,
fall back under either threshold. The two restated NGL *regions* cascade: their
0-datapoint subregions (Sub-Saharan Africa, Northern/Southern/Western Europe) inherit the
restated regional figure rather than the global one.

Note the direction. Relaxing 5 → 3 lets thin samples publish their own mean, and here every
such sample is **cheaper** than the tier above it, so the restatement lowers capex — by
0.6% on oil operating and 11% on NGL operating. That is the rule working as specified (a
3-pipeline mean is publishable, a 2-pipeline mean is not), not an argument for the number 5;
but NGL Northern Africa at US$0.52M/km off three pipelines is the thinnest published average
in either tracker and is worth a sanity check at the next release.

### Restated on 2026-09-04

Verified first: with `RELEASE_AS_PUBLISHED = True` the repointed notebook (see below)
reproduces the published wiki cost-per-km table exactly, all 22 oil values.

Global capex, US$ bn, as shipped → restated:

| status | Oil shipped | Oil restated | NGL shipped | NGL restated |
|---|---|---|---|---|
| proposed | 54.94 | 54.75 | 15.19 | 14.99 |
| construction | 43.29 | 43.29 | 6.43 | 5.49 |
| **in development** | **98.23** | **98.03** | **21.62** | **20.48** |
| shelved | 18.63 | 17.08 | 0.35 | 0.35 |
| cancelled | 186.22 | 185.91 | 2.88 | 2.31 |
| operating | 1,053.69 | 1,047.41 | 182.92 | 162.26 |
| idle | 12.93 | 12.74 | 0.33 | 0.33 |
| mothballed | 14.32 | 14.32 | 3.62 | 3.62 |
| retired | 54.74 | 54.53 | 0.15 | 0.15 |

Country movements are confined to the six restated levels: on oil, Greece, Italy, Spain,
Portugal, Albania, North Macedonia, Serbia, Brunei, Cambodia, Indonesia, Malaysia and
Myanmar; on NGL, Algeria, Egypt, Libya, Tunisia, Belgium, France, Germany, the Netherlands
and Russia. Everything else is unchanged to the cent.

**Where the restatement landed:** the wiki's Oil section
([GGIT and GOIT cost estimates](https://www.gem.wiki/GGIT_and_GOIT_cost_estimates)) — prose
"fewer than five data points" → "three", plus the two changed oil subregion values.
**Nowhere else, because there is nowhere else:** the published GOIT summary-tables workbook
([`1OYH6D7c…`](https://docs.google.com/spreadsheets/d/1OYH6D7c-D0FsL5GzBGijtkmvQCTkBUclj-UVoOieUFo/edit))
carries only km tabs — km by country/area, region, owner and start year — and has never
published a capex tab, for any GOIT release. The capex tables of this release exist only in
the per-run `.xlsx` (gitignored) and in the wiki table. The `Pipeline capex estimates by …`
tabs in the *other* workbook (`1NbEpGt2K5nY…`) are GGIT gas, not GOIT, and were restated
separately.

## Reads go through `gem-db-ops`, not `pygsheets` (2026-09-04)

The load cell used `pygsheets.authorize(service_account_env_var="GDRIVE_API_CREDENTIALS")`,
which died with the `gem-analysis` service account on 2026-07-31 — this notebook could not
run at all between then and the restatement. It now reads via the sibling `gem-db-ops` repo
(read-only `gws-gem` profile): `read_tab_values(title, SPREADSHEET_KEY)`, wrapped in a
`load_sheet` that keeps the old loader's contract (formatted-value strings, rows padded to
the widest, all-blank trailing rows dropped).

**Call the library, never the `gem_sheets.py` CLI.** The CLI silently ignores `--sheet-key`
for its four registered tab titles — `"Oil/NGL pipelines"` among them — and hands back the
rolling backend instead of the snapshot. The library call takes an explicit key.

Repointing also surfaced a latent break: the header offsets had drifted to the **rolling
backend** while `SPREADSHEET_KEY` still named the June 2026 snapshot. `Country ratios by
pipeline` was being read at `start="A2"`, correct for the backend since it gained an A1
run-stamp row on 2026-08-05 but one row low for this snapshot, which put a data row in the
header and raised `KeyError: 'Status'` downstream. Now `start=None`. The committed notebook
could not have reproduced its own release even with working auth. **Re-point the key and the
offsets together, never one without the other.**
