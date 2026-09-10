# GGIT LNG Terminals — summary sheets, September 2025 (reproduction)

Reproduces the eleven published LNG tabs in the official GEM summary-tables workbook
from the September 2025 LNG Terminals release download.

This folder is a **validated baseline to fork for the Q4 2026 release** (mid-to-late
October 2026). It is not a production run — it re-derives an already-published
deliverable so that the method lives in code instead of in a mix of pivot tables and a
retired notebook.

## Files

| File | Tracked? | What it is |
|---|---|---|
| `GGIT-LNG-summary-sheets-Sep2025-reproduction.ipynb` | yes | the notebook, September snapshot; outputs committed as a release record |
| `GGIT-LNG-summary-sheets-Oct2025-reproduction.ipynb` | yes | same method, October snapshot — the fork that reproduces the owner tabs |
| `GEM-GGIT-LNG-Terminals-2025-09.csv` | no (gitignored) | the September 2025 release download |
| `GEM-GGIT-LNG-Terminals-2025-10.csv` | no (gitignored) | the `owners all corrected` export of 2025-10-23 |
| `published-2025-09-reference.json` | no (gitignored) | all eleven published tabs, for validation |
| `GGIT-LNG-summary-sheets-*2025-reproduction.xlsx` | no (gitignored) | notebook output |

## The published workbook mixes two snapshots

The eleven published tabs were **not** all built from the same data, which is why no single
input reproduces all of them. Two snapshots exist, identical in schema (1,206 rows × 73
columns) and in unit-ID set, differing in 204 `Owner` and 51 `Parent` values plus three US
export capacity edits:

| Tab family | Built from | Result |
|---|---|---|
| capacity by country/area and region | September download | residuals are published-side errors only |
| operating capacity by start year | either — unaffected by the diff | **exact on both** |
| capacity by owner | the 2025-10-23 `owners all corrected` export | **exact on both tabs** |
| capex | September download, via the retired Colab cost notebook | **restated** — see the floating fix |

The three capacity edits that separate them are all United States export units, and they
postdate the capacity pivots: Rio Grande T5 (Phase 2) `proposed 5.4` → `construction 6.0`,
CP2 Phase 1 `10.0` → `14.4`, CP2 Phase 2 `10.0` → `13.6`. Running the October snapshot
therefore *worsens* the capacity tabs by exactly those edits (US proposed −1.83,
construction +10.41) while fixing the owner tabs completely.

So: **run both notebooks.** Take the capacity and start-year tabs from the September run
and the owner tabs from the October run. For 2026 this problem disappears — there will be
one snapshot — but the lesson carries: pull the owner data and the capacity data at the
same moment, or the published tabs will not tie out.

## Re-pulling the inputs

Both inputs are gitignored. Reads are authenticated through `gws-gem` (read-only);
never use an anonymous export URL.

```bash
# the release download — the flat data the October 2025 pivots were built on
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-gem \
GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file \
gws sheets values get --params '{"spreadsheetId":"<pivot-workbook-key>",
  "range":"LNG Terminals!A1:BU1207","valueRenderOption":"UNFORMATTED_VALUE"}'

# the published tabs, one call per tab, same valueRenderOption

# the October snapshot — spreadsheet titled
# "lng-export-2025-10-23T173749 - owners all corrected", tab "LNG Terminals"
gws sheets spreadsheets values get --params '{"spreadsheetId":"<owners-corrected-key>",
  "range":"LNG Terminals!A1:BW1207","valueRenderOption":"UNFORMATTED_VALUE"}'
```

For **2026, do not re-pull from the pivot workbook.** Pull through `gem-db-ops`
instead — that is the single source of truth for LNG:

```bash
python ../../../../gem-db-ops/lng/pull.py
```

Mind the column names: the all-fields Postgres export uses `TerminalID`/`UnitID` where
the 2025 download uses `ProjectID`/`UnitID`.

## Inputs

One row per **unit**, not per terminal — an export terminal with three trains is three
rows. Every published tab sums unit capacity, so unit grain is correct throughout. The
only place terminal grain matters is the capex cost sample, which dedupes on `ProjectID`.

## Fuel bucket

`Fuel == "LNG"` only. This drops the nine NH3 / LH2 / eLNG rows that share the tracker
(1,206 rows in the download → 1,197 LNG rows).

## Statuses

