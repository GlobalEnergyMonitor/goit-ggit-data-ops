"""Write computed lengths and country ratios into the backend tracker sheet.

Run by hand, from a laptop, via the gws-gem-write profile. There is no CI path
and no automatic trigger -- see sheets_client.py.

What the writer has to respect
------------------------------
Both target tabs carry structure that a naive values.update destroys.

`Length estimates by pipeline` (sheetId 1069562947)
  * row 1 is a note; row 2 is the header; 2 frozen rows; data starts at row 3
  * columns A:B only, all pasted values -- no formulas
  * a basicFilter and filterView 1371853704 both cover stale row ranges, so they
    get resized to the new extent rather than left behind

`Country ratios by pipeline` (sheetId 443997510)
  * columns A-F are pasted values; G-AH are 28 columns of per-row, non-array
    formulas. They must be filled by copyPaste/PASTE_FORMULA so the relative
    row references follow -- never retyped, and never left short of the data
  * bandedRange 1069951898 spans V2:AH<end> and is resized with the data
  * filterView 886703151 spans A1:W<end> and is resized too
  * 1 frozen row, 6 frozen columns
  * column X (H2Status) contains `INDEX(#REF!, MATCH(C<n>, ...))` in *every*
    row -- verified rows 2, 5000, 6860, 6861. It is pre-existing and uniformly
    broken, so propagating row 2 does not spread anything new. Preserve it;
    do not "fix" it as a side effect of a length run.

Row-count changes go through insertDimension (inheritFromBefore: true) or
deleteDimension so formats and banding follow, and the formula block is filled
across the whole data range afterwards. Writing values into a range longer than
the formula block leaves rows with data and no lookups -- which is exactly what
the manual paste workflow had done: as of 2026-07-31 the live ratios tab had
formulas in G:AH only through row 6754, leaving the last 107 rows without
Region, SubRegion... StartCountry/EndCountry/RouteType/RouteAccuracy. The
default fill repairs that; pass fill_formulas='new-rows' to opt out.

`Country dictionary` (sheetId 610217930) is written too, by the step-2.5 change
set that prepare_boundaries.py computes. It is pipelines-only despite what its
A1 banner claims, carries no formulas, and is kept sorted by column A -- see
_plan_dictionary_tab for the ordering the edits have to follow.

Sequencing note: the dictionary change set and the length write are independent.
Only a column-A change can orphan a live ratios row, the only column-A changes
are the 9 deletions, and none of those appear in the live tab -- prepare_bound-
aries.py re-derives this check on every run rather than trusting this comment.
"""

from __future__ import annotations

import datetime as _dt

import sheets_client

LENGTH_TAB = 'Length estimates by pipeline'
LENGTH_SHEET_ID = 1069562947
LENGTH_FIRST_DATA_ROW = 3
LENGTH_NOTE_CELL = 'A1'
LENGTH_BASIC_FILTER_FIRST_ROW = 2          # basicFilter starts on the header row
LENGTH_FILTER_VIEW_ID = 1371853704

DICT_TAB = 'Country dictionary'
DICT_SHEET_ID = 610217930
DICT_WIDTH = 18                            # A:R
DICT_FIRST_DATA_ROW = 2                    # row 1 is the header, 1 frozen row
DICT_COL_COUNTRY = 0                       # A
DICT_COL_ALPHA3 = 1                        # B
DICT_COL_REGION = 4                        # E
DICT_COL_SUBREGION = 5                     # F
DICT_COL_BUBBLE = 7                        # H
DICT_COL_ALIAS = 8                         # I  (EEZNamesIfDifferent)
DICT_COL_NOTES = 16                        # Q
DICT_BANDED_RANGE_ID = 1642471189

RATIOS_TAB = 'Country ratios by pipeline'
RATIOS_SHEET_ID = 443997510
RATIOS_FIRST_DATA_ROW = 2
RATIOS_VALUE_COLUMNS = ['PipelineName', 'SegmentName', 'ProjectID', 'Country',
                        'LengthEstimateKmByCountry', 'LengthPerCountryFraction']
