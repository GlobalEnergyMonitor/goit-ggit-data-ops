# SOP: summary tables, dashboard, and wiki after a pipeline data release

The repeatable procedure for everything that sits on top of a pipeline release (GGIT gas, GOIT oil/NGL): the interim draft workbook, the official summary tables, the Flourish dashboard, the wiki cost-estimates page, and the topline points for communications. `RELEASE-CHECKLIST.md` covers producing the data itself (QC, lengths, ownership, snapshot, downloads). This document picks up at step 9 of that checklist and goes through publishing.

Worked example: the Nov 2026 gas release, `summary-sheets/2026-q4-gas-pipelines/`. Where this SOP says "the first time we did it" something was learned that is worth keeping.

Standing rules that apply to every step:

- Read Google Sheets and Drive only through the `gws` CLI (`gws-gem`, read-only). Never the Drive connector, never public CSV URLs.
- Every Sheets or Drive write (draft workbook, published workbook, Flourish source Sheets, snapshots) and every wiki edit needs explicit approval first, one action at a time. Preview, then ask.
- The notebook never writes to Sheets. Writers are separate scripts.
- Fix data problems at the source (the tracker Sheet or the routes repo), never in a notebook cell or by hand-editing outputs.

## 0. Before you start

- [ ] Release folder exists: `summary-sheets/YYYY-qN-<tracker>/`, with `CHECKLIST.md` copied from `RELEASE-CHECKLIST.md` and its header filled in.
- [ ] Note the Drive folder for the release update (the "YYYY QN - <tracker> update" folder). The snapshot, the draft workbook, and any Flourish source Sheets live there.
- [ ] Open the previous release's folder and workbook as the reference for tab layout and numbers.

## 1. Interim snapshot (any time before ownership or other data is final)

Use this when you want real numbers early. It is not the release snapshot.

