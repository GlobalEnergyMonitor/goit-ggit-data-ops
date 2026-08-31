# GGIT LNG Terminals — summary sheets, **Asia only**, Q4 2026 data

An Asia-scoped cut of the eleven LNG summary tabs, built to supply numbers for a
colleague's South/Southeast Asia gas write-up (the Iran-conflict stress-test piece).
This is an **analysis cut, not a release artifact** — nothing here is published, and the
notebook never writes to Google Sheets.

The method is the global one. Read `../2026-q4-lng-terminals/README.md` and, behind it,
`../2025-q3-lng-terminals/README.md` first — every caveat there applies here unchanged.

## Files

| File | Tracked? | What it is |
|---|---|---|
| `GGIT-LNG-summary-sheets-Asia-2026Q4.ipynb` | yes | the notebook, outputs committed (summary-sheets convention) |
| `all-fields-2026-08-28T161944.csv` | no (gitignored) | full all-fields database download, 2026-08-28 — **the input** |
| `lng-export-2026-08-28T161950.csv` | no (gitignored) | the distributed LNG export of the same pull; not used |
| `GGIT-LNG-summary-sheets-Asia-2026Q4.xlsx` | no (gitignored) | notebook output, 14 sheets |

Both CSVs hold the **same 1,281 rows**. `all-fields` is the superset (115 columns vs 73)
and is the input, because it also keeps `Substatus` and the `[ref]` columns for
spot-checking a figure by hand. No fresh pull is needed to re-run.

## The one structural change: scope lands at pivot time

Everything before the pivots — the LNG fuel filter, the terminal-capacity fallback, the
parent ownership split, and above all the **capex regional rate fit** — runs on the full
world dataset. `in_scope()` is applied only when a tab is finally pivoted.

This is not stylistic. The capex rates are means over a global sample of terminals,
trimmed to the 10th–90th percentile. Filtering the input to Asia first refits them on a
smaller pool, which changes which terminals survive the trim:

| Asia onshore rate (US$/mtpa) | fitted on global sample | fitted on Asia-only sample |
|---|---|---|
| import | 280,928,023 | 263,473,206 (−6.2%) |
| export | 737,821,924 | 370,226,837 (−49.8%) |

Filtering at load would have halved every Asian export capex cell. The tabs here use the
global fit, so they stay comparable with the published global tabs.

## What's in the workbook

The eleven standard tabs, scoped to `Region == "Asia"` (all five UN M49 Asian
subregions), plus three extra sheets cutting **Southern Asia + South-eastern Asia** —
the write-up's actual subject — for import capacity, export capacity and capex.

`Total` rows are **Asia** totals, not world totals.

## Read before quoting a number

1. **Export capex is thin.** The Asia import rate rests on 113 sampled terminals; the
   export rate rests on **9**. Asian export capex is the least reliable figure in the
   workbook — quote it with a range, or not at all. The notebook prints the per-region
   sample counts so this stays visible.
2. **Capex is an estimate, not a reported total.** Every cell is either a reported cost
   or capacity × a regional rate, and most units carry no reported cost.
3. **The floating-unit defect is fixed here, and the published tabs still carry it.**
   The global notebook tests `Floating == "yes"` against a column that holds `True`/blank,
   so the branch never fires and FSRUs are costed at the *onshore* regional rate. That is
   wrong anywhere and badly wrong in an FSRU-heavy region, so this cut sets
   `CAPEX_FIX_FLOATING = True`: floating units take the offshore rate, and offshore uses
   regional means the way onshore already does. Asia's offshore import rate is
   145.2 M$/mtpa against 280.9 M$/mtpa onshore, so the fix pulls import capex down.

   | in-development capex, US$ bn | Asia import | Asia export | S+SE import | S+SE export |
   |---|---|---|---|---|
   | A published defect (all onshore) | 116.1 | 102.8 | 37.0 | 54.3 |
   | B token fixed → global offshore | 110.5 | 102.8 | 32.9 | 54.3 |
   | C token + regional offshore (**this notebook**) | 108.7 | 102.8 | 31.6 | 54.3 |

   Export barely moves: the estimate only prices units with no reported cost, and only
   3 Asian export units (2.7 mtpa) are both floating and uncosted, against 70 import
   units (214.9 mtpa). The notebook prints this table every run, so a
   published-comparable figure is always available — but **anything quoted from the capex
   tabs here is no longer directly comparable with the published global tabs**, and that
   has to be said alongside the number. Set the flag to `False` to reproduce them.

   The *other* transcribed defect — the unconditional terminal-level `CostUSDPerMtpa`
   override — is still in place. It is undocumented rather than clearly wrong.
4. **Validation is inert.** There are no published Asia tabs to diff against. The evidence
   the method is right is the 2025 global reproduction, not anything in this notebook.

## Finding: the global README's cost-coverage question is answered

`../2026-q4-lng-terminals/README.md` flags that the `gem-db-ops` pull carries far fewer
cost values than the 2025 release download (`CostUSD` 251 vs 437,
`TotKnownTerminalCostsUSD` 335 vs 613) and asks whether the database lost them.

It did not. This all-fields download carries **493** and **692** — more than either.
So `lng/pull.py` in `gem-db-ops` is mapping a narrower field. That's worth fixing there;
until it is, prefer the all-fields download for any capex work.
