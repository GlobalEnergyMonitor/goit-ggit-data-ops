# Annual update cycle checklist

Step-by-step checklist for running a GOIT/GGIT annual update cycle — the
research phase where the live tracker sheet gets updated country by country.

```
Cycle:          2026-q3-gas-pipelines
Research window: 2026-07-06 → TBD (data freeze)
Update sheet:   TBD (create at spin-up: "Q3 2026 gas pipelines - update sheet")
Asana project:  TBD (create at spin-up)
Target release: 2026-11 (penciled in)
Run by:         Baird
```

---

## 1. Spin-up (before researchers start)

- [ ] Run (or copy-and-update) the year's allocation notebook in
      `updates/researcher-allocation/` — days-per-country estimates from the
      live sheet's project counts and each researcher's available days
- [ ] Create the **update sheet** in Drive, named
      `Q3 2026 gas pipelines - update sheet`. Structure (see the Q3 2025
      sheet as the model): one row per country/area with primary researcher,
      net research days, PRIORITY 1 (in-dev pipelines) status, PRIORITY 2
      (rest of data) %, counts checked vs. total by status bucket,
      days-to-complete estimates. Include the possible-updates and
      country-tips tabs
- [ ] Create the cycle **Asana project** and country tasks — structure and
      canonical subtask checklist are in [asana-templates.md](../asana-templates.md)
- [ ] Migrate carry-over: previous cycle's unfinished country tasks and
      anything relevant from the future-tasks project
- [x] Create the cycle folder here, copy this checklist in, fill the header
- [x] Set up `progress-snapshot.ipynb` and `mid-update-qc-sweep.ipynb` in the
      cycle folder; point their config cells at this cycle's sheets and start
      date (update-sheet key still TBD in both configs)
- [ ] Confirm the GEM-wide release template task exists in the Data Team
      Workplan for the target release (the "[PENCILED IN]" task) and dates
      still make sense

## 2. Onboarding (per researcher, as they join)

- [ ] **Isabel Mahon (2026-07-06)** — returning from the 2025 cycle; skip the
      beginner tutorials, confirm access + assignments
- [ ] Share the [training hub central doc](https://docs.google.com/document/d/133QLUsqsibX1JSsFsEFkHplB4Qz5LkhsFGmbQgFsV-U/edit)
      — new researchers start with the Genially tutorials; experienced ones
      skip to the workflows section
- [ ] Share the [Visual Dictionary: GGIT/GOIT](https://docs.google.com/presentation/d/1rr_zBDKqb9H_hhdpaczEWRR3t_JgtHtSaNVM3Jaql_Q/edit)
- [ ] Confirm edit access to the live tracker sheet and the update sheet
- [ ] Walk through: the update sheet (their countries, priorities), one Asana
      country task end-to-end (the subtask checklist), and how to stamp
      `Researcher` initials + `LastUpdated` on every row they touch
- [ ] Assign their country tasks in Asana (their section) and set rough
      sequencing/deadlines

## 3. During the update

- [ ] Run `progress-snapshot.ipynb` roughly weekly — per-researcher and
      per-country progress from the live sheet's `LastUpdated`/`Researcher`
      stamps; flag countries with no recent activity and re-balance
      assignments if someone is stuck or ahead
- [ ] Run `mid-update-qc-sweep.ipynb` periodically (at least monthly, and
      after any bulk change) — fuel/status/ProjectID sweeps plus data-entry
      checks on recently touched rows; fix findings **in the live sheet** now,
      while the researcher who made the change is still on the project
- [ ] Triage "QUESTIONS FOR BAIRD" subtasks in Asana as they accumulate
- [ ] Keep the update sheet's progress columns honest (researchers update
      them when finishing a country; spot-check against the snapshot output)
- [ ] Log recurring lessons in the country-tips tab and, if tooling/process
      broke, fix it (or this checklist) now

## 4. Wind-down and hand-off

- [ ] Each researcher writes a research summary (Asana pattern:
      "<Name> - 2026 research summary" task in the cycle project)
- [ ] Move unfinished country work and deferred ideas to the future-tasks
      Asana project so the next cycle starts from a clean list
- [ ] Final `mid-update-qc-sweep.ipynb` run comes back clean
- [ ] Agree the **data-freeze point** with everyone still editing
- [ ] Fill in the update sheet's "best estimate for NEXT update (days)"
      column while memories are fresh — next year's allocation notebook
      reads from it
- [ ] Hand off to the root [RELEASE-CHECKLIST.md](../../RELEASE-CHECKLIST.md)
      (its step 2 pre-flight assumes exactly this freeze)
