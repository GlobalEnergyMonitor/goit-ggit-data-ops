# 2026 Q3 — GGIT gas pipelines update (active)

The 2026 annual gas pipelines research cycle. Isabel Mahon starts 2026-07-06;
more researchers join through the following months. Target release is
penciled in for ~2026-11 (Asana "Prep for GGIT pipelines update - Q3 2026
[PENCILED IN]" in the Data Team Workplan: start 2026-10-09, due 2026-11-10).

Work through [CHECKLIST.md](CHECKLIST.md) (copied from
[../UPDATE-CHECKLIST.md](../UPDATE-CHECKLIST.md)).

## Cycle links

| What | Where |
| --- | --- |
| Live backend | "Pipelines (Gas/Oil/NGL) - main", key `1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek`, tab "Gas pipelines" |
| Update sheet | *to be created at spin-up* (`Q3 2026 gas pipelines - update sheet`; model: [Q3 2025 sheet](https://docs.google.com/spreadsheets/d/1xK1qEj1uAsbyb1ekcFpjQzlHq_Nb2-fDuW9M7NCwiWI/edit)) |
| Cycle Asana project | *to be created at spin-up* (structure: [../asana-templates.md](../asana-templates.md)) |
| Carry-over tasks | [GGIT 2026 pipelines update - future tasks](https://app.asana.com/1/1200305284526705/project/1211318539684872) |
| Previous cycle | [GGIT 2025 pipelines update (Q3)](https://app.asana.com/1/1200305284526705/project/1209490578832845) |
| Allocation math | [../researcher-allocation/researcher-allocation-for-2026.ipynb](../researcher-allocation/researcher-allocation-for-2026.ipynb) |

## Researcher roster (fill in as people join)

| Researcher | Start | Countries (see update sheet for full assignment) |
| --- | --- | --- |
| Isabel Mahon | 2026-07-06 | |

## Notebooks

- [progress-snapshot.ipynb](progress-snapshot.ipynb) — per-researcher /
  per-country progress from the live sheet's `Researcher` + `LastUpdated`
  stamps, optionally joined against the update sheet's assignments. Run
  weekly-ish. **Read-only.**
- [mid-update-qc-sweep.ipynb](mid-update-qc-sweep.ipynb) — during-data-entry
  QC on the live sheet: fuel/status/ProjectID sweeps
  (`gem-tracker-constants`) plus data-entry checks on rows touched this
  cycle. Run at least monthly and after bulk changes. **Read-only** — fix
  findings in the live sheet by hand.

Both notebooks still authenticate with `GDRIVE_API_CREDENTIALS` and the
`gem-analysis` service account, **which was deleted on 2026-07-31** — they will
fail until repointed at the `gws` CLI read path (see RELEASE-CHECKLIST.md step 1
and `route-lengths/sheets_client.py`). They also need
`pip install -e ../../gem-tracker-constants` (their first cell does this).