RATIOS_FORMULA_FIRST_COL = 6               # G, 0-indexed
RATIOS_FORMULA_LAST_COL = 34               # exclusive: AH is index 33
RATIOS_BANDED_RANGE_ID = 1069951898
RATIOS_BANDED_FIRST_COL = 21               # V
RATIOS_FILTER_VIEW_ID = 886703151
RATIOS_FILTER_VIEW_LAST_COL = 23           # exclusive: through W

# Rows per values.update call. Keeps each JSON body far under the argv budget
# in sheets_client.MAX_ARG_BYTES.
CHUNK_ROWS = 1000

METADATA_FIELDS = (
    'sheets(properties(sheetId,title,gridProperties),'
    'bandedRanges(bandedRangeId,range),'
    'basicFilter(range),'
    'filterViews(filterViewId,range))'
)


class WriteError(RuntimeError):
    pass


def _tab_state(metadata, sheet_id):
    for sheet in metadata.get('sheets', []):
        if sheet['properties']['sheetId'] == sheet_id:
            return sheet
    raise WriteError(f'sheetId {sheet_id} not found in the spreadsheet')


def _cell(value):
    """Coerce a pandas/numpy scalar into something JSON-serialisable."""
    if value is None:
        return ''
    if isinstance(value, float):
        # NaN -> blank, so the sheet shows an empty cell rather than the string
        # "nan" (which would then flow into every downstream formula).
        if value != value:
            return ''
        return value
    if isinstance(value, (int, str)):
        return value
    if hasattr(value, 'item'):
        return _cell(value.item())
    return str(value)


def _rows(frame, columns):
    return [[_cell(v) for v in row] for row in frame[columns].itertuples(index=False)]


def _resize_rows(sheet_id, current_rows, target_rows):
    """insertDimension / deleteDimension to make the grid exactly target_rows."""
    if target_rows == current_rows:
        return []
    if target_rows > current_rows:
        return [{'insertDimension': {
            'range': {'sheetId': sheet_id, 'dimension': 'ROWS',
                      'startIndex': current_rows, 'endIndex': target_rows},
            'inheritFromBefore': True,
        }}]
    return [{'deleteDimension': {
        'range': {'sheetId': sheet_id, 'dimension': 'ROWS',
                  'startIndex': target_rows, 'endIndex': current_rows},
    }}]


def _plan_length_tab(state, by_pipeline, update_note=True):
    grid = state['properties']['gridProperties']
    current_rows = grid['rowCount']
    n = len(by_pipeline)
    target_rows = LENGTH_FIRST_DATA_ROW - 1 + n

    requests = _resize_rows(LENGTH_SHEET_ID, current_rows, target_rows)

    # The basicFilter and the saved filter view both still point at row ranges
    # from older, shorter versions of this tab.
    if state.get('basicFilter'):
        requests.append({'setBasicFilter': {'filter': {
            'range': {'sheetId': LENGTH_SHEET_ID,
                      'startRowIndex': LENGTH_BASIC_FILTER_FIRST_ROW - 1,
                      'endRowIndex': target_rows,
                      'startColumnIndex': 0, 'endColumnIndex': 2},
            'sortSpecs': state['basicFilter'].get('sortSpecs', []),
        }}})
    for view in state.get('filterViews', []):
        if view['filterViewId'] != LENGTH_FILTER_VIEW_ID:
            continue
        requests.append({'updateFilterView': {
            'filter': {'filterViewId': LENGTH_FILTER_VIEW_ID,
                       'range': {'sheetId': LENGTH_SHEET_ID,
                                 'startRowIndex': LENGTH_BASIC_FILTER_FIRST_ROW - 1,
                                 'endRowIndex': target_rows,
                                 'startColumnIndex': 0, 'endColumnIndex': 2}},
            'fields': 'range',
        }})

    values = [
        (f"'{LENGTH_TAB}'!A{LENGTH_FIRST_DATA_ROW}",
         _rows(by_pipeline, ['ProjectID', 'LengthEstimateKm'])),
    ]
    if update_note:
        stamp = _dt.date.today().isoformat()
        values.insert(0, (f"'{LENGTH_TAB}'!{LENGTH_NOTE_CELL}",
                          [[f'written by route-lengths/ (see its README) - {stamp}']]))

    return {'tab': LENGTH_TAB, 'current_rows': current_rows,
            'target_rows': target_rows, 'data_rows': n,
            'requests': requests, 'values': values}


