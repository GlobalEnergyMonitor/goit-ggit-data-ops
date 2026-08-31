# Backend tracker QC (during the update cycle)

Checks the **live backend Google Sheet** while researchers are still working in
it — the during-the-update counterpart to `releases/qc/`, which checks the
finished download files. Catching a bad status or a value in the wrong column
here means the researcher who entered it is still on that country; catching it
at release time means re-exporting everything.

Everything lives in one module, `tracker_qc.py`. It is both the CLI and the
engine behind `updates/<cycle>/mid-update-qc-sweep.ipynb`, so the notebook and
the headless run can't drift apart.

**Read-only.** This never writes to the sheet. Fixes are made by hand in the
sheet (or by the researcher who owns the country).

## Quick start

```bash
# live sheet, read-only, authenticated through gem-db-ops
python tracker_qc.py --tracker ggit --cycle-start 2026-07-06

# oil/NGL tab instead
python tracker_qc.py --tracker goit

# a CSV already pulled by gem-db-ops/ggit/pull.py (faster to iterate on)
python tracker_qc.py --csv ../../../gem-db-ops/ggit/gem_export_ggit.csv --tracker ggit

# hand the flagged rows to someone
python tracker_qc.py --tracker ggit --dump-rows findings.csv
```

Prints one line per check (`OK` / `NOTE` / `WARN` / `FAIL` / `SKIP`) grouped by
tier, then a summary ordered by row count, and exits non-zero if anything
FAILs. Needs `pandas` and `pip install -e ../../gem-tracker-constants`.

Reads go through `gem-db-ops/gem_sheets.py` (the `gws` CLI against
`~/.config/gws-gem`, read-only) — never a public export URL. Everything is
loaded as **strings**: QC has to see what is literally in the cell, including
the values that don't parse as numbers.

| Flag | Meaning |
| --- | --- |
| `--tracker {ggit,goit}` | which tab, and which schema to expect |
| `--csv PATH` | read a pulled CSV instead of the live sheet |
| `--header-row N` | header offset for `--csv` (default 2, what `pull.py` writes) |
| `--cycle-start YYYY-MM-DD` | enables the cycle-scoped checks (see tier 12) |
| `--dump-rows PATH` | write the FAIL + WARN rows, one row per (check, ProjectID) |
| `--levels FAIL,WARN` | which levels to print (default: all but OK) |
| `--today YYYY-MM-DD` | override "now", for reproducible runs |

## Levels

- **FAIL** — structurally wrong. It will corrupt a release, silently drop rows
  from it, or means a value is sitting in the wrong column. Fix these first;
  they are almost always cheap.
- **WARN** — a real gap or inconsistency to work through, but the release will
  still build.
- **NOTE** — informational: legacy backlog, distributions worth an eyeball,
  plausible-but-odd values, explicit placeholders.
- **SKIP** — the column this check needs isn't on this tracker's tab. Expected:
  GGIT has ~132 columns, GOIT ~107, and every check is presence-guarded so one
  codebase covers both.

Rows with no `Status` **and** no `PipelineName` are treated as reserved-ID
placeholders and excluded from the per-row checks — otherwise they fire every
required-field check at once and bury the real findings.

## The tiers

**0. Shape & identifiers.** Row counts, `ProjectID` present / unique / matching
`P<digits>`, fully empty rows. A malformed ProjectID is a FAIL: it has usually
been *overwritten* by a value meant for another column, which loses the ID.

**1. Vocabularies.** `Status` against `gem_tracker_constants.PIPELINE_STATUS`
and `Fuel` against the package's fuel buckets — the same buckets the release
export filters on, so a value outside them silently vanishes from the release.
Also the smaller vocabularies (`RouteType`, `RouteAccuracy`, `EuropeTracker`,
…), split into *normalizable* (case/whitespace only — safe to fix in bulk) and
*outside vocabulary* (needs a decision). Currency codes are checked against
ISO 4217; `CAN`→`CAD` and `RMB`→`CNY` are the recurring offenders.

