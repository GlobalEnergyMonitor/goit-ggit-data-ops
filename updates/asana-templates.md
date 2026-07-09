# Cycle spin-up templates — Asana, update sheet, Drive

How to set up the coordination infrastructure for a new update cycle. Copied
from how the Q3 2024 / Q3 2025 gas cycles actually ran.

## Asana project

Create one project per cycle in the globalenergymonitor.org workspace, named
`GGIT YYYY pipelines update (Qn)` (or GOIT equivalent). Previous cycles, for
reference and for copying structure:

- [GGIT pipelines update (Q3 2024)](https://app.asana.com/1/1200305284526705/project/1207590556245656)
- [GGIT 2025 pipelines update (Q3)](https://app.asana.com/1/1200305284526705/project/1209490578832845)
- [GGIT 2026 pipelines update - future tasks](https://app.asana.com/1/1200305284526705/project/1211318539684872)
  — standing carry-over project between cycles; also holds the master copies
  of the subtask templates below

### Sections

- One section per researcher: `RESEARCHERS - <FirstName>` (Chinese-language
  researchers historically grouped as `CHINESE RESEARCHERS - <FirstName>`)
- `RESEARCH SUMMARY (WHEN FINISHED)` — one "<Name> - <year> research summary"
  task per researcher, done at wind-down
- `unsorted/general/for next year` — parking lot; sweep into the future-tasks
  project at wind-down

### Country tasks

One task per country/area, named just the country (e.g. "Turkiye"), placed in
the assigned researcher's section. Each carries the standard subtask
checklist (master copies live in the future-tasks project):

1. Review relevant tasks for this country from previous updates
2. Check the possible updates sheet and incorporate changes/additions
3. **Update all in-development pipelines** (priority 1)
   - Confirm and/or update the status of each project with new research
   - Make sure all pink reference cells in the sheet have URLs where data
     is available
   - Add/update the route (or add as a subtask for batched work later)
   - Update the wiki page and reformat if needed
   - Update the Researcher initials and LastUpdated date
4. Research any missing in-development pipelines (check news, search
   engines, AI tools)
   - Add in-dev projects to sheet; fill in pink reference cells
   - Create wiki pages
   - Add a route (or add to "improve/add routes" for batched work later)
5. IF YOU HAVE EXTRA TIME (priority 2)
   - Check for any missing operating pipelines
   - Check operating, cancelled, idle, mothballed pipelines
   - Improve/add routes
   - Update/reformat wiki pages
6. Update your progress in the progress tracking sheet
7. Add to country tips tab
8. Mark country task complete
9. QUESTIONS FOR BAIRD — running list the researcher appends to; PM triages

## Update sheet (Drive)

Named `Qn YYYY <fuel> pipelines - update sheet`, by research quarter.
Model: [Q3 2025 gas pipelines - update sheet](https://docs.google.com/spreadsheets/d/1xK1qEj1uAsbyb1ekcFpjQzlHq_Nb2-fDuW9M7NCwiWI/edit).
Main tab columns (row 1 is a banner note; headers on row 2):

- `primary researcher`, `Qn net research days available`, additional researcher(s)
- `country/area (unique start+end)`, `region`, `subregion`
- `PRIORITY 1: Qn YYYY status (in-dev pipelines)` + `PRIORITY 1 REACHED?`
- `PRIORITY 2: Qn YYYY status (rest of data)` + `PRIORITY 2 %?`
- counts: in-dev / operating / cancelled-idled-mothballed, each with a
  "checked (YYYY update)" companion column
- days-to-complete estimates (faster/slower, for in-dev and rest-of-data) —
  seeded from `updates/researcher-allocation/`
- `last researcher (previous cycle)`, `additional notes`,
  `best estimate for NEXT update (days)`

Plus tabs: possible updates (leads to check per country) and country tips.

## Drive folder

The **release** Drive folder is created near the end of the cycle, named by
**release quarter** — e.g. "2025 Q4 - GGIT pipelines update"
([folder](https://drive.google.com/drive/folders/1xKsstvuTiPzIyAzUqufvbFPrzROULPh4)).
It holds the release snapshot sheet, exported downloads, summary-table
output, website-text docs, and the ownership-team and data-team hand-off
subfolders. Creating it is release work (RELEASE-CHECKLIST.md step 6), not
cycle spin-up — listed here only because the naming trips people up.

## Onboarding links (share with every new researcher)

- [GOIT/GGIT technical training guide — central document](https://docs.google.com/document/d/133QLUsqsibX1JSsFsEFkHplB4Qz5LkhsFGmbQgFsV-U/edit)
- [Visual Dictionary: GGIT/GOIT](https://docs.google.com/presentation/d/1rr_zBDKqb9H_hhdpaczEWRR3t_JgtHtSaNVM3Jaql_Q/edit)
- [Training and resources Drive folder](https://drive.google.com/drive/folders/10igMZ_AAoBYeERaXfoujpsC9wlns-0_H)
  (Genially interactive tutorials, QGIS/georeferencing/OSM workflows, video
  tutorials, OSINT resources)