def _plan_ratios_tab(state, by_country, fill_formulas='all'):
    grid = state['properties']['gridProperties']
    current_rows = grid['rowCount']
    n = len(by_country)
    target_rows = RATIOS_FIRST_DATA_ROW - 1 + n
    first_data_index = RATIOS_FIRST_DATA_ROW - 1

    requests = _resize_rows(RATIOS_SHEET_ID, current_rows, target_rows)

    # Fill G:AH by copying row 2's formulas down. copyPaste tiles a one-row
    # source across the destination and rewrites relative references per row.
    if fill_formulas == 'all':
        fill_start = first_data_index + 1        # row 3 onwards; row 2 is the source
    elif fill_formulas == 'new-rows':
        fill_start = max(current_rows, first_data_index + 1)
    else:
        raise WriteError(f'unknown fill_formulas={fill_formulas!r}')
    if fill_start < target_rows:
        requests.append({'copyPaste': {
            'source': {'sheetId': RATIOS_SHEET_ID,
                       'startRowIndex': first_data_index,
                       'endRowIndex': first_data_index + 1,
                       'startColumnIndex': RATIOS_FORMULA_FIRST_COL,
                       'endColumnIndex': RATIOS_FORMULA_LAST_COL},
            'destination': {'sheetId': RATIOS_SHEET_ID,
                            'startRowIndex': fill_start,
                            'endRowIndex': target_rows,
                            'startColumnIndex': RATIOS_FORMULA_FIRST_COL,
                            'endColumnIndex': RATIOS_FORMULA_LAST_COL},
            'pasteType': 'PASTE_FORMULA',
        }})

    for band in state.get('bandedRanges', []):
        if band['bandedRangeId'] != RATIOS_BANDED_RANGE_ID:
            continue
        requests.append({'updateBanding': {
            'bandedRange': {'bandedRangeId': RATIOS_BANDED_RANGE_ID,
                            'range': {'sheetId': RATIOS_SHEET_ID,
                                      'startRowIndex': first_data_index,
                                      'endRowIndex': target_rows,
                                      'startColumnIndex': RATIOS_BANDED_FIRST_COL,
                                      'endColumnIndex': RATIOS_FORMULA_LAST_COL}},
            'fields': 'range',
        }})

    for view in state.get('filterViews', []):
        if view['filterViewId'] != RATIOS_FILTER_VIEW_ID:
            continue
        requests.append({'updateFilterView': {
            'filter': {'filterViewId': RATIOS_FILTER_VIEW_ID,
                       'range': {'sheetId': RATIOS_SHEET_ID,
                                 'startRowIndex': 0, 'endRowIndex': target_rows,
                                 'startColumnIndex': 0,
                                 'endColumnIndex': RATIOS_FILTER_VIEW_LAST_COL}},
            'fields': 'range',
        }})

    values = [(f"'{RATIOS_TAB}'!A{RATIOS_FIRST_DATA_ROW}",
               _rows(by_country, RATIOS_VALUE_COLUMNS))]

    return {'tab': RATIOS_TAB, 'current_rows': current_rows,
            'target_rows': target_rows, 'data_rows': n,
            'requests': requests, 'values': values}


# ---------------------------------------------------------------------------
# `Country dictionary`
#
# Grouped by Region/SubRegion, alphabetical within group -- not sorted by name,
# so a new row has to land inside the right block and a re-regioned row has to
# move. Three rows carry manual cell formatting (a highlight on the deprecated
# RegionOld column, and a couple of white-background cells), which is why rows
# are moved with insert/deleteDimension rather than by rewriting the grid in
# place: the formatting travels with the row instead of staying behind on
# whatever country lands in that position afterwards.
# ---------------------------------------------------------------------------

def _a1_column(index):
    label = ''
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        label = chr(65 + rem) + label
    return label


def _blocks(table):
    """Contiguous runs of equal (Region, SubRegion), as (key, start, end)."""
    runs = []
    for i, row in enumerate(table):
        key = (row[DICT_COL_REGION].strip(), row[DICT_COL_SUBREGION].strip())
        if runs and runs[-1][0] == key and runs[-1][2] == i - 1:
            runs[-1][2] = i
        else:
            runs.append([key, i, i])
    return runs


