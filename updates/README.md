# Annual update cycles

Workspace for the **annual update phase** of GOIT/GGIT — the months-long
research cycle in which researchers update the live tracker Google Sheet
country by country. This is the phase *before* a release: once the update
winds down and the data freezes, work hands off to the root
[RELEASE-CHECKLIST.md](../RELEASE-CHECKLIST.md).

One folder per cycle, named `YYYY-qN-<tracker>` by **research quarter**
(matching the `scripts/data-release-summary-sheets/` convention). Note the
mismatch to watch for in Drive: the release-artifacts Drive folders are named
by **release** quarter (e.g. "2025 Q4 - GGIT pipelines update" holds the
release built from the **Q3** 2025 research cycle).

```
updates/
├── UPDATE-CHECKLIST.md        reusable cycle checklist — copy into each cycle
│                              folder as CHECKLIST.md and check off as you go
├── asana-templates.md         how to spin up the cycle's Asana project, update
│                              sheet, and Drive folder; researcher onboarding links
├── researcher-allocation/     per-year allocation notebooks (days-per-country
│                              math that feeds the update sheet); formerly
│                              scripts/researcher-requests-scripts/
├── 2026-q1-oil-pipelines/     GOIT oil/NGL cycle (done; released June 2026)
└── 2026-q3-gas-pipelines/     GGIT gas cycle (active) — progress + QC notebooks
```

## What a cycle looks like

1. **Spin-up** — run the year's researcher-allocation notebook; create the
   update sheet, Asana project, and Drive folder (see
   [asana-templates.md](asana-templates.md)).
2. **Onboarding** — each researcher gets the training hub, the update sheet,
   and their Asana country tasks.
3. **The update itself** — researchers work country tasks; PM runs
   `progress-snapshot.ipynb` and `mid-update-qc-sweep.ipynb` (in the cycle
   folder) to track progress and catch data-entry issues early.
4. **Wind-down** — research summaries, carry-over to the future-tasks Asana
   project, data freeze, hand off to the release checklist.

Full detail: [UPDATE-CHECKLIST.md](UPDATE-CHECKLIST.md).

## Standing references

- **Live backend**: "Pipelines (Gas/Oil/NGL) - main" Google Sheet, key
  `1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek` (headers on row 3;
  `Researcher` initials + `LastUpdated` date are how cycle activity is stamped).
- **Training hub**: [GOIT/GGIT technical training guide — central document](https://docs.google.com/document/d/133QLUsqsibX1JSsFsEFkHplB4Qz5LkhsFGmbQgFsV-U/edit)
  in the [technical training and resources folder](https://drive.google.com/drive/folders/10igMZ_AAoBYeERaXfoujpsC9wlns-0_H).
- **Visual dictionary**: [Visual Dictionary: GGIT/GOIT](https://docs.google.com/presentation/d/1rr_zBDKqb9H_hhdpaczEWRR3t_JgtHtSaNVM3Jaql_Q/edit) (slides).
- **Fuel buckets / status lists**: the in-repo
  [gem-tracker-constants](../gem-tracker-constants/) package — cycle notebooks
  import from it, never re-declare lists inline.

## Past cycles (pre-dating this folder)

| Cycle | Update sheet | Asana project |
| --- | --- | --- |
| Q3 2024 gas pipelines | — | [GGIT pipelines update (Q3 2024)](https://app.asana.com/1/1200305284526705/project/1207590556245656) |
| Q3 2025 gas pipelines | [Q3 2025 gas pipelines - update sheet](https://docs.google.com/spreadsheets/d/1xK1qEj1uAsbyb1ekcFpjQzlHq_Nb2-fDuW9M7NCwiWI/edit) | [GGIT 2025 pipelines update (Q3)](https://app.asana.com/1/1200305284526705/project/1209490578832845) |
| Q1 2026 oil pipelines | [Q1 2026 oil pipelines - update sheet](https://docs.google.com/spreadsheets/d/1NH8pwFbV0RRAuv1BGwon63pMYpXOtMzf7NksI41ydLE/edit) | see [2026-q1-oil-pipelines/](2026-q1-oil-pipelines/) |

Carry-over work between gas cycles lives in
[GGIT 2026 pipelines update - future tasks](https://app.asana.com/1/1200305284526705/project/1211318539684872).
