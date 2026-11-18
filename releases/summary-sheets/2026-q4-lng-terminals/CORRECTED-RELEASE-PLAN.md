# Corrected October 2026 release: plan for summary tables and Flourish

Written 2026-11-17. On 2026-11-16 PB sent a corrected version of the October 2026 LNG Terminals release (Cameroon FLNG status and coordinates, Bahrain Hidd FLNG start years, stop years removed from 11 operating terminals). This plan covers what follows from it. Nothing past "Done so far" has been run.

## Done so far

- Corrected data checked against the 2026-10-19 pull: the 44 listed corrections applied to the pull reproduce the corrected xlsx on all 1,268 units (`GEM-GGIT-LNG-Terminals-2026-q4-corrected.csv`, gitignored).
- Notebook run on the original pull reproduces the October workbook, so the before and after comparison is clean. The corrections move 2.4 mtpa (Cameroon FLNG) from Operating to Idled in the export tabs and change the start-year tab for Bahrain Hidd (6.0 mtpa, 2019 to 2025). Import capacity and import capex tabs do not change.
- The "Copy of Copy" summary-tables Sheet in the Drive folder was updated on 2026-11-17 for the corrected release: 26 table cells and one Changelog row. It was read back and matches the corrected run. The tab subtitles still say "October 2026 release".
- A fresh database export from 2026-11-17 was compared. It carries the corrections except the 11 stop-year removals, plus five newer edits (new Polar LNG unit, Aguirre and Kangan moved to cancelled, a Papua New Guinea LNG terminal total change, owner changes). It is saved as `GEM-GGIT-LNG-Terminals-2026-q4-1117-export.csv` and is not the basis of anything yet.

## Decision gate: which data becomes official

Everything below waits on this. Decide with the tracker lead.

1. **Corrected release only.** The official data is PB's corrected files. The Sheet already matches. Go to the Flourish steps with `-corrected.csv` as the input.
2. **Corrected release plus the post-release edits.** The official data becomes a newer snapshot. The Sheet must be redone from the new export (all eleven tabs, plus owner-tab rows), the subtitles and Changelog reworded, and the data team must republish the xlsx and GIS files first. Use `-1117-export.csv` or a later pull as the input.
3. **Do not update the official data.** Revert the Sheet edits (the original values are in `GGIT-LNG-summary-sheets-2026Q4.xlsx`, the October workbook; the Sheet's version history also has them), leave the dashboard alone, and note the corrections for the next release.

Open questions for the data team whichever way it goes: the 11 stop-year removals are missing from the 2026-11-17 database export, so say whether the database or the export script is behind.

## Flourish steps (options 1 and 2)

The dashboard is built by `make_flourish_csvs.py`, which runs the notebook and writes one CSV per chart. Its README section explains how the Sheets feed Flourish.

1. Point the notebook's `DATA_CSV` at the chosen input. This is a one-line edit in the config cell. Re-read the notebook from disk first, since it may be open in Jupyter.
2. Run `python make_flourish_csvs.py` without `--upload`. It rewrites `flourish-csvs/*.csv` locally. Copy the current folder aside first so the old files can be diffed.
3. Diff every CSV against the October versions and list which of the nine chart files changed. Expected from the corrections: the export capacity over time chart, the export in-development and operating top-10 files only if Cameroon or Bahrain sit in them, the terminal map points file (Cameroon's coordinates moved offshore to about 2.87 N, 9.82 E), and possibly the highlights file. Confirm rather than assume.
4. Check the four highlight numbers in `lng-dashboard-28357206-highlights.csv`. They are typed into Flourish by hand, so any change needs a manual retype, and the dashboard text doc must match.
5. Show the diff and get approval. Then run with `--upload` (writes through `gws-gem-write`, one approval for the batch). The published Sheets keep their links, and the charts pick up the change on their own reload schedule.
6. Look at the live charts, especially the map, and confirm Cameroon shows as idled at its new position.

## Other places the numbers may appear

- The dashboard text doc and its "Flourish figure locations" tab, if any highlight number changed.
- The wiki and any briefing that quotes operating export capacity or Cameroon's status.
- The release notes: say the corrections were applied and that capex tabs were not otherwise recomputed.

## After the decision

- Update this README's "Open before publishing" list and the Changelog wording to match what was published.
- Send the data team the stop-year finding and, if option 1 is chosen, the list of post-release edits not included.