1. Refresh lengths if the tracker changed since the last run: `python route-lengths/route_lengths.py --dry-run --sheet-key <live key> --out-dir <scratch>` and read the reconciliation. If pipelines were added, removed, or changed length, run again with `--write` (approval needed, it writes the live tracker's two length tabs and verifies afterward).
2. Copy the live tracker into the release Drive folder (`gws-gem-write drive files copy`, approval needed). Name it `Copy of <tracker name> - <month> <day> <year> interim snapshot (pre-<what is missing>)`.
3. Record the key in the release `CHECKLIST.md` and in the notebook (next step).

The final snapshot is the same procedure after all data is final (checklist step 6). Everything below is rerun against it.

## 2. Summary notebook

1. Open the release notebook (copy last release's in if this is a new release; checklist step 9).
2. Set `SPREADSHEET_KEY` to the snapshot key. Do not leave it on the rolling backend.
3. Run once per region: `REGION_NAME` = `Global`, then each regional tracker code. Global output goes next to the notebook, each regional run into `regional/<code>/`, because the file name is the same for every region.
4. Read the run output: the pipes-vs-ratios guard must pass (25 km tolerance). A failure means the data disagrees with itself. Fix the cause at the source. First time we did it, the cause was a `CountriesOrAreas` value written `Egypt,Cyprus` with no space after the comma, which the notebook's `", "` split drops.
5. Confirm the cost cell reported its suppressed subregions (fewer than 3 datapoints inherit the tier above, standing rule).
6. Keep the committed notebook output-free. Commit the notebook, README, and scripts. Workbooks stay gitignored.

Checks before trusting any output:

- Km totals by status agree with the release downloads (they filter on the same `gem-tracker-constants` buckets).
- Compare against the previous published release. Chase every large mover (a country or region changing by more than about 10%) back to its rows before it goes in a headline.

## 3. Draft workbook

The draft is where everyone looks at numbers before the official workbook changes.

1. Copy the last published summary workbook into the release Drive folder (approval needed). Name it as a draft.
2. Dry run: `python draft-workbook/write_draft.py dry`. It checks headers, reports the cell ranges and any stale rows it would clear. Then run it for real (approval needed). It writes the gas tabs and the cost per km tab, sets the A3 banner to DRAFT (and "provisional" on the owner tab while parent research is unfinished), and writes values only.
3. Fix formatting, which the script does not set. The script writes values only, so the old tab's formatting stays where it was, and when the new table is a different length the old formatting lands on the wrong rows. Check every tab, especially the bottom, and compare against the same tab in the published workbook. Target look:
   - Only the Total row is gray and bold. Nothing above it except the header is gray, and nothing below it is formatted.
   - A black line sits directly above the Total row on every tab that has one, gas and LNG, across the table's width. It is the top border of the Total row (`updateBorders`, `SOLID`, black).
   - The capex by country/area tab is the exception: the Country column (C) is gray and bold on every row by design, and Region and Subregion are merged cells that span their rows. Rows below Total must be plain white with no merges.
   - Font is Calibri on every gas tab, banner included, with sizes 16 for the title and 12 for rows 2 to 4 (tracker name, date, GEM link) kept as they are, and everything from row 5 down at 9 (on Changelog and Region definitions the banner is rows 1 to 3, so row 4 down is 9). The published workbook is a mix of Calibri and Arial (Arial is the Sheets default), so set Calibri on the draft with one `repeatCell` per tab limited to `userEnteredFormat.textFormat.fontFamily`, which leaves bold alone. A new tab (for example cost per km) follows the same sizes. Set body size with one `repeatCell` per tab from the first row after the banner, limited to `userEnteredFormat.textFormat.fontSize`. Do the same on the published workbook at the final publish step, with approval. For both workbooks the whole pass (Calibri on every visible tab, plus the Total-row line) was run as one `batchUpdate` on 2026-11-17, skipping the hidden `calc` and `calc-` helper tabs.
   How to fix a stale tab, with one `batchUpdate` per tab (write approval, per-action):
   - Find the Total row: the row whose A or C cell reads "Total".
   - Copy the format of a normal data row (`copyPaste` with `PASTE_FORMAT`) onto every stale row between the last real data row and Total. This clears leftover gray, bold, and borders in one step.
   - Add a `SOLID` black top border to the Total row (`updateBorders`) on the tabs that have one.
   - For rows below Total: `unmergeCells` on each stale merge (the exact merged range, a partial range is rejected), then a `repeatCell` setting white background and bold off, and `updateBorders` with `NONE`. Sheets rejects a `copyPaste` source outside the grid, so copying from a far empty row fails on a short tab.
   - Rescan the tab to confirm one gray Total row. A quick scan reads each row's background, bold, and borders through `spreadsheets get` with `includeGridData`.
   The Nov 2026 gas draft needed all of this: two gray country rows and a stray line on km by country, nine gray rows on km by owner, a gray 2025 row on km by start year, and twelve gray merged rows below Total on capex by country/area.
4. Spot-check totals against the notebook and compare the headline numbers with the previous release.
5. Leave the LNG tabs, `calc` helper tabs, Region definitions, and Changelog alone.

## 4. Publish the official summary tables (once data is final)

1. Re-run steps 1 to 3 on the final snapshot.
2. Copy the final tabs into the published workbook (approval needed, one per edit), remove the DRAFT banner text, and add a Changelog row.
3. Hand the workbook to whoever writes the report or brief.

## 5. Flourish dashboard

The gas dashboard follows the LNG pattern in `summary-sheets/2026-q4-lng-terminals/` (`make_flourish_csvs.py` and its README).

1. One CSV per Flourish chart, with exactly the columns that chart's data table expects. Gas has no script yet: write `make_flourish_csvs.py` in the release folder, reusing the notebook's code cells up to the workbook write, the way the LNG script does.
2. Check each CSV against the draft workbook before uploading.
3. `--upload` writes the CSVs and the published Sheets that Flourish reads (`gws-gem-write`, approval each time). Only data already public in the chart goes in those Sheets. Refresh them in place so links never change. Never publish a working or backend Sheet.
4. Open the dashboard in Flourish and confirm every chart refreshed.

## 6. Wiki cost-estimates page

Page: https://www.gem.wiki/GGIT_and_GOIT_cost_estimates

1. Source the figures from the final published summary tables, not the interim draft.
2. Use `gem-wiki/gemwiki.py` and `wiki_query.py`. Never hand-roll a session, user agent, or auth path.
3. Read the current page text, build the new text, and show a preview diff. A wiki edit needs explicit per-edit approval.
4. Edit, then reload the page and check that the new numbers match the published tables.
5. The first time we did this for a release, record here what the page's structure is and which sections each release rewrites. This is not written down yet. Fill it in on the Nov 2026 update.

## 7. Topline points and graphics for communications

1. Pull three headline findings from the final tables. Check each against the table, not a rounded memory.
2. Per idea, name the chart, the CSV that feeds it, and the one-sentence takeaway.
3. When another tracker's numbers are quoted (for example LNG figures in a joint email), verify them against that tracker's published summary sheets.
4. Dates for the next release go in the Asana release task.

## 8. Wrap-up

- [ ] Update the release `CHECKLIST.md` and README with what was run, on which snapshot, with the results.
- [ ] Note anything that went wrong or was confusing and fix this SOP while it is fresh.
- [ ] Update `RELEASE-CHECKLIST.md` if a step changed.
- [ ] Commit notebook, README, and scripts. Do not push without asking.

## Scripts and where they live

| Script | Location | What it does |
|---|---|---|
| `route_lengths.py` | `route-lengths/` | lengths and country ratios; dry run by default, `--write` pushes to the tracker |
| release notebook | `summary-sheets/<release>/` | builds the summary workbook from the snapshot |
| `write_draft.py` | `summary-sheets/<release>/draft-workbook/` | pastes the Global workbook into the draft Sheet; `GXLSX` env var overrides the input |
| `find_cell.py` | same folder | small `gws` helper the writer imports |
| `make_flourish_csvs.py` | LNG release folder (gas: to write) | one CSV per dashboard chart, optional `--upload` |
| `gemwiki.py`, `wiki_query.py` | `gem-wiki/` | the only wiki client |
