# route-lengths

Pipeline length + country-ratio calculation feeding two tabs of the backend
tracker sheet. See README.md for the layout and how to run it.

## Key facts

- **Never hardcode a country fix.** The predecessor notebook accumulated four:
  Hong Kong/Macao carved out of China by name, `Alaska` → `United States`,
  `Senkaku Islands` → `Japan`, and `Canary Islands` → `Morocco` but only on
  Nigeria-Morocco pipelines. All four are gone, and every one of them is now
  produced by a general rule. If a country comes out wrong, fix the rule or the
  `Country dictionary` row — do not add a remap.
- **Region is geographic, not sovereign** (decided 2026-07-31). An entity with
  its own dictionary row uses it; otherwise it takes the region of the nearest
  country polygon. Sovereignty inheritance is what made the Canary Islands
  special-case necessary, and it also gets Tromelin Island and Matthew and
  Hunter Islands wrong. Named joint areas are never collapsed to one party.
- **The `Country dictionary` tab (sheetId 610217930) is pipelines-only**
  (confirmed 2026-08-02) — adding, deleting or re-regioning rows there affects
  the pipeline trackers and nothing else. Don't confuse it with the two
  `... (imported for ref.)` tabs beside it, which are read-only IMPORTRANGE
  mirrors of GEM's naming sheet; the "THIS IS IMPORTED INTO THE TERMINALS
  SHEET" banner belongs to `Region dictionary (imported for ref.)`, not here.
  Row 1 is the header, 1 frozen row, data starts at row 2, 18 columns, no
  formulas anywhere, kept sorted by column A.
- **All 328 EEZ polygons must resolve.** `prepare_boundaries.py` raises if any
  don't, because an unresolved polygon silently drops kilometres. Fix the
  dictionary rather than relaxing the check.
- **Google Sheets access goes through `sheets_client.py` only.** The
  `gem-analysis` service account is deleted; `gem_tracker_constants.sheets`
  and `GDRIVE_API_CREDENTIALS` are dead everywhere. Reads use the `gws` CLI
  (`~/.config/gws-gem`, read-only), writes `~/.config/gws-gem-write`. Do not
  import pygsheets here.
- **Runs are manual, and that is load-bearing.** The routes-repo dispatch
  trigger was dropped 2026-07-31. Because nothing runs unattended, the write
  path can use the work account's own interactive OAuth token — no service
  account, no repo secret. Never put the `gws-gem-write` token in CI: it
  carries Drive/Gmail/Calendar scope for the whole work account.
- **The two output tabs are the one approved auto-write carve-out** in this
  repo — and only those two. `prepare_boundaries.py --apply-dictionary-diff`
  can write the `Country dictionary` tab, but it is *not* covered by that
  carve-out and needs explicit per-edit approval every time, as does anything
  else on the sheet.
- **The dictionary tab is positional, so its writer simulates first.** Rows are
  grouped by Region/SubRegion (alphabetical within group, not sorted by name)
  and three rows carry manual cell formatting, so edits move rows with
  insert/`deleteDimension` rather than rewriting the grid. `simulate_dictionary`
  replays the whole request sequence locally and the write aborts unless the
  result matches the expected table exactly — one off-by-one in a positional
  insert silently shifts every row below it. When a block is split, resolve the
  *cheapest* split first: moving "everything not in the largest run" relocated
  31 rows when the real fix was to move the 2 interlopers.
- **The dictionary change set is diffed against the live tab, not declared.**
  `ALIAS_FIXES`/`DEAD_ROWS`/`REGION_FIXES` state the intent; every section of
  `--emit-dictionary-diff` filters them by what the sheet still needs, so a
  re-run after a successful write prints `NOTHING PENDING` and plans a no-op
  instead of re-proposing applied work. Keep it that way — a diff that always
  reports the constants can't tell you whether the write landed.
- **The output tabs have structure a plain values.update destroys**: 28 columns
  of per-row formulas, a banded range, frozen panes, stale filter ranges, and a
  pre-existing broken `#REF!` in column X that must be left alone. The writer
  sizes the grid, fills formulas by `copyPaste`/`PASTE_FORMULA`, resizes banding
  and filters, then writes values — in that order. `sheet_writer.py`'s docstring
  is the record of why each step exists.
- **The manual paste workflow left the ratios tab ragged**: as of 2026-07-31 the
  G:AH formulas stopped at row 6754 while data ran to 6861, so 107 pipelines had
  no Region/SubRegion/StartCountry/… That is the concrete failure this replaces.
  The default `--fill-formulas all` repairs it, and did on 2026-08-03 — formulas
  now run to the last data row. Expect it to recur if anyone pastes by hand again.
- **The header row moves.** `Country dictionary` lost a banner row on
  2026-08-02, shifting its header from row 2 to row 1 and breaking a hardcoded
  `header_row=2`. `find_header_row` now locates it by looking for a known
  column name; don't reintroduce a literal row number.
- `boundaries-*.gpkg` is a build artifact and is gitignored; `boundaries.json`
  and `boundaries-attribution.csv` are committed deliberately (explicit
  negations in the repo `.gitignore`) as the provenance record.
- Route files with `"geometry": null` are normal placeholders, ~1,100 of them.
  They are not errors; those pipelines fall through to the known-length path.
