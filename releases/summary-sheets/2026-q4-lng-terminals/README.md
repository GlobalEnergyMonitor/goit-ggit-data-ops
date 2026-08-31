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

- **The terminal-capacity fallback is a rule, not a 2025 fact** — where every unit on a
  terminal lacks `CapacityinMtpa`, it takes the single terminal total. Against a current
  pull it fires on **nothing**: Commonwealth LNG's six blank units, the 2025 worked example,
  have since been consolidated into one unit carrying 9.5 mtpa. The rule self-cancels when
  the data is clean. Check its printed output each run anyway.
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