def _insert_index(table, region, subregion, country):
    """Where a row belongs: inside its block, alphabetically."""
    key = (region.strip(), subregion.strip())
    runs = [r for r in _blocks(table) if r[0] == key]
    if not runs:
        raise WriteError(
            f'{country!r} wants Region/SubRegion {key}, which no existing row '
            f'uses -- refusing to guess where it goes'
        )
    # If a group is split across runs, the longest run is the real block.
    _, start, end = max(runs, key=lambda r: r[2] - r[1])
    for i in range(start, end + 1):
        if table[i][DICT_COL_COUNTRY].strip().casefold() > country.casefold():
            return i
    return end + 1


def _new_dict_row(country, region, subregion, bubble='', notes=''):
    row = [''] * DICT_WIDTH
    row[DICT_COL_COUNTRY] = country
    row[DICT_COL_REGION] = region
    row[DICT_COL_SUBREGION] = subregion
    row[DICT_COL_BUBBLE] = bubble
    row[DICT_COL_NOTES] = notes
    return row


def plan_dictionary(changes, sheet_key=None, backend=None):
    """Turn a prepare_boundaries change set into ordered requests. No writes."""
    sheet_key = sheet_key or sheets_client.PIPELINES_SHEET_KEY
    backend = backend or sheets_client.get_backend()
    metadata = backend.get_metadata(sheet_key, METADATA_FIELDS)
    state = _tab_state(metadata, DICT_SHEET_ID)

    values = backend.batch_get(sheet_key, [f"'{DICT_TAB}'!A1:R"])[0]
    if not values:
        raise WriteError(f'{DICT_TAB!r} came back empty')
    table = [(list(r) + [''] * DICT_WIDTH)[:DICT_WIDTH] for r in values[1:]]
    table = [[str(c) for c in row] for row in table]
    by_name = {row[DICT_COL_COUNTRY].strip(): i for i, row in enumerate(table)}

    def _need(name):
        if name not in by_name:
            raise WriteError(f'{name!r} is not in {DICT_TAB!r} -- '
                             'the sheet has moved under the change set')
        return by_name[name]

    # -- 1. in-place cell edits, at live coordinates ----------------------
    cell_edits = []

    def _edit(name, column, value):
        idx = _need(name)
        table[idx][column] = value          # keep the model in step with the sheet
        cell_edits.append(
            (f"'{DICT_TAB}'!{_a1_column(column)}{idx + DICT_FIRST_DATA_ROW}", value))

    for country, alias in changes['alias_fixes'].items():
        _edit(country, DICT_COL_ALIAS, alias)
    canary = changes.get('canary')
    if canary:
        _edit(canary['Country'], DICT_COL_ALPHA3, canary['alpha3_new'])
        _edit(canary['Country'], DICT_COL_NOTES, canary['notes_new'])

    # -- 2. region corrections, applied to the local model ----------------
    # These rows get moved below, so the corrected values ride along in the
    # insert payload rather than being written twice.
    for country, fix in changes.get('region_fixes', {}).items():
        row = table[_need(country)]
        row[DICT_COL_REGION], row[DICT_COL_SUBREGION] = fix['to']

    # -- 3. deletions -----------------------------------------------------
    doomed = {_need(name) for name in changes['deletions']}

    # -- 4. what has to move to stay with its block -----------------------
    # A block is split by an *interloper* -- one Northern Africa row sitting in
    # the middle of Sub-Saharan Africa splits Sub-Saharan into two runs. Moving
    # "the rows not in the largest run" would then relocate 28 African countries
    # instead of the single row that is actually out of place. So resolve the
    # cheapest split first and re-derive: once the interloper leaves, the runs
    # either side of it merge and that split disappears on its own.
    kept = [row for i, row in enumerate(table) if i not in doomed]
    home_of = {id(row): i for i, row in enumerate(kept)}
    work = list(kept)
    moved_rows = []
    while True:
        runs = {}
        for key, start, end in _blocks(work):
            runs.setdefault(key, []).append((start, end))
        split = {k: v for k, v in runs.items() if len(v) > 1}
        if not split:
            break

        def stragglers(spans):
            home = max(spans, key=lambda r: r[1] - r[0])
            return [i for span in spans if span != home
                    for i in range(span[0], span[1] + 1)]

        key = min(split, key=lambda k: len(stragglers(split[k])))
        loose = set(stragglers(split[key]))
        moved_rows.extend(work[i] for i in sorted(loose))
        work = [row for i, row in enumerate(work) if i not in loose]
    movers = sorted(home_of[id(row)] for row in moved_rows)
    staying = work

    # -- 5. insertions: new rows plus the movers, into the right blocks ----
    pending = [
        _new_dict_row(add['Country'], add['Region'], add['SubRegion'],
                      bubble=add.get('PipelineBubbleRegion', ''),
                      notes=f"region by {add['basis']}")
        for add in changes['additions'].to_dict('records')
    ] + moved_rows
    pending.sort(key=lambda r: (r[DICT_COL_REGION], r[DICT_COL_SUBREGION],
                                r[DICT_COL_COUNTRY].casefold()))

    model = list(staying)
    inserts = []
    for row in pending:
        idx = _insert_index(model, row[DICT_COL_REGION], row[DICT_COL_SUBREGION],
                            row[DICT_COL_COUNTRY])
        model.insert(idx, row)
        inserts.append(idx)

    target_rows = DICT_FIRST_DATA_ROW - 1 + len(model)

    # -- 6. requests, in application order --------------------------------
    requests = []
    for i in sorted(doomed, reverse=True):
        grid = i + DICT_FIRST_DATA_ROW - 1
        requests.append({'deleteDimension': {'range': {
            'sheetId': DICT_SHEET_ID, 'dimension': 'ROWS',
            'startIndex': grid, 'endIndex': grid + 1}}})
    for i in sorted(movers, reverse=True):
        grid = i + DICT_FIRST_DATA_ROW - 1
        requests.append({'deleteDimension': {'range': {
            'sheetId': DICT_SHEET_ID, 'dimension': 'ROWS',
            'startIndex': grid, 'endIndex': grid + 1}}})
    for idx in inserts:
        grid = idx + DICT_FIRST_DATA_ROW - 1
        requests.append({'insertDimension': {
            'range': {'sheetId': DICT_SHEET_ID, 'dimension': 'ROWS',
                      'startIndex': grid, 'endIndex': grid + 1},
            # At the top of the data the row above is the bold header, so
            # inheriting from it would make the new row bold.
            'inheritFromBefore': grid > DICT_FIRST_DATA_ROW - 1}})

    # -- 7. values for every row that ended up new or moved ---------------
    # Match by identity, not equality -- two joint-area rows can be equal in
    # every written column while being different rows.
    seen = set()
    written = []
    for row in pending:
        for i, candidate in enumerate(model):
            if candidate is row and i not in seen:
                seen.add(i)
                written.append(i)
                break
    written.sort()
    value_ranges = []
    for run in _contiguous(written):
        first = run[0] + DICT_FIRST_DATA_ROW
        value_ranges.append((f"'{DICT_TAB}'!A{first}",
                             [[_cell(v) for v in model[i]] for i in run]))

    # -- 8. banding and filter views follow the new extent ----------------
    for band in state.get('bandedRanges', []):
        if band['bandedRangeId'] != DICT_BANDED_RANGE_ID:
            continue
        requests.append({'updateBanding': {
            'bandedRange': {'bandedRangeId': DICT_BANDED_RANGE_ID,
                            'range': {'sheetId': DICT_SHEET_ID,
                                      'startRowIndex': 0, 'endRowIndex': target_rows,
                                      'startColumnIndex': 0,
                                      'endColumnIndex': DICT_WIDTH}},
            'fields': 'range'}})
    # Filter views are looked up by id from live metadata rather than hardcoded:
    # they are personal saved views and their titles are people's names.
    for view in state.get('filterViews', []):
        requests.append({'updateFilterView': {
            'filter': {'filterViewId': view['filterViewId'],
                       'range': {'sheetId': DICT_SHEET_ID,
                                 'startRowIndex': 0, 'endRowIndex': target_rows,
                                 'startColumnIndex': 0,
                                 'endColumnIndex': DICT_WIDTH}},
            'fields': 'range'}})

    return {
        'tab': DICT_TAB,
        'current_rows': state['properties']['gridProperties']['rowCount'],
        'target_rows': target_rows,
        'data_rows': len(model),
        'cell_edits': cell_edits,
        'deleted': sorted(table[i][DICT_COL_COUNTRY] for i in doomed),
        'moved': [r[DICT_COL_COUNTRY] for r in moved_rows],
        'added': [r[DICT_COL_COUNTRY] for r in pending if r not in moved_rows],
        'requests': requests,
        'values': value_ranges,
        # The table this plan is expected to produce. simulate_dictionary()
        # replays the requests against the live rows and must reproduce it.
        'final_table': model,
    }


