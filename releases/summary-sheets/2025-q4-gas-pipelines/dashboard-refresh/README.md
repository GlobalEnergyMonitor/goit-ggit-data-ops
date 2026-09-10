# GGIT gas-pipelines dashboard — capex chart refresh

Drop-in replacement data for the two **capital expenditure** charts on the
[gas pipelines dashboard](https://globalenergymonitor.org/research/explore-global-gas-infrastructure-tracker-gas-pipelines-dashboard).

## Why

The dashboard's capex charts carry **December 2023** data (confirmed: their
in-development total of US$723 bn matches that release's published 722.98), and
they were produced with the same missing fuel filter that was found in the
Nov 2025 summary tables — oil/NGL/LPG/CO2/naphtha pipeline rows were pivoted
into a "gas pipelines" capex table. The published Nov 2025 summary tables were
corrected in place on 2026-09-02, and restated again on 2026-09-03 under the
standing >= 3 data point rule (Melanesia's single-pipeline subregional average
now inherits Oceania's); these files carry the same corrected basis to the
dashboard.

Note the km, owner and start-year charts on the same dashboard are **also**
Dec 2023 vintage, but they are *not* affected by the bug (the km tabs always
filtered on fuel correctly). Refreshing only the capex charts leaves the
dashboard internally mixed-vintage; refreshing all six is the cleaner option.

## Files

| File | Flourish viz | Layout |
|---|---|---|
| `dashboard_capex_table_nov2025.csv` | `28357294` (table) | `Region, Subregion, Proposed, Construction, Proposed + Construction` — 23 rows, region rows have a blank Subregion, `Total` last. Matches the existing chart's row order exactly. |
| `dashboard_capex_map_nov2025.csv` | `28357291` (choropleth) | `Country, CountryISO3166-1alpha-3, Category` — all 268 region rows in the existing chart's order, with the same five categorical bin labels. |

`Category` bins (unchanged from the existing chart, half-open intervals on
in-development capex): `US$0–1 billion`, `US$1–5 billion`, `US$5–10 billion`,
`US$10–50 billion`, `US$50–150 billion`. Every country the tracker does not
cover falls in the bottom bin, as in the existing chart.

The map CSV carries an extra fourth column, `InDevCapexUSDbn`, which the
existing chart does not bind. It is there for verification and as an optional
tooltip field — drop it if you want a byte-identical column set.

## Provenance

Both files are the gas-only (`Fuel in {Gas, Gas and Hydrogen}`) recomputation of
the Nov 2025 release snapshot, and reconcile to the corrected summary tables:
the table's `Total` in-development figure of **554.8** is the same number now in
the published `Pipeline capex estimates by region` tab. Regenerate with
`capex_lib.compute(..., gas_only=True, min_points=3)` (see
`../../2026-q4-gas-pipelines/README.md` for the methodology notes).

Headline changes from the Dec 2023 chart: global in-development capex
723 → 554.8; Sub-Saharan Africa 83.7 → 28.3; Northern America 106.4 → 72.1;
Northern Europe 13.4 → 1.2; Western Europe 16.5 → 5.9. The map's top bin is
unchanged in membership (China, Russia, United States). Melanesia carries 0.9
rather than 0.2 under the >= 3 rule (Papua New Guinea 0.15 → 0.86).

## Uploading

Requires a Flourish account with edit access to the GEM visualisations — the
CSVs are prepared, but the upload is a manual step in Flourish (open the viz,
Data tab, replace the sheet, keep the existing column bindings, Publish).