**2. Types.** Numeric columns that don't parse, split into *multi-valued*
(`42,36,30` — a real convention in `Diameter`, so a WARN, not an error) and
genuinely non-numeric. Month columns that hold a year (FAIL — wrong column) or
a spelled-out month name. URL columns whose contents contain no URL. Scalar
columns containing a URL, a `LINESTRING`, or a date — the wrong-column
signature again.

**3. Derived columns.** Every converted column recomputed from its source and
units and compared: `LengthKnownKm`, `DiameterInMm`, `CapacityBcm/y`,
`StartYearEarliest`, `NumberOfCountries`. A disagreement is a FAIL — one of the
two is stale, and the release ships the derived one. Also `LengthMergedKm == 0`
while `LengthEstimateKm` holds a real number, which shadows a good estimate
with a zero.

**4. Status logic.** Each status against the milestone year it implies
(`shelved`→`ShelvedYear`, `cancelled`→`CancelledYear`, `retired`→`StopYear`,
construction→`ConstructionYear`, built→`StartYear1`), in both directions: the
year missing, and the year set on a row whose status no longer matches. Plus
in-development rows whose start year is already past, and operating rows whose
start year is in the future.

**5. Chronology.** Year columns inside `[1900, now+40]`, milestone ordering
(proposal ≤ construction ≤ start ≤ stop), the later year set with the earlier
one blank, and a month set with no year.

**6. Plausibility.** Order-of-magnitude bands on capacity, length and diameter,
zero and sub-1-km lengths, negatives, and capacity more than 25× its country
median. These are unit errors far more often than data errors.

**7. Duplicates.** Exact duplicates on name + segment + countries + status, and
near-duplicates: same name and country with lengths within 5%. Long pipelines
legitimately appear as several segment rows, so read these before deleting
anything.

**8. References.** Each value column against its `[ref]` column. Sheet-wide
sparseness is legacy backlog and reports as NOTE; the same gap on a row
stamped **this cycle** is a WARN, because that's work that just happened and is
still fixable with the person who did it. Plus the `Wiki` link.

**9. Geography.** Endpoint countries not listed in `CountriesOrAreas`, blank
region/subregion, and — the one that bites hardest — the same country carrying
two different region or subregion spellings across rows ("North Africa" vs
"Northern Africa", "West Asia" vs "Western Asia"). That splits a country in
two in any regional rollup.

**10. Cross-field.** Value/units pairs where one side is blank, route geometry
vs `RouteAccuracy`, hydrogen fields vs a hydrogen `Fuel`, PCI codes vs
`EuropeTracker`, owner names vs owner entity IDs, and rows whose `Fuel` says
they belong on the *other* tracker's tab (FAIL — the release reads the tabs
separately, so the row is either dropped or double-counted).

**11. Text hygiene.** Leading/trailing whitespace, doubled spaces, non-breaking
and zero-width spaces. Invisible, and they break every exact-match join.

**12. Staleness & cycle coverage.** `LastUpdated` parseable, not blank, not in
the future; rows untouched in over 12 months (scoped to in-development rows,
where status decay actually matters); researcher initials present. With
`--cycle-start`, the cycle rollups (per researcher, per country) and the
required fields on rows touched this cycle.

## Where fixes belong

Almost everything here is fixed **in the live sheet**, by the researcher who
owns the country — that's the point of running it mid-cycle. Exceptions:

- Derived-column disagreements (tier 3): re-run whatever produces the derived
  column. For lengths that is `route-lengths/`.
- Route geometry vs `RouteAccuracy` (tier 10): the geometry lives in the
  `goit-ggit-pipeline-routes` repo, not the sheet.
- A new legitimate value that a vocabulary check rejects: add it to
  `gem-tracker-constants` (edit its YAML and run its tests), never inline here.
