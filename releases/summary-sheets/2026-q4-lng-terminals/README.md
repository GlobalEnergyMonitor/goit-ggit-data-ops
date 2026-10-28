# GGIT LNG Terminals — summary sheets, Q4 2026 release

Production run for the Q4 2026 LNG Terminals release (mid-to-late October 2026). Builds the
eleven LNG tabs of the official GEM summary-tables workbook.

The method is documented in full in `../2025-q3-lng-terminals/README.md` — **read that
first.** This folder is a fork of the notebook validated there; only the input, the id-column
handling and the (optional) validation section differ. Read against the snapshot each tab
family was actually built from, all eleven 2025 tabs reproduce exactly or to
published-side error only.

## Files

| File | Tracked? | What it is |
|---|---|---|
| `GGIT-LNG-summary-sheets-2026Q4.ipynb` | yes | the notebook; committed output-free until the real run |
| `GEM-GGIT-LNG-Terminals-2026-q4.csv` | no (gitignored) | the 2026 pull |
| `published-2026-q4-reference.json` | no (gitignored) | published tabs, once they exist; optional |
| `GGIT-LNG-summary-sheets-2026Q4.xlsx` | no (gitignored) | notebook output |
| `make_flourish_csvs.py` | yes | builds one CSV per LNG dashboard Flourish chart; see below |
| `flourish-csvs/*.csv` | no (gitignored) | its output |

## Dashboard CSVs for Flourish

`python make_flourish_csvs.py` runs the notebook's code cells up to "Write the workbook" and writes one CSV per chart listed in the "Flourish figure locations" tab of the dashboard text doc, with exactly the columns each chart binds. Because it reuses the notebook's frames, the dashboard carries the same fallback and capex numbers as the summary tables. `--upload` updates the CSV files in the Drive folder "LNG dashboard (current)" through `gws-gem-write`, then writes the same values into the Google Sheet of the same name without ".csv", and prints each Sheet's published CSV link. Flourish reads those Sheets, not the CSV files: in each chart's Data tab, "Import from URL" takes the Sheet's `.../pub?output=csv` link. A Drive CSV link does not work, because Drive serves the file as a generic download and Flourish rejects anything not served as CSV. The nine Sheets were made and published to the web on 2026-10-22 with "republish on change" on, so writing into the same Sheet keeps its link and the published CSV catches up within about two minutes. A refresh needs no clicking in Flourish beyond its own reload schedule. A chart with no Sheet yet gets one made from its CSV, set to Calibri 10pt, and published. Values are written as typed text, so the published CSV matches the local file exactly. Ask before running it. The four highlight numbers are typed into Flourish number charts rather than bound to data, so `lng-dashboard-28357206-highlights.csv` is a reference for retyping them. The map file replaces only the map's points sheet; its lines and regions sheets are the basemap. Two numbers differ from the 2026-10 dashboard text doc on purpose (decided 2026-10-22): "cancelled or shelved since 2022" is 590 mtpa, not 584, because it counts Tabeer LNG's 5.7 mtpa terminal total under the fallback rules, the same way operating capacity counts Tianjin LNG; and the capex table's Total row is rounded from the full sum, so it can sit 0.1 off the sum of the rounded rows.

## Pulling the input

Through `gem-db-ops`, the single source of truth for LNG — not a Sheets tab:

```bash
python ../../../../gem-db-ops/lng/pull.py --out GEM-GGIT-LNG-Terminals-2026-q4.csv
```

That export differs from the 2025 release download in two ways the notebook handles: it
names the id column `TerminalID` rather than `ProjectID`, and it carries a UTF-8 BOM. The
load cell renames the column, reads with `utf-8-sig`, and asserts on a required-column list
so a schema change fails loudly instead of silently producing wrong totals.

Smoke-tested against a current `gem-db-ops` pull (1,281 rows → 1,257 LNG): runs clean, all
eleven tabs written.

The pull's six cost columns were repaired on 2026-08-28 and now reproduce the website's
all-fields download **byte-for-byte** — see `gem-db-ops/docs/ALL_FIELDS_STATUS.md`. Coverage
went from `CostUSD` 251 rows / `TotKnownTerminalCostsUSD` 335 to 494 / 700, which is exactly
what the website carries. The capex cost sample roughly doubled as a result (466 unit-level
cost/mtpa values → 659 after the terminal override; 209 onshore + 85 offshore terminals after
the trim), so the regional means differ from any run made before that date. Re-run rather
than reusing earlier capex output.