Eight, stored lowercase in the tracker: `proposed`, `construction`, `shelved`,
`cancelled`, `operating`, `idled`, `mothballed`, `retired`.

`gem-tracker-constants` disagrees — its `TERMINAL_STATUS` says **`Idle`** where both the
tracker and the published tables say **`Idled`**. The notebook flags this rather than
working around it; the fix belongs in that package's `statuses.yaml`.

## Terminal-level capacity fallback

Capacity is the sum of unit-level `CapacityinMtpa`. Some terminals carry no unit-level
capacity at all — the figure is only recorded once, on the terminal, in
`TotExportLNGTerminalCapacityinMtpa` / `TotImportLNGTerminalCapacityinMtpa`. **Where every
unit on a terminal is blank, take the single terminal total instead.** Commonwealth LNG is
the worked example: six blank export units, 9.5 mtpa on the terminal.

`apply_capacity_fallback()` implements this by appending one synthetic row per qualifying
terminal, so the ordinary group-and-sum downstream needs no special case. The synthetic
row also carries `TotKnownTerminalCostsUSD` into `CostUSD` when no unit on the terminal
carries a cost. It is flagged `FromTerminalTotal` and **excluded from the capex tabs** —
there the terminal cost is already spread across the real units, so the synthetic row would
double-count one unit's share.

Two terminals qualify in September 2025:

| Terminal | Type | Country | Blank units | Fallback |
|---|---|---|---|---|
| Commonwealth LNG Terminal | export | United States | 6 | 9.5 mtpa |
| Tabeer LNG Terminal | import | Pakistan | 2 | 5.7 mtpa |

The rule fires only when **every** unit is blank. Twenty-two further terminals have *some*
blank units; in all twenty-two the unit sum already equals the terminal total, so falling
back there would double-count. This is a general rule, not a 2025 fact — **it carries over
to 2026 unchanged**, and the notebook prints each terminal it fires on.

## How each tab is built

### Capacity by country/area and by region (4 tabs)

Sum of `CapacityinMtpa` by row label and status, matching the October 2025 pivot specs
(rows = `Country/Area` or `SubRegion`, columns = `Status`, values = SUM `CapacityinMtpa`,
filters on `FacilityType` and `Fuel`). Rows that are zero across every status are
dropped, as the published tabs do.

`In Development` is derived as `Proposed + Construction`, so it cannot desync. `Total` is
likewise derived, not carried.

The pivots emit **subregions only**. The `Region` column and the empty-subregion rows in
the published tabs were added by hand at paste time; the notebook rebuilds that scaffold
from the download's own `Region`/`SubRegion` pairing.

### Operating capacity by start year (1 tab)

Rows = `ActualStartYear` floored at 1980, columns = `FacilityType`, filtered to
`Fuel = LNG` and four built statuses. **Reproduces the published values exactly, all 47
rows.**

Two caveats to carry into 2026:

- the 1980 floor drops ~182.7 mtpa of earlier capacity, so the `Total` row is **not**
  total built capacity;
- the tab is titled *"Operating LNG capacity by start year"* but the pivot filter admits
  `idled`, `mothballed` and `retired` as well. The title is wrong, not the data —
  verified against the pivot spec.

### Capacity by owner (2 tabs)

Ownership is one string per unit — `"Parent A [60.0%]; Parent B [40.0%]"` — so each unit's
capacity is split across parents by the stated fractions. Unlabelled parents split the
unclaimed remainder evenly. Units carrying **no** `Parent` at all are bucketed as
`unknown`, not dropped; the published tabs do the same, and those 12 import units are worth
18.88 mtpa cancelled and 10.51 mtpa proposed.

The tracker carries in-progress `[TO BE DELETED]` markers inside 37 parent names; these are
stripped, or those parents split into two rows.

Against the October snapshot **both tabs reproduce exactly** — no cell differs by more than
0.001, and no parent appears in the computation that is absent from the published tab.

One one-directional gap remains: 17 export / 73 import minority holders appear only in the
published tabs, because the retired notebook read the Sheet backend's
`Terminal operators/owners` tabs, which carry holders the flat `Parent` column does not.
Their capacity is already accounted for under the majority holders, so the totals still
tie; only the row list is shorter.

### Capex (4 tabs)