def simulate_dictionary(plan_dict, sheet_key=None, backend=None):
    """Replay a dictionary plan locally and diff against its expected table.

    The write is a sequence of positional row inserts and deletes, so an
    off-by-one anywhere silently shifts every row below it. Cheaper to catch
    that here than in the sheet.
    """
    sheet_key = sheet_key or sheets_client.PIPELINES_SHEET_KEY
    backend = backend or sheets_client.get_backend()
    values = backend.batch_get(sheet_key, [f"'{DICT_TAB}'!A1:R"])[0]
    table = [[str(c) for c in (list(r) + [''] * DICT_WIDTH)[:DICT_WIDTH]]
             for r in values[1:]]

    for a1, value in plan_dict['cell_edits']:
        ref = a1.split('!')[1]
        col = _a1_column_index(''.join(c for c in ref if c.isalpha()))
        row = int(''.join(c for c in ref if c.isdigit()))
        table[row - DICT_FIRST_DATA_ROW][col] = value

    for request in plan_dict['requests']:
        kind = next(iter(request))
        if kind == 'deleteDimension':
            rng = request[kind]['range']
            start = rng['startIndex'] - (DICT_FIRST_DATA_ROW - 1)
            del table[start:start + (rng['endIndex'] - rng['startIndex'])]
        elif kind == 'insertDimension':
            rng = request[kind]['range']
            start = rng['startIndex'] - (DICT_FIRST_DATA_ROW - 1)
            for _ in range(rng['endIndex'] - rng['startIndex']):
                table.insert(start, [''] * DICT_WIDTH)

    for a1, rows in plan_dict['values']:
        first = int(a1.split('!A')[1]) - DICT_FIRST_DATA_ROW
        for offset, row in enumerate(rows):
            table[first + offset] = [str(c) for c in row]

    expected = [[str(c) for c in row] for row in plan_dict['final_table']]
    problems = []
    if len(table) != len(expected):
        problems.append(f'simulated {len(table)} rows, expected {len(expected)}')
    for i, (got, want) in enumerate(zip(table, expected)):
        if got != want:
            cols = [_a1_column(c) for c in range(DICT_WIDTH) if got[c] != want[c]]
            problems.append(
                f'row {i + DICT_FIRST_DATA_ROW} ({want[DICT_COL_COUNTRY]!r}): '
                f'columns {",".join(cols)} differ -- '
                f'{[got[c] for c in range(DICT_WIDTH) if got[c] != want[c]]} != '
                f'{[want[c] for c in range(DICT_WIDTH) if got[c] != want[c]]}'
            )
    return problems, table