## What carries over from 2025

- **The terminal-capacity fallback follows four rules agreed with the tracker lead on 2026-10-21**, applied per terminal and facility type (the notebook's fallback cell spells them out): (1) if any unit has a nonzero capacity, use the unit sum, even when other units are zero or blank and even when it disagrees with the terminal total; (2) if every unit is zero or blank and all share one status, add the terminal total once under that status; (3) if every unit is zero or blank and statuses differ, add it to no status, because the split is unknown; (4) take NH3 / LH2 / eLNG unit capacity off the terminal total first, because the tracker adds it in. In the start-year tab the synthetic row takes the latest start year among its units. Against the 2026-10-19 pull it adds **two import terminals** and leaves out none: Tabeer LNG (Pakistan, 2 shelved units, 5.7 mtpa, the same case as 2025) and Tianjin LNG, Beijing Gas Group (China, 3 operating units, 5.0 mtpa). Tianjin's phases started in 2023, 2024 and 2024, so its 5.0 mtpa counts in 2024 in the start-year tab. Commonwealth LNG, the 2025 worked example, has since been consolidated into one unit carrying 9.5 mtpa, so the fallback no longer fires there.
- **Terminal totals are not a reliable check on the unit sum.** On the 2026-10-19 pull, 8 terminal groups differ from their own unit sum. The three import ones (Fos Tonkin, Wilhelmshaven, Brunsbüttel) are exactly their NH3 units, which the tracker adds into the LNG total; the tracker lead is sending that to the data team. Of the five export ones, only Papua New Guinea LNG is explained by status (its terminal total equals its operating units only). Das Island (6.70 vs 6.00), Argentina LNG (27.95 vs 30.00) and Aurora Spassk-Dalny (0.04 vs 0.03) are unexplained, and Papua LNG has one blank unit with a unit sum of 4.99 against a total of 5.6. Under rule 1 none of these change the tabs, which sum units.
- **Blank `Parent` values bucket as `unknown`**, they are not dropped. This matched the
  published tabs exactly in 2025.
- **The start-year tab's title is wrong**, not its data: it says "Operating" but includes
  idled, mothballed and retired. Its 1980 floor also means `Total` is not total built
  capacity.
- **`gem-tracker-constants` says `Idle`** where the tracker says `Idled`. The cross-check
  cell reports this; it is not fixed.

## Open before publishing

1. **The floating-unit defect is fixed from this run forward — say so in the release notes.**
   The method was transcribed from the retired cost notebook bugs included, so that 2025
   ties out. One of those bugs is now corrected: `CAPEX_FIX_FLOATING = True` (2026-08-28)
   makes FSRUs cost at the **offshore** regional rate instead of the onshore one, and lets
   offshore use regional means the way onshore already does. The old branch tested
   `Floating == "yes"` against a column holding `True`/blank, so it never fired.

   | in-development capex, US$ bn | import | export | total |
   |---|---|---|---|
   | A published defect (all onshore) | 170.0 | 818.3 | 988.4 |
   | B token fixed → global offshore | 152.4 | 823.8 | 976.2 |
   | C token + regional offshore (**this notebook**) | 158.3 | 823.6 | 981.9 |

   Import falls in every region (Asia −7.1, Europe −3.5, world −11.7 bn); export is
   near-flat because most large export units carry a reported cost that overrides the
   estimate. 167 import units (498.6 mtpa) and 40 export units (156.6 mtpa) are repriced.
   The comparison cell prints all of this every run, so the pre-fix figure stays
   available — **capex tabs from this release are not comparable with earlier published
   ones**, and that belongs in the release notes. Set the flag to `False` to reproduce them.

   The *other* transcribed defect — the unconditional terminal-level `CostUSDPerMtpa`
   override — is still in place, undocumented rather than clearly wrong. Decide separately.
2. **Use one snapshot for all eleven tabs.** The 2025 published workbook mixed a September
   pull for the capacity tabs with an October `owners all corrected` pull for the owner
   tabs; that single fact caused most of the unexplained 2025 residuals.
3. **Validation is inert** until `REFERENCE_JSON` points at published 2026 tabs. A skipped
   validation is not a passed one.
4. Raise with the tracker lead: the 2025 published capacity tabs do not reconcile against
   themselves (stale `In Development` cells, `Total` rows that do not equal their own data
   rows, and region tabs that disagree with their own country tabs).

The notebook never writes to Google Sheets. Pasting results into the published workbook
needs explicit per-edit approval.