Transcribed from the retired Colab notebook that produced the published capex tabs
(`Summary table python code.ipynb`). All four reproduced **exactly** against the September
snapshot — no cell differed by more than 0.001 US$ bn — until the floating-unit fix below
was switched on (2026-09-03). They are now a **restatement** of the published tabs, and
`CAPEX_FIX_FLOATING = False` returns the original figures.

1. derive cost-per-mtpa as `CostUSD / CapacityinMtpa`, then overwrite it wherever
   `TotKnownTerminalCostsUSD` and the matching terminal total capacity both exist;
2. split the cost sample on `Offshore`, collapse each terminal to one datapoint carrying
   its mean, then trim each side to the 10th–90th percentile;
3. mean cost-per-mtpa per top-level `Region`, separately for onshore and floating,
   each falling back to the global mean below three datapoints;
4. estimate `capacity × regional cost-per-mtpa`, then override with unit `CostUSD`, then
   override again with `TotKnownTerminalCostsUSD / NumberOfUnits`.

Three details are load-bearing and none is obvious:

- **`CostUSDPerMtpa` is derived, not stored.** An earlier reading of this folder concluded
  the published capex depended on a cost column lost with the old Sheet backend. It does
  not — the column is computed from `CostUSD`, `CapacityinMtpa` and
  `TotKnownTerminalCostsUSD`, all of which the release download carries.
- **Order matters in step 4.** The terminal-level override lands *last*, so it beats a
  unit-level `CostUSD` on the same row.
- **The synthetic terminal-total rows are excluded here.** They are a capacity device; in
  capex they would add a second unit-share of `TotKnownTerminalCostsUSD` on top of the real
  units' shares — exactly +1.83 US$ bn on Commonwealth LNG and +0.25 on Tabeer LNG, which
  is what the last four residuals on each capex tab turned out to be.

### The floating-unit defect, and the fix (2026-09-03)

The source's estimate step tests `Floating == "yes"` while the column holds `True`/blank, so
it **never matched**: the floating rate table was computed and then never used, and every
FSRU was costed at its onshore regional rate. The source compounded this by forcing the
floating rates to the global mean while onshore used regional means — an unconditional
assignment where a sparse-sample fallback was intended.

`CAPEX_FIX_FLOATING = True` corrects both, and is now on. Floating units cost at their
region's floating rate, with the same `CAPEX_MIN_POINTS = 3` fallback to the global mean
that onshore uses. Set the flag to `False` to reproduce the tabs as first published; the
notebook's comparison cell prices both either way, so the alternative is never hidden.

What it moves, on the September snapshot (US$ bn, all statuses):

| | as first published | with the fix |
|---|---|---|
| export terminal capex | 1,938.6 | **1,962.8** (+24.2) |
| import terminal capex | 774.5 | **693.9** (−80.6) |

Import falls because floating import terminals are cheap per mtpa (Asia 144.6 US$M/mtpa
against an onshore Asia rate of 285.8) and there are many of them; export rises because
floating export is *expensive* (Africa 1,174.4 against an onshore 412.6). In development
alone: export 837.08 → 843.69 (Nigeria +6.17), import 155.65 → 135.97 (Brazil −4.59,
India −3.81, LAC −8.19 as a subregion).

One defect in the source method is still **reproduced deliberately**, because it is what
produced the published figures: the step-1 override is unconditional — the source has its
`& isna()` guard commented out — so a terminal-level ratio replaces a unit-level one even
where the unit ratio is the better number. Import runs after export, so import wins on a
terminal carrying both.

## The published tabs do not reconcile against themselves

With the fallback rule in place and no hand-entered deltas, every remaining capacity
difference is a published-side error. Three checks, using only published cells:

1. **`In Development` ≠ `Proposed` + `Construction`** on Germany (+5.0), Western Europe
   (+5.1), Northern America (−10.5), France (+0.2) and the Netherlands (+0.1). Proposed
   cells were edited and the derived cells never recomputed.
2. **The `Total` row ≠ the sum of its own data rows**, in all four capacity tabs. Totals
   were computed at one moment and individual cells edited afterwards.
3. **The region tab ≠ the country tab**, for the same underlying data. Northern America is
   0.9 higher in the export-by-region tab than its own United States + Canada cells;
   South-eastern Asia is 2.0 *lower* than its member countries. Nine smaller ±0.10
   mismatches on the import side.