def _a1_column_index(label):
    n = 0
    for ch in label:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _contiguous(indices):
    runs = []
    for i in indices:
        if runs and i == runs[-1][-1] + 1:
            runs[-1].append(i)
        else:
            runs.append([i])
    return runs


def describe_dictionary(p):
    lines = [f"  {p['tab']}: {p['data_rows']:,} data rows, "
             f"grid {p['current_rows']:,} -> {p['target_rows']:,} "
             f"({p['target_rows'] - p['current_rows']:+,} rows)"]
    lines.append(f"      {len(p['cell_edits'])} cell edits "
                 f"(aliases, Canary Islands)")
    lines.append(f"      {len(p['deleted'])} deleted: "
                 f"{', '.join(p['deleted'][:3])}...")
    lines.append(f"      {len(p['added'])} added, {len(p['moved'])} moved "
                 f"to rejoin their block: {', '.join(p['moved']) or 'none'}")
    kinds = {}
    for request in p['requests']:
        kind = next(iter(request))
        kinds[kind] = kinds.get(kind, 0) + 1
    lines.append('      ' + ', '.join(f'{v}x {k}' for k, v in kinds.items()))
    for a1, rows in p['values']:
        lines.append(f"      = values.update {a1} ({len(rows)} rows)")
    return '\n'.join(lines)


def write_dictionary(plan_dict, sheet_key=None, backend=None, dry_run=False):
    """Apply a dictionary plan. Cell edits, then structure, then new values."""
    sheet_key = sheet_key or sheets_client.PIPELINES_SHEET_KEY
    backend = backend or sheets_client.get_backend(require_write=True)
    if not getattr(backend, 'allow_write', False):
        raise WriteError('write_dictionary needs a write backend')
    for a1, value in plan_dict['cell_edits']:
        backend.values_update(sheet_key, a1, [[value]], dry_run=dry_run)
    if plan_dict['requests']:
        backend.batch_update(sheet_key, plan_dict['requests'], dry_run=dry_run)
    for a1, rows in plan_dict['values']:
        backend.values_update(sheet_key, a1, rows, dry_run=dry_run)
    return plan_dict


def verify_dictionary(plan_dict, sheet_key=None, backend=None):
    """Re-read the tab and confirm the change set landed."""
    sheet_key = sheet_key or sheets_client.PIPELINES_SHEET_KEY
    backend = backend or sheets_client.get_backend()
    problems = []
    metadata = backend.get_metadata(sheet_key, METADATA_FIELDS)
    state = _tab_state(metadata, DICT_SHEET_ID)
    got = state['properties']['gridProperties']['rowCount']
    if got != plan_dict['target_rows']:
        problems.append(f'{DICT_TAB}: expected {plan_dict["target_rows"]} rows, '
                        f'found {got}')

    values = backend.batch_get(sheet_key, [f"'{DICT_TAB}'!A1:R"])[0]
    table = [(list(r) + [''] * DICT_WIDTH)[:DICT_WIDTH] for r in values[1:]]
    names = [str(row[DICT_COL_COUNTRY]).strip() for row in table]
    for name in plan_dict['deleted']:
        if name in names:
            problems.append(f'{name!r} was supposed to be deleted but is still there')
    for name in plan_dict['added'] + plan_dict['moved']:
        if name not in names:
            problems.append(f'{name!r} was supposed to be added but is missing')

    # Every Region/SubRegion group must be one contiguous block again.
    split = [key for key, count in
             ((k, sum(1 for r in _blocks([[str(c) for c in row] for row in table])
                      if r[0] == k))
              for k in {(str(r[DICT_COL_REGION]).strip(),
                         str(r[DICT_COL_SUBREGION]).strip()) for r in table})
             if count > 1]
    for key in split:
        problems.append(f'Region/SubRegion {key} is split across more than one block')
    return problems


def plan(by_pipeline, by_country, sheet_key=None, backend=None,
         update_note=True, fill_formulas='all'):
    """Read the live tabs and work out what would be written. No writes."""
    sheet_key = sheet_key or sheets_client.PIPELINES_SHEET_KEY
    backend = backend or sheets_client.get_backend()
    _check_inputs(by_pipeline, by_country)
    metadata = backend.get_metadata(sheet_key, METADATA_FIELDS)
    return {
        'sheet_key': sheet_key,
        'length': _plan_length_tab(_tab_state(metadata, LENGTH_SHEET_ID),
                                   by_pipeline, update_note=update_note),
        'ratios': _plan_ratios_tab(_tab_state(metadata, RATIOS_SHEET_ID),
                                   by_country, fill_formulas=fill_formulas),
    }


def _check_inputs(by_pipeline, by_country):
    missing = [c for c in ['ProjectID', 'LengthEstimateKm']
               if c not in by_pipeline.columns]
    if missing:
        raise WriteError(f'by_pipeline is missing {missing}')
    missing = [c for c in RATIOS_VALUE_COLUMNS if c not in by_country.columns]
    if missing:
        raise WriteError(f'by_country is missing {missing}')
    if by_pipeline.empty or by_country.empty:
        raise WriteError('refusing to write an empty table over a live tab')
    if by_pipeline['ProjectID'].duplicated().any():
        dupes = by_pipeline.loc[by_pipeline['ProjectID'].duplicated(), 'ProjectID']
        raise WriteError(f'duplicate ProjectIDs in by_pipeline: {list(dupes)[:5]}')