Check 3 explains the last two residuals, and each cuts a different way. The Malaysia +2.0
is a hand edit applied to the **country tab only** — the published region tab agrees with
this notebook. The Northern America +0.9 is the reverse, a region-tab-only edit. In both
cases the reproduction sits on the side that reconciles.

None of the three can happen here: `In Development` and `Total` are derived, and both
geographies roll up from the same unit rows. All three are worth raising with the tracker
lead before the Q4 2026 run.

## Validation

The notebook diffs every computed tab against `published-2025-09-reference.json`
cell-by-cell. Every capacity residual traces to one of the three published-side errors
above. Tolerances differ by tab because the capacity and start-year tabs were
pasted as values rounded to 1 dp, while the owner and capex tabs carry full precision.

| Tab | September | October |
|---|---|---|
| export capacity by country/area | **3** — Malaysia ×2 + `Total` In Dev | 8 (+ the 3 US edits) |
| import capacity by country/area | **3** — France, Germany, `Total` In Dev | 3 |
| export capacity by region | **2** — Northern America ×2 | 6 (+ the 3 US edits) |
| import capacity by region | **2** — Western Europe, `Total` In Dev | 2 |
| operating capacity by start year | **0 — exact** | **0 — exact** |
| export capacity by owner | 27 | **0 — exact** |
| import capacity by owner | 9 | **0 — exact** |
| export terminal capex by country/area | 20 — restated | 39 (restated + the 3 US edits) |
| export terminal capex by region | 18 — restated | 26 (restated + the 3 US edits) |
| import terminal capex by country/area | 114 — restated | 114 — restated |
| import terminal capex by region | 64 — restated | 64 — restated |

Bold marks the snapshot each tab family should be read from. Read that way, **the seven
non-capex tabs reproduce exactly or to published-side error only**: the start-year tab and
both owner tabs cell-for-cell, and the four capacity tabs down to the three published-side
error classes above. The four capex tabs no longer match by design — the floating fix
restates them, and all four published capex tabs were rewritten to the restated figures on
2026-09-04 (2,997 cells across the six capex tabs in one batch, with the gas Melanesia fix;
Changelog rows added). Flip `CAPEX_FIX_FLOATING` to `False` to re-verify the original
reproduction.

## Tunable parameters

| Parameter | Value | Meaning |
|---|---|---|
| `FUEL` | `"LNG"` | excludes NH3 / LH2 / eLNG rows |
| `BUILT_STATUSES` | operating, idled, mothballed, retired | counted as built in the start-year tab |
| `START_YEAR_FLOOR` | `1980` | pivot's row floor; drops ~182.7 mtpa |
| `CAPEX_QLO`, `CAPEX_QHI` | `0.10`, `0.90` | quantile trim on the cost-per-mtpa sample |
| `CAPEX_MIN_POINTS` | `3` | datapoints needed for a regional mean |
| `CAPEX_FIX_FLOATING` | `True` | floating units cost at the floating rate, regionally |
| `CAPEX_FLOATING_ALWAYS_GLOBAL` | derived | `not CAPEX_FIX_FLOATING` — don't set it directly |
| `FLOATING_TRUE_TOKEN` | derived | `True` with the fix on, `"yes"` (dead branch) off |
| `TOL_ROUNDED` / `TOL_EXACT` | `0.06` / `0.001` | validation tolerances |

## Forking for Q4 2026

1. Copy this folder to `releases/summary-sheets/2026-q4-lng-terminals/`.
2. Repoint `DATA_CSV` at the 2026 pull from `gem-db-ops` (see above). Keep **one**
   snapshot for all eleven tabs — the September/October split documented here is the
   single biggest source of unexplained residuals, and it is avoidable.
3. Nothing to reset — the capacity fallback is a rule, not a list of 2025 deltas. Check
   the terminals it prints, though; the set will differ.
4. Drop `REFERENCE_JSON` and the validation section, or repoint it at the 2026 published
   tabs once they exist.
5. Keep `CAPEX_FIX_FLOATING = True` (it already is in the 2026 Q4 notebooks). The one
   remaining reproduced defect is the unconditional step-1 override — decide on it, and
   say so in the release notes either way, since it changes published-comparable figures.
6. Raise with the tracker lead: the self-reconciliation failures, the start-year tab's
   title, and the `Idle`/`Idled` drift in `gem-tracker-constants`.