def describe(plan_dict):
    """Human-readable summary of a plan, for review before writing."""
    lines = [f"spreadsheet {plan_dict['sheet_key']}"]
    for key in ('length', 'ratios'):
        p = plan_dict[key]
        delta = p['target_rows'] - p['current_rows']
        change = 'unchanged' if delta == 0 else f'{delta:+,} rows'
        lines.append(
            f"  {p['tab']}: {p['data_rows']:,} data rows, "
            f"grid {p['current_rows']:,} -> {p['target_rows']:,} ({change})"
        )
        for request in p['requests']:
            lines.append(f"      + {next(iter(request))}")
        for a1, rows in p['values']:
            lines.append(f"      = values.update {a1} ({len(rows):,} rows)")
    return '\n'.join(lines)


def _apply(backend, sheet_key, tab_plan, dry_run):
    if tab_plan['requests']:
        backend.batch_update(sheet_key, tab_plan['requests'], dry_run=dry_run)
    for a1, rows in tab_plan['values']:
        if len(rows) <= CHUNK_ROWS:
            backend.values_update(sheet_key, a1, rows, dry_run=dry_run)
            continue
        # A1 anchors are 'Tab'!A<row>; step the row for each chunk.
        tab, _, anchor = a1.rpartition('!')
        column = anchor[0]
        first_row = int(anchor[1:])
        for offset in range(0, len(rows), CHUNK_ROWS):
            chunk = rows[offset:offset + CHUNK_ROWS]
            backend.values_update(
                sheet_key, f'{tab}!{column}{first_row + offset}', chunk,
                dry_run=dry_run,
            )


def write_all(by_pipeline, by_country, sheet_key=None, backend=None,
              dry_run=False, update_note=True, fill_formulas='all',
              plan_dict=None):
    """Write both tabs. Structure requests first, then values.

    dry_run sends every request to gws with --dry-run, which validates the body
    locally and never reaches the API -- use it to check the plan is well-formed
    without touching the sheet.
    """
    sheet_key = sheet_key or sheets_client.PIPELINES_SHEET_KEY
    backend = backend or sheets_client.get_backend(require_write=True)
    if not getattr(backend, 'allow_write', False):
        raise WriteError(
            'write_all needs a write backend: '
            'sheets_client.get_backend(require_write=True)'
        )
    if plan_dict is None:
        plan_dict = plan(by_pipeline, by_country, sheet_key=sheet_key,
                         backend=backend, update_note=update_note,
                         fill_formulas=fill_formulas)

    # Length first: the ratios tab's LengthEstimateKm column looks it up.
    _apply(backend, sheet_key, plan_dict['length'], dry_run)
    _apply(backend, sheet_key, plan_dict['ratios'], dry_run)
    return plan_dict


def verify(plan_dict, backend=None):
    """Re-read the tabs after a write and confirm the extents took."""
    backend = backend or sheets_client.get_backend()
    sheet_key = plan_dict['sheet_key']
    metadata = backend.get_metadata(sheet_key, METADATA_FIELDS)
    problems = []
    for key, sheet_id in (('length', LENGTH_SHEET_ID), ('ratios', RATIOS_SHEET_ID)):
        want = plan_dict[key]['target_rows']
        got = _tab_state(metadata, sheet_id)['properties']['gridProperties']['rowCount']
        if got != want:
            problems.append(f'{plan_dict[key]["tab"]}: expected {want} rows, found {got}')

    state = _tab_state(metadata, RATIOS_SHEET_ID)
    want = plan_dict['ratios']['target_rows']
    for band in state.get('bandedRanges', []):
        if band['bandedRangeId'] == RATIOS_BANDED_RANGE_ID:
            if band['range'].get('endRowIndex') != want:
                problems.append(
                    f'banded range ends at {band["range"].get("endRowIndex")}, '
                    f'expected {want}'
                )

    # The formula block must reach the last data row -- the failure this whole
    # design exists to prevent.
    tail = backend.batch_get(
        sheet_key, [f"'{RATIOS_TAB}'!Z{want}:AH{want}"], render='FORMULA')[0]
    if not tail or not any(str(c).startswith('=') for c in tail[0]):
        problems.append(f'no formulas in Z:AH on the last data row ({want})')
    return problems
