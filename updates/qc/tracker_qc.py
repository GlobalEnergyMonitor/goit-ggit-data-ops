#!/usr/bin/env python
"""Live-sheet QC for the GOIT/GGIT pipeline trackers.

This is the *during-the-update-cycle* counterpart to
``releases/qc/data-release-qc.py``: that one checks finished release files,
this one checks the live "Pipelines (Gas/Oil/NGL) - main" Google Sheet while
researchers are still editing it.

Usage:
    python tracker_qc.py --tracker ggit
    python tracker_qc.py --tracker goit --cycle-start 2026-07-06
    python tracker_qc.py --csv /path/to/gem_export_ggit.csv --tracker ggit
    python tracker_qc.py --tracker ggit --dump-rows findings.csv

Prints one line per check (OK / NOTE / WARN / FAIL) and exits 1 if any check
FAILs. ``--dump-rows`` writes every flagged row to a CSV, one row per
(check, ProjectID), for working through in the sheet.

Importable as a library — that is how ``mid-update-qc-sweep.ipynb`` uses it:

    import tracker_qc
    df = tracker_qc.load_live('ggit')
    findings = tracker_qc.run_all(df, cycle_start='2026-07-06')
    tracker_qc.print_summary(findings)
    findings_by_name['non-canonical Status'].rows(df)   # offending rows

**Read-only.** Reads go through the sibling ``gem-db-ops`` repo (the single
source of truth for pulling GEM data); nothing here writes to the sheet.
Every check is column-presence guarded, so the same code runs against GGIT
(132 cols) and GOIT (107 cols) — absent columns produce SKIP, not a crash.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

# gem-db-ops is the only sanctioned read path for GEM tracker data.
GEM_DB_OPS = Path(__file__).resolve().parents[3] / 'gem-db-ops'

MISSING = {'', '--', 'nan', 'None'}

# Canonical vocabularies. Statuses come from gem-tracker-constants when it is
# installed so this file never becomes a second declaration of them.
try:
    from gem_tracker_constants import PIPELINE_STATUS
    CANONICAL_STATUSES = set(PIPELINE_STATUS)
except ImportError:  # pragma: no cover - constants package not installed
    CANONICAL_STATUSES = {'proposed', 'construction', 'operating', 'idle',
                          'mothballed', 'shelved', 'cancelled', 'retired'}

YEAR_COLS = ['ProposalYear', 'ConstructionYear', 'StartYear1', 'StartYear2',
             'StartYear3', 'StartYearEarliest', 'ShelvedYear', 'CancelledYear',
             'StopYear', 'FIDYear', 'H2ProposedYear', 'H2StartYear',
             'SegmentCostYear']
MONTH_COLS = ['ProposalMonth', 'ConstructionMonth', 'StartMonth1', 'CancelledMonth',
              'StartYear2Month', 'StartYear3Month', 'StopMonth']
MONTH_NAMES = {m.lower() for m in
               ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December',
                'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Sept',
                'Oct', 'Nov', 'Dec']}
MONTH_YEAR_PAIRS = [('ProposalMonth', 'ProposalYear'),
                    ('ConstructionMonth', 'ConstructionYear'),
                    ('StartMonth1', 'StartYear1'),
                    ('StartYear2Month', 'StartYear2'),
                    ('StartYear3Month', 'StartYear3'),
                    ('CancelledMonth', 'CancelledYear'),
                    ('StopMonth', 'StopYear')]
NUMERIC_COLS = ['Capacity', 'CapacityBcm/y', 'CapacityBOEd', 'Pressure',
                'LengthKnown', 'LengthKnownKm', 'LengthEstimateKm',
                'LengthMergedKm', 'Diameter', 'DiameterInMm', 'ProjectLevelCost',
                'SegmentCost', 'Cost', 'CostUSD', 'CostEuro', 'NumberOfCountries']
VALUE_UNITS_PAIRS = [('Capacity', 'CapacityUnits'), ('Diameter', 'DiameterUnits'),
                     ('LengthKnown', 'LengthKnownUnits'), ('Pressure', 'PressureUnits'),
                     ('ProjectLevelCost', 'ProjectLevelCostUnits'),
                     ('SegmentCost', 'SegmentCostUnits'), ('Cost', 'CostUnits'),
                     ('H2Cost', 'H2CostUnits')]
STATUS_MILESTONES = [('cancelled', 'CancelledYear'), ('shelved', 'ShelvedYear'),
                     ('retired', 'StopYear')]
# statuses that imply the pipeline has been built and should have a start year
BUILT_STATUSES = {'operating', 'idle', 'mothballed', 'retired'}
IN_DEV_STATUSES = {'proposed', 'construction'}

# Value -> ref column pairs. Sparse refs are a known legacy backlog, so these
# are reported as WARN on cycle-touched rows and NOTE on the whole sheet.
VALUE_REF_PAIRS = [('Status', 'Status [ref]'), ('Fuel', 'Fuel [ref]'),
                   ('PipelineType', 'PipelineType [ref]'),
                   ('Capacity', 'Capacity [ref]'), ('LengthKnown', 'Length [ref]'),
                   ('Diameter', 'Diameter [ref]'), ('StartYear1', 'Start [ref]'),
                   ('ProposalYear', 'Proposal [ref]'),
                   ('ConstructionYear', 'Construction [ref]'),
                   ('CancelledYear', 'Cancelled [ref]'),
                   ('ShelvedYear', 'Shelved [ref]'), ('StopYear', 'Stop [ref]'),
                   ('FIDYear', 'FID [ref]'), ('Delayed', 'Delay [ref]'),
                   ('SegmentCost', 'SegmentCost [ref]'),
                   ('ProjectLevelCost', 'ProjectLevelCost [ref]'),
                   ('Cost', 'Cost [ref]')]

# Free-text vocabularies. Each entry is (column, canonical values). Values
# outside the set are flagged; a value differing only by case or surrounding
# whitespace is flagged as normalizable rather than unknown.
VOCABULARIES = {
    'Fuel': None,  # reported for review; the buckets live in gem-tracker-constants
    'PipelineType': {'transmission', 'distribution', 'gathering',
                     'both transmission and gathering',
                     'both transmission and distribution'},
    'FIDStatus': {'FID', 'Pre-FID'},
    'RouteAccuracy': {'very high (within meters)', 'high', 'medium', 'low',
                      'very low (straight line/schematic)', 'no route'},
    'RouteType': {'Mapped route (at any accuracy)',
                  'Not mapped (but could be — route or endpoints are known)',
                  'Unavailable (cannot find route)', 'Capacity expansion only',
                  'Bidirectionality upgrade only', 'Included in other ProjectID'},
    'Delayed': {'yes'},
    'DelayType': {'confirmed', 'inferred'},
    'ShelvedCancelledType': {'confirmed', 'inferred'},
    'EuropeTracker': {'yes'},
    'AssociatedWithUSLNGExports': {'yes'},
    'PipelineDirectionality': {'unidirectional', 'bidirectional'},
    'LengthKnownUnits': {'km', 'mi'},
    'DiameterUnits': {'in', 'mm'},
    'PressureUnits': {'MPa', 'bar', 'psi', 'kgf/cm2'},
    'ProjectLevelCostUnits': None,
    'SegmentCostUnits': None,
    'CostUnits': None,
    'CapacityUnits': None,
}

# Currency codes seen in the cost-unit columns that are not ISO 4217.
NON_ISO_CURRENCIES = {'CAN': 'CAD', 'RMB': 'CNY'}

# Capacity unit -> bcm/y factor, for the derived-column agreement check.
BCM_PER_YEAR = {'bcm/y': 1.0, 'MMcf/d': 0.010337, 'MMSCMD': 0.365,
                'Mcf/d': 1.0337e-5, 'mtpa': 1.36, 'scm/y': 1e-9, 'm3/d': 3.65e-7}

# Plausibility ceilings. Deliberately generous — the point is to catch unit
# errors (a national network's throughput entered as one pipeline's), not to
# second-guess large real pipelines.
MAX_BCM_PER_YEAR = 180.0       # Transco, the world's largest, is ~172
MAX_LENGTH_KM = 30_000.0       # NGTL is ~24,500 km
MAX_DIAMETER_MM = 2_000.0
MAX_DIAMETER_IN = 100.0


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_live(tracker: str) -> pd.DataFrame:
    """Read a tracker tab live from the backend sheet, read-only, via gem-db-ops.

    Everything comes back as stripped strings — QC needs to see exactly what
    is in each cell, including the values that fail to parse as numbers.
    """
    if not GEM_DB_OPS.exists():
        raise SystemExit(
            f"gem-db-ops not found at {GEM_DB_OPS}. It is the single source of "
            "truth for pulling GEM data — clone it next to this repo, or pass "
            "--csv with a CSV pulled by `python ggit/pull.py`."
        )
    sys.path.insert(0, str(GEM_DB_OPS))
    import gem_sheets

    tab = gem_sheets.resolve_tab(tracker)
    values = gem_sheets.read_tab_values(tab.title, tab.sheet_key)
    header = [str(c).strip() for c in values[tab.header_row]]
    rows = values[tab.header_row + 1:]
    width = len(header)
    rows = [r + [''] * (width - len(r)) if len(r) < width else r[:width] for r in rows]
    return pd.DataFrame(rows, columns=header, dtype=str).fillna('')


def load_csv(path, header_row: int = 2) -> pd.DataFrame:
    """Read a CSV already pulled by gem-db-ops (`ggit/pull.py` / `goit/pull.py`)."""
    df = pd.read_csv(path, header=header_row, dtype=str,
                     keep_default_na=False, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Finding plumbing
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """One check's result. ``mask`` indexes the offending rows of the frame."""

    level: str          # OK / NOTE / WARN / FAIL / SKIP
    tier: str
    name: str
    detail: str = ''
    mask: pd.Series | None = None
    cols: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return 0 if self.mask is None else int(self.mask.sum())

    def rows(self, df: pd.DataFrame, extra: list[str] | None = None) -> pd.DataFrame:
        """The offending rows, with identifying columns plus the check's own."""
        if self.mask is None or not self.count:
            return df.iloc[:0]
        want = ID_COLS + self.cols + (extra or [])
        keep = [c for i, c in enumerate(want) if c in df.columns and c not in want[:i]]
        return df.loc[self.mask, keep]


ID_COLS = ['ProjectID', 'PipelineName', 'SegmentName', 'CountriesOrAreas',
           'Status', 'Researcher', 'LastUpdated']


class Checker:
    """Accumulates findings for one frame."""

    def __init__(self, df: pd.DataFrame, cycle_start=None, today=None):
        self.df = df
        self.findings: list[Finding] = []
        self.tier = ''
        self.today = pd.Timestamp(today or datetime.date.today())
        self.cycle_start = pd.Timestamp(cycle_start) if cycle_start else None

        # Rows with a ProjectID but nothing else are reserved-ID placeholders,
        # not data-entry errors — every required-field check would fire on them.
        self.placeholder = self.blank('Status') & self.blank('PipelineName')
        self.real = ~self.placeholder

        self.last_updated = pd.to_datetime(
            self.s('LastUpdated'), errors='coerce', format='mixed')
        if self.cycle_start is not None:
            self.cycle = self.last_updated >= self.cycle_start
        else:
            self.cycle = pd.Series(False, index=df.index)

    # -- cell accessors -----------------------------------------------------

    def has(self, *cols) -> bool:
        return all(c in self.df.columns for c in cols)

    def s(self, col) -> pd.Series:
        """Stripped string view of a column (empty series if absent)."""
        if col not in self.df.columns:
            return pd.Series('', index=self.df.index, dtype=str)
        return self.df[col].astype(str).str.strip()

    def blank(self, col) -> pd.Series:
        return self.s(col).isin(MISSING)

    def filled(self, col) -> pd.Series:
        return ~self.blank(col)

    def num(self, col) -> pd.Series:
        """Numeric view: strips thousands commas, leaves anything else as NaN.

        Commas are only stripped when they form valid thousands grouping.
        Stripping unconditionally turns the very common multi-valued entry
        ``42,36,30`` into 423630, which then sails through every plausibility
        band as a real number.
        """
        raw = self.s(col)
        grouped = raw.str.fullmatch(r'-?\d{1,3}(?:,\d{3})+(?:\.\d+)?')
        cleaned = raw.mask(grouped, raw.str.replace(',', '', regex=False))
        return pd.to_numeric(cleaned.replace(dict.fromkeys(MISSING)), errors='coerce')

    # -- reporting ----------------------------------------------------------

    def report(self, level, name, detail='', mask=None, cols=None):
        self.findings.append(Finding(level, self.tier, name, detail, mask,
                                     list(cols or [])))

    def flag(self, name, mask, cols=None, level='WARN', detail='', ok_detail=''):
        """Report ``level`` with a count when ``mask`` has rows, else OK."""
        mask = mask & self.real
        n = int(mask.sum())
        if n:
            bits = [f'{n} rows'] + ([detail] if detail else [])
            self.report(level, name, '; '.join(bits), mask, cols)
        else:
            self.report('OK', name, ok_detail)
        return mask

    def skip(self, name, why):
        self.report('SKIP', name, why)


# ---------------------------------------------------------------------------
# Tier 0 — sheet shape
# ---------------------------------------------------------------------------

def check_shape(c: Checker):
    c.tier = '0. sheet shape'
    df = c.df
    c.report('NOTE', 'row counts',
             f'{len(df)} sheet rows: {int(c.real.sum())} data rows, '
             f'{int(c.placeholder.sum())} reserved-ID placeholders '
             f'(ProjectID only, everything else blank)',
             c.placeholder, ['ProjectID'])

    if not c.has('ProjectID'):
        return c.report('FAIL', 'ProjectID column present')
    pid = c.s('ProjectID')
    c.flag('ProjectID missing', pid.isin(MISSING), level='FAIL')
    c.flag('ProjectID malformed (not P<digits>)',
           ~pid.isin(MISSING) & ~pid.str.fullmatch(r'P\d+'), ['ProjectID'], 'FAIL')
    c.flag('ProjectID duplicated',
           ~pid.isin(MISSING) & pid.duplicated(keep=False), ['ProjectID'], 'FAIL')

    # An all-blank row inside the data block usually means a stray edit or a
    # row that was cleared instead of deleted.
    key_cols = [x for x in ['PipelineName', 'Status', 'CountriesOrAreas'] if c.has(x)]
    if key_cols:
        empty = c.blank('ProjectID')
        for col in key_cols:
            empty &= c.blank(col)
        c.flag('fully empty row (no ProjectID either)', empty, level='WARN')


# ---------------------------------------------------------------------------
# Tier 1 — vocabulary conformance
# ---------------------------------------------------------------------------

def check_vocabularies(c: Checker):
    c.tier = '1. vocabulary'

    if c.has('Status'):
        status = c.s('Status')
        bad = ~status.isin(CANONICAL_STATUSES) & ~status.isin(MISSING)
        normalizable = bad & status.str.lower().str.strip().isin(CANONICAL_STATUSES)
        c.flag('non-canonical Status', bad, ['Status'], 'FAIL',
               detail=f'{int(normalizable.sum())} of them differ only by case/'
                      'whitespace; the rest drop out of every status-bucket filter',
               ok_detail=str(status[c.real].value_counts().to_dict()))
        c.flag('blank Status on a real row', c.blank('Status'), level='FAIL')

    if c.has('Fuel'):
        try:
            from gem_tracker_constants import find_uncovered_fuels
            uncovered = find_uncovered_fuels(c.df.loc[c.real], fuel_col='Fuel')
            n = len(uncovered)
            c.report('FAIL' if n else 'OK', 'Fuel outside gem-tracker-constants buckets',
                     f'{n} distinct uncovered values: {list(uncovered)[:10]}' if n
                     else str(c.s('Fuel')[c.real].value_counts().to_dict()))
        except ImportError:
            c.skip('Fuel outside gem-tracker-constants buckets',
                   'gem-tracker-constants not installed '
                   '(pip install -e ./gem-tracker-constants)')

    for col, canonical in VOCABULARIES.items():
        if not c.has(col):
            continue
        vals = c.s(col)
        present = ~vals.isin(MISSING)
        if canonical is None:
            counts = vals[present & c.real].value_counts()
            c.report('NOTE', f'{col} values (review)',
                     f'{len(counts)} distinct: {counts.to_dict()}')
            continue
        lowered = {v.lower() for v in canonical}
        bad = present & ~vals.isin(canonical)
        normalizable = bad & vals.str.lower().isin(lowered)
        unknown = bad & ~normalizable
        c.flag(f'{col} normalizable (case/whitespace only)', normalizable, [col], 'WARN',
               detail=f'variants: {sorted(set(vals[normalizable & c.real]))}')
        c.flag(f'{col} outside vocabulary', unknown, [col], 'WARN',
               detail=f'values: {sorted(set(vals[unknown & c.real]))[:12]}')

    for col in ['ProjectLevelCostUnits', 'SegmentCostUnits', 'CostUnits']:
        if not c.has(col):
            continue
        vals = c.s(col)
        bad = vals.isin(NON_ISO_CURRENCIES)
        c.flag(f'{col} non-ISO currency code', bad, [col], 'WARN',
               detail='; '.join(f'{k} -> {v}' for k, v in NON_ISO_CURRENCIES.items()
                                if (vals == k).any()))


# ---------------------------------------------------------------------------
# Tier 2 — type conformance (paste and column-shift errors)
# ---------------------------------------------------------------------------

def check_types(c: Checker):
    c.tier = '2. type conformance'

    for col in NUMERIC_COLS + YEAR_COLS:
        if not c.has(col):
            continue
        bad = c.filled(col) & c.num(col).isna()
        # Multi-valued entries ("42,36,30") are a distinct, very common shape:
        # legitimate information in a field nothing downstream can compute on.
        multi = bad & c.s(col).str.fullmatch(r'[\d\s.,/;&+-]*[,/;&+-][\d\s.,/;&+-]*')
        c.flag(f'{col} multi-valued (comma/slash list or range)', multi, [col], 'WARN',
               detail='blank DiameterInMm/CapacityBcm-style derived columns follow'
                      if col in ('Diameter', 'Capacity') else '')
        c.flag(f'{col} not a number', bad & ~multi, [col], 'WARN',
               detail=f'examples: {sorted(set(c.s(col)[bad & ~multi & c.real]))[:4]}')

    # Geometry, URLs and prose landing in scalar columns: always a paste error.
    scalar = [x for x in NUMERIC_COLS + YEAR_COLS + MONTH_COLS + list(VOCABULARIES)
              if c.has(x)]
    for pattern, label in [(r'^\s*(?:LINESTRING|MULTILINESTRING|POINT|POLYGON)\b',
                            'WKT geometry'),
                           (r'^\s*https?://', 'a URL')]:
        hits = pd.Series(False, index=c.df.index)
        where = []
        for col in scalar:
            m = c.s(col).str.contains(pattern, case=False, regex=True)
            if m.any():
                hits |= m
                where.append(f'{col} ({int((m & c.real).sum())})')
        c.flag(f'scalar column contains {label}', hits,
               [col for col in scalar if c.s(col).str.contains(
                   pattern, case=False, regex=True).any()],
               'FAIL', detail='in ' + ', '.join(where) if where else '')

    for col in MONTH_COLS:
        if not c.has(col):
            continue
        vals = c.s(col)
        year_like = vals.str.fullmatch(r'(?:19|20)\d\d')
        c.flag(f'{col} holds a year, not a month', year_like, [col], 'FAIL')
        # The month columns mix numerals with English month names, full and
        # abbreviated. Names are readable but they are not the same key as 4.
        named = vals.str.lower().str.rstrip('.').isin(MONTH_NAMES)
        c.flag(f'{col} spelled as a month name, not 1-12', named, [col], 'WARN',
               detail=f'variants: {sorted(set(vals[named & c.real]))[:12]}')
        out_of_range = (c.filled(col) & ~year_like & ~named
                        & ~c.num(col).between(1, 12, inclusive='both'))
        c.flag(f'{col} neither a number 1-12 nor a month name', out_of_range,
               [col], 'WARN',
               detail=f'values: {sorted(set(vals[out_of_range & c.real]))[:4]}')

    for col in ['Wiki'] + [x for x in c.df.columns if x.endswith('[ref]')]:
        if not c.has(col):
            continue
        vals = c.s(col)
        c.flag(f'{col} filled but contains no URL',
               c.filled(col) & ~vals.str.contains('http', case=False), [col], 'WARN')


# ---------------------------------------------------------------------------
# Tier 3 — derived-column agreement
# ---------------------------------------------------------------------------

def _disagrees(expected, actual, abs_tol, rel_tol):
    both = expected.notna() & actual.notna()
    tol = np.maximum(abs_tol, rel_tol * actual.abs())
    return both & ((expected - actual).abs() > tol)


def check_derived(c: Checker):
    c.tier = '3. derived columns'

    if c.has('LengthKnown', 'LengthKnownUnits', 'LengthKnownKm'):
        raw, units = c.num('LengthKnown'), c.s('LengthKnownUnits')
        expected = pd.Series(np.where(units == 'mi', raw * 1.60934, raw),
                             index=c.df.index)
        expected[~units.isin({'km', 'mi'})] = np.nan
        c.flag('LengthKnownKm disagrees with LengthKnown + units',
               _disagrees(expected, c.num('LengthKnownKm'), 0.5, 0.01),
               ['LengthKnown', 'LengthKnownUnits', 'LengthKnownKm'], 'FAIL')

    if c.has('Diameter', 'DiameterUnits', 'DiameterInMm'):
        raw, units = c.num('Diameter'), c.s('DiameterUnits')
        expected = pd.Series(np.where(units == 'in', raw * 25.4, raw), index=c.df.index)
        expected[~units.isin({'in', 'mm'})] = np.nan
        c.flag('DiameterInMm disagrees with Diameter + units',
               _disagrees(expected, c.num('DiameterInMm'), 1.0, 0.02),
               ['Diameter', 'DiameterUnits', 'DiameterInMm'], 'FAIL')

    if c.has('Capacity', 'CapacityUnits', 'CapacityBcm/y'):
        factor = c.s('CapacityUnits').map(BCM_PER_YEAR)
        expected = c.num('Capacity') * factor
        c.flag('CapacityBcm/y disagrees with Capacity + units',
               _disagrees(expected, c.num('CapacityBcm/y'), 0.05, 0.05),
               ['Capacity', 'CapacityUnits', 'CapacityBcm/y'], 'FAIL',
               ok_detail=f'{int((expected.notna() & c.num("CapacityBcm/y").notna()).sum())}'
                         ' rows with a convertible unit checked')

    for src, derived in [('Capacity', 'CapacityBcm/y'), ('Capacity', 'CapacityBOEd'),
                         ('Diameter', 'DiameterInMm'), ('LengthKnown', 'LengthKnownKm')]:
        if c.has(src, derived):
            c.flag(f'{src} present but {derived} blank (conversion failed)',
                   c.filled(src) & c.blank(derived), [src, derived], 'WARN')

    if c.has('StartYearEarliest'):
        starts = [c.num(x) for x in ['StartYear1', 'StartYear2', 'StartYear3']
                  if c.has(x)]
        if starts:
            lowest = pd.concat(starts, axis=1).min(axis=1)
            earliest = c.num('StartYearEarliest')
            c.flag('StartYearEarliest != min(StartYear1..3)',
                   lowest.notna() & earliest.notna() & (lowest != earliest),
                   ['StartYear1', 'StartYear2', 'StartYear3', 'StartYearEarliest'],
                   'FAIL')
            c.flag('StartYear present but StartYearEarliest blank',
                   lowest.notna() & earliest.isna(), ['StartYearEarliest'], 'WARN')

    if c.has('LengthMergedKm', 'LengthEstimateKm'):
        merged, est = c.num('LengthMergedKm'), c.num('LengthEstimateKm')
        c.flag('LengthMergedKm == 0 despite a real LengthEstimateKm',
               (merged == 0) & (est > 0),
               ['LengthKnown', 'LengthEstimateKm', 'LengthMergedKm'], 'FAIL',
               detail='LengthKnown=0 shadows the estimate — blank the 0 in the sheet')

    if c.has('NumberOfCountries', 'CountriesOrAreas'):
        counted = c.s('CountriesOrAreas').apply(
            lambda v: 0 if v in MISSING else len([p for p in v.split(',') if p.strip()]))
        declared = c.num('NumberOfCountries')
        c.flag('NumberOfCountries != len(CountriesOrAreas)',
               declared.notna() & (counted > 0) & (declared != counted),
               ['CountriesOrAreas', 'NumberOfCountries'], 'FAIL')


# ---------------------------------------------------------------------------
# Tier 4 — status <-> milestone logic
# ---------------------------------------------------------------------------

def check_status_logic(c: Checker):
    c.tier = '4. status logic'
    if not c.has('Status'):
        return c.skip('status logic', 'no Status column')
    status = c.s('Status').str.lower()

    for name, year_col in STATUS_MILESTONES:
        if not c.has(year_col):
            continue
        is_status = status == name
        c.flag(f'{name} rows missing {year_col}', is_status & c.blank(year_col),
               [year_col], 'WARN',
               ok_detail=f'{int((is_status & c.real).sum())} {name} rows')
        c.flag(f'{year_col} set on a non-{name} row',
               ~is_status & c.filled(year_col), [year_col], 'WARN')

    if c.has('ConstructionYear'):
        c.flag('construction rows missing ConstructionYear',
               (status == 'construction') & c.blank('ConstructionYear'),
               ['ConstructionYear'], 'WARN')
    if c.has('StartYear1'):
        built = status.isin(BUILT_STATUSES)
        c.flag('built rows (operating/idle/mothballed/retired) missing StartYear1',
               built & c.blank('StartYear1'), ['StartYear1'], 'WARN',
               ok_detail=f'{int((built & c.real).sum())} built rows')
        c.flag('in-development row with a StartYear1 already in the past',
               status.isin(IN_DEV_STATUSES) & (c.num('StartYear1') < c.today.year),
               ['StartYear1'], 'WARN',
               detail='either it started (status is stale) or the year needs revising')
        c.flag('operating row with a StartYear1 in the future',
               (status == 'operating') & (c.num('StartYear1') > c.today.year),
               ['StartYear1'], 'FAIL')


# ---------------------------------------------------------------------------
# Tier 5 — chronology
# ---------------------------------------------------------------------------

def check_chronology(c: Checker):
    c.tier = '5. chronology'
    hi = c.today.year + 15
    for col in YEAR_COLS:
        if not c.has(col):
            continue
        years = c.num(col)
        c.flag(f'{col} outside [1900, {hi}]',
               years.notna() & ~years.between(1900, hi), [col], 'FAIL')

    sequence = [x for x in ['ProposalYear', 'FIDYear', 'ConstructionYear',
                            'StartYear1', 'StartYear2', 'StartYear3', 'StopYear']
                if c.has(x)]
    for earlier, later in zip(sequence, sequence[1:]):
        c.flag(f'{earlier} > {later}', c.num(earlier) > c.num(later),
               [earlier, later], 'WARN')

    for later, earlier in [('StartYear2', 'StartYear1'), ('StartYear3', 'StartYear2')]:
        if c.has(later, earlier):
            c.flag(f'{later} set but {earlier} blank',
                   c.filled(later) & c.blank(earlier), [earlier, later], 'WARN')

    for month_col, year_col in MONTH_YEAR_PAIRS:
        if c.has(month_col, year_col):
            c.flag(f'{month_col} set but {year_col} blank',
                   c.filled(month_col) & c.blank(year_col),
                   [month_col, year_col], 'WARN')


# ---------------------------------------------------------------------------
# Tier 6 — plausibility bands
# ---------------------------------------------------------------------------

def check_plausibility(c: Checker):
    c.tier = '6. plausibility'

    if c.has('CapacityBcm/y'):
        bcm = c.num('CapacityBcm/y')
        c.flag(f'CapacityBcm/y above {MAX_BCM_PER_YEAR:g} bcm/y', bcm > MAX_BCM_PER_YEAR,
               ['Capacity', 'CapacityUnits', 'CapacityBcm/y'], 'WARN',
               detail='likely a unit error — check against the country total')
        c.flag('Capacity filled but converts to 0', (bcm == 0) & c.filled('Capacity'),
               ['Capacity', 'CapacityUnits', 'CapacityBcm/y'], 'NOTE',
               detail='Capacity=0 is often legitimate (a bidirectionality-only '
                      'upgrade, say) — confirm rather than assume an error')

    for col, ceiling in [('LengthMergedKm', MAX_LENGTH_KM),
                         ('LengthKnownKm', MAX_LENGTH_KM)]:
        if not c.has(col):
            continue
        km = c.num(col)
        c.flag(f'{col} above {ceiling:g} km', km > ceiling, [col], 'WARN')
        c.flag(f'{col} == 0', km == 0, [col, 'LengthEstimateKm'], 'WARN',
               detail='zeroes out length rollups')
        c.flag(f'{col} between 0 and 1 km', (km > 0) & (km < 1), [col], 'NOTE')

    if c.has('LengthMergedKm'):
        c.flag('LengthMergedKm blank', c.blank('LengthMergedKm'),
               ['LengthKnown', 'LengthEstimateKm', 'LengthMergedKm'], 'WARN')

    if c.has('Diameter', 'DiameterUnits'):
        d, u = c.num('Diameter'), c.s('DiameterUnits')
        c.flag('Diameter implausible for its units',
               ((u == 'in') & (d > MAX_DIAMETER_IN)) | ((u == 'mm') & (d > MAX_DIAMETER_MM)),
               ['Diameter', 'DiameterUnits'], 'WARN')

    for col in ['Capacity', 'LengthKnown', 'Diameter', 'Pressure',
                'SegmentCost', 'ProjectLevelCost', 'Cost']:
        if c.has(col):
            c.flag(f'{col} negative', c.num(col) < 0, [col], 'FAIL')

    # Country-relative outliers: within a country, a value far above the rest of
    # the distribution is usually a unit slip rather than a genuinely huge pipe.
    if c.has('CapacityBcm/y', 'StartCountryOrArea'):
        bcm = c.num('CapacityBcm/y')
        country = c.s('StartCountryOrArea')
        med = bcm.groupby(country).transform('median')
        n = bcm.groupby(country).transform('count')
        c.flag('CapacityBcm/y more than 25x its country median',
               (n >= 5) & (med > 0) & (bcm > 25 * med),
               ['Capacity', 'CapacityUnits', 'CapacityBcm/y', 'StartCountryOrArea'],
               'NOTE')


# ---------------------------------------------------------------------------
# Tier 7 — duplicates
# ---------------------------------------------------------------------------

def _normalize_name(s: pd.Series) -> pd.Series:
    return (s.str.lower().str.replace(r'[‐-―]', '-', regex=True)
            .str.replace(r'[^a-z0-9]+', ' ', regex=True).str.strip())


def check_duplicates(c: Checker):
    c.tier = '7. duplicates'
    key_cols = [x for x in ['PipelineName', 'SegmentName', 'CountriesOrAreas', 'Status']
                if c.has(x)]
    if not key_cols:
        return c.skip('duplicate rows', 'no name columns')

    exact = pd.Series('', index=c.df.index)
    for col in key_cols:
        exact = exact + '||' + c.s(col)
    c.flag('duplicate name + segment + countries + status',
           exact.duplicated(keep=False) & c.filled('PipelineName'),
           key_cols + ['LengthMergedKm', 'Capacity'], 'WARN')

    # Near-duplicates: same normalized name and country, lengths within 5%.
    if c.has('PipelineName', 'CountriesOrAreas', 'LengthMergedKm'):
        norm = (_normalize_name(c.s('PipelineName')) + '||'
                + _normalize_name(c.s('SegmentName')) + '||'
                + _normalize_name(c.s('CountriesOrAreas')))
        km = c.num('LengthMergedKm')
        near = pd.Series(False, index=c.df.index)
        for _, idx in c.df[c.real & c.filled('PipelineName')].groupby(norm).groups.items():
            if len(idx) < 2:
                continue
            vals = km.loc[idx]
            for i in idx:
                if pd.isna(vals[i]) or vals[i] <= 0:
                    continue
                close = vals.drop(i).dropna()
                if ((close - vals[i]).abs() <= 0.05 * vals[i]).any():
                    near[i] = True
        c.flag('near-duplicate: same name/country, length within 5%',
               near & ~exact.duplicated(keep=False),
               ['PipelineName', 'SegmentName', 'LengthMergedKm'], 'WARN')


# ---------------------------------------------------------------------------
# Tier 8 — reference coverage
# ---------------------------------------------------------------------------

def check_references(c: Checker):
    c.tier = '8. references'
    for val_col, ref_col in VALUE_REF_PAIRS:
        if not c.has(val_col, ref_col):
            continue
        unsourced = c.filled(val_col) & c.blank(ref_col)
        filled = int((c.filled(val_col) & c.real).sum())
        n = int((unsourced & c.real).sum())
        # Legacy backlog on the whole sheet; a real gate on this cycle's edits.
        c.report('NOTE' if n else 'OK', f'{val_col} unsourced ({ref_col} blank)',
                 f'{n}/{filled} rows' if n else f'{filled} rows all sourced',
                 unsourced & c.real, [val_col, ref_col])
        if c.cycle.any():
            c.flag(f'{val_col} unsourced on a cycle-touched row',
                   unsourced & c.cycle, [val_col, ref_col], 'WARN',
                   ok_detail=f'{int((c.cycle & c.filled(val_col)).sum())} cycle rows')

    if c.has('Wiki'):
        c.flag('Wiki link missing', c.blank('Wiki'), ['Wiki'], 'WARN')
        c.flag('Wiki link is not a gem.wiki URL',
               c.filled('Wiki') & ~c.s('Wiki').str.contains('gem.wiki'), ['Wiki'], 'WARN')


# ---------------------------------------------------------------------------
# Tier 9 — geographic coherence
# ---------------------------------------------------------------------------

def check_geography(c: Checker):
    c.tier = '9. geography'

    if c.has('CountriesOrAreas'):
        for col in ['StartCountryOrArea', 'EndCountryOrArea']:
            if not c.has(col):
                continue
            listed = c.s('CountriesOrAreas').apply(
                lambda v: {p.strip() for p in v.split(',')})
            val = c.s(col)
            outside = c.filled(col) & pd.Series(
                [v not in ls for v, ls in zip(val, listed)], index=c.df.index)
            c.flag(f'{col} not listed in CountriesOrAreas', outside,
                   [col, 'CountriesOrAreas'], 'WARN',
                   detail='fine for a pipeline that terminates abroad — check the '
                          'country list is complete')

    for col in ['StartCountryOrArea', 'EndCountryOrArea', 'StartRegion', 'EndRegion',
                'StartSubRegion', 'EndSubRegion']:
        if c.has(col):
            c.flag(f'{col} blank', c.blank(col), [col], 'WARN')

    # Region/sub-region should be a pure function of country.
    for country_col, attr_cols in [('StartCountryOrArea', ['StartRegion', 'StartSubRegion']),
                                   ('EndCountryOrArea', ['EndRegion', 'EndSubRegion'])]:
        for attr in attr_cols:
            if not c.has(country_col, attr):
                continue
            sub = c.df.loc[c.real & c.filled(country_col) & c.filled(attr)]
            spread = sub.groupby(c.s(country_col)[sub.index])[attr].nunique()
            offenders = set(spread[spread > 1].index)
            c.flag(f'{attr} inconsistent for the same {country_col}',
                   c.s(country_col).isin(offenders) & c.filled(attr),
                   [country_col, attr], 'FAIL',
                   detail=f'countries: {sorted(offenders)[:8]}' if offenders else '')


# ---------------------------------------------------------------------------
# Tier 10 — cross-field flag coherence
# ---------------------------------------------------------------------------

def check_cross_field(c: Checker):
    c.tier = '10. cross-field flags'

    for val_col, unit_col in VALUE_UNITS_PAIRS:
        if not c.has(val_col, unit_col):
            continue
        c.flag(f'{val_col} set but {unit_col} blank',
               c.filled(val_col) & c.blank(unit_col), [val_col, unit_col], 'FAIL')
        c.flag(f'{unit_col} set but {val_col} blank',
               c.blank(val_col) & c.filled(unit_col), [val_col, unit_col], 'WARN')

    if c.has('RouteType', 'RouteAccuracy'):
        mapped = c.s('RouteType').str.startswith('Mapped route')
        c.flag('mapped route but RouteAccuracy = "no route"',
               mapped & (c.s('RouteAccuracy') == 'no route'),
               ['RouteType', 'RouteAccuracy'], 'FAIL')
        c.flag('unmapped route but RouteAccuracy is a real accuracy',
               ~mapped & c.filled('RouteAccuracy')
               & (c.s('RouteAccuracy') != 'no route') & c.filled('RouteType'),
               ['RouteType', 'RouteAccuracy'], 'WARN')

    h2_cols = [x for x in ['H2PipelineType', 'H2%', 'H2ProposedYear', 'H2StartYear',
                           'H2Notes', 'H2RepurposedKm', 'H2NewBuildKm', 'H2Cost']
               if c.has(x)]
    if h2_cols and c.has('Fuel'):
        any_h2 = pd.Series(False, index=c.df.index)
        for col in h2_cols:
            any_h2 |= c.filled(col)
        try:
            from gem_tracker_constants import GAS_HYDROGEN_FUEL_OPTIONS
            h2_fuels = set(GAS_HYDROGEN_FUEL_OPTIONS) | set()
        except ImportError:
            h2_fuels = {'Gas and Hydrogen', 'Hydrogen'}
        declared = c.s('Fuel').isin(h2_fuels)
        c.flag('H2 fields filled but Fuel is not a hydrogen fuel', any_h2 & ~declared,
               ['Fuel'] + h2_cols[:3], 'WARN',
               detail='either the rows need a Fuel update or the convention needs '
                      'documenting — decide once, it is currently split both ways')
        c.flag('Fuel is a hydrogen fuel but no H2 fields filled', declared & ~any_h2,
               ['Fuel'] + h2_cols[:3], 'WARN')

    pci_cols = [x for x in ['PCI3', 'PCI4', 'PCI5', 'PCI6', 'DraftPCI7',
                            'PCI345ID', 'PCI6ID', 'PCI6ProjectCode', 'DraftPCI6List']
                if c.has(x)]
    if pci_cols and c.has('EuropeTracker'):
        any_pci = pd.Series(False, index=c.df.index)
        for col in pci_cols:
            any_pci |= c.filled(col)
        c.flag('PCI code set but EuropeTracker blank', any_pci & c.blank('EuropeTracker'),
               ['EuropeTracker'] + pci_cols[:4], 'WARN',
               detail='a PCI code on a non-European pipeline is usually a fill-down slip')
    if c.has('EuropeTracker', 'StartRegion', 'EndRegion'):
        touches_europe = (c.s('StartRegion') == 'Europe') | (c.s('EndRegion') == 'Europe')
        c.flag('EuropeTracker = yes but neither endpoint is in Europe',
               (c.s('EuropeTracker') == 'yes') & ~touches_europe,
               ['EuropeTracker', 'StartRegion', 'EndRegion'], 'WARN')
        c.flag('European pipeline without EuropeTracker = yes',
               touches_europe & c.blank('EuropeTracker'),
               ['EuropeTracker', 'StartRegion', 'EndRegion'], 'NOTE')

    for owner_col, id_col in [('Owner', 'ParentEntityIDs'), ('Parent', 'ParentEntityIDs'),
                              ('Owner', 'OwnerEntityIDs')]:
        if not c.has(owner_col, id_col):
            continue
        c.flag(f'{owner_col} set but {id_col} blank',
               c.filled(owner_col) & c.blank(id_col), [owner_col, id_col], 'WARN')
    for id_col in ['ParentEntityIDs', 'OwnerEntityIDs']:
        if not c.has(id_col):
            continue
        vals = c.s(id_col)
        c.flag(f'{id_col} = "unknown"', vals.str.lower() == 'unknown', [id_col], 'NOTE',
               detail='an explicit placeholder, not a malformed ID')
        c.flag(f'{id_col} malformed (not an E<digits> list)',
               c.filled(id_col) & (vals.str.lower() != 'unknown')
               & ~vals.str.fullmatch(r'E\d+(?:\s*[;,]\s*E\d+)*'), [id_col], 'WARN')

    if c.has('Fuel'):
        # A gas tab should hold gas; an oil tab should hold oil/NGL.
        gas_tab = c.has('CapacityBcm/y')
        wrong = (c.s('Fuel') == 'Oil') if gas_tab else c.s('Fuel').isin({'Gas'})
        c.flag('row filed on the wrong tracker tab for its Fuel', wrong, ['Fuel'], 'FAIL')


# ---------------------------------------------------------------------------
# Tier 11 — text hygiene
# ---------------------------------------------------------------------------

TEXT_COLS = ['PipelineName', 'PipelineNetworkGrouping', 'SegmentName',
             'CountriesOrAreas', 'Owner', 'Parent', 'Researcher', 'Status', 'Fuel',
             'PipelineType', 'StartLocation', 'EndLocation', 'StartCountryOrArea',
             'EndCountryOrArea', 'StartState/Province', 'EndState/Province']


def check_text_hygiene(c: Checker):
    c.tier = '11. text hygiene'
    for col in TEXT_COLS:
        if not c.has(col):
            continue
        raw = c.df[col].astype(str)
        stripped = raw.str.strip()
        c.flag(f'{col} has leading/trailing whitespace',
               (raw != stripped) & (stripped != ''), [col], 'WARN',
               detail='splits the value into two distinct keys in every group-by')
        c.flag(f'{col} has a doubled space', stripped.str.contains('  '), [col], 'NOTE')
        c.flag(f'{col} has a non-breaking or zero-width space',
               raw.str.contains(' |​|﻿', regex=True), [col], 'WARN')


# ---------------------------------------------------------------------------
# Tier 12 — staleness and cycle coverage
# ---------------------------------------------------------------------------

def check_staleness(c: Checker):
    c.tier = '12. staleness'
    if not c.has('LastUpdated'):
        return c.skip('staleness', 'no LastUpdated column')

    lu = c.last_updated
    c.flag('LastUpdated unparseable', c.filled('LastUpdated') & lu.isna(),
           ['LastUpdated'], 'FAIL')
    c.flag('LastUpdated blank', c.blank('LastUpdated'), ['LastUpdated'], 'WARN')
    c.flag('LastUpdated in the future', lu > c.today, ['LastUpdated'], 'FAIL')
    if c.has('Researcher'):
        c.flag('Researcher initials missing', c.blank('Researcher'),
               ['Researcher', 'LastUpdated'], 'WARN')

    cutoff = c.today - pd.DateOffset(months=12)
    c.flag('not updated in over 12 months', lu < cutoff, ['LastUpdated'], 'NOTE',
           detail=f'oldest {lu.min():%Y-%m-%d}' if lu.notna().any() else '')
    if c.has('Status'):
        in_dev = c.s('Status').str.lower().isin(IN_DEV_STATUSES)
        c.flag('in-development row not updated in over 12 months', in_dev & (lu < cutoff),
               ['LastUpdated'], 'WARN',
               detail=f'of {int((in_dev & c.real).sum())} in-development rows; this is '
                      'the population where status decay actually matters')

    if c.cycle_start is None:
        return c.skip('cycle coverage', 'no --cycle-start given')
    n = int((c.cycle & c.real).sum())
    c.report('NOTE', 'rows touched this cycle',
             f'{n} rows stamped on/after {c.cycle_start:%Y-%m-%d}', c.cycle & c.real,
             ['LastUpdated', 'Researcher'])
    if c.has('Researcher'):
        by_researcher = c.s('Researcher')[c.cycle & c.real].value_counts()
        c.report('NOTE', 'cycle rows by researcher', str(by_researcher.to_dict()))
    if c.has('StartCountryOrArea'):
        by_country = c.s('StartCountryOrArea')[c.cycle & c.real].value_counts()
        c.report('NOTE', 'cycle rows by country', str(by_country.head(20).to_dict()))

    required = [x for x in ['PipelineName', 'Status', 'Fuel', 'CountriesOrAreas',
                            'Researcher', 'LengthMergedKm', 'PipelineType']
                if c.has(x)]
    for col in required:
        c.flag(f'cycle row missing {col}', c.cycle & c.blank(col), [col], 'WARN')


CHECKS = [check_shape, check_vocabularies, check_types, check_derived,
          check_status_logic, check_chronology, check_plausibility,
          check_duplicates, check_references, check_geography, check_cross_field,
          check_text_hygiene, check_staleness]


def run_all(df: pd.DataFrame, cycle_start=None, today=None) -> list[Finding]:
    """Run every check over ``df`` and return the findings in tier order."""
    c = Checker(df, cycle_start=cycle_start, today=today)
    for check in CHECKS:
        check(c)
    return c.findings


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

LEVEL_ORDER = {'FAIL': 0, 'WARN': 1, 'NOTE': 2, 'SKIP': 3, 'OK': 4}


def print_findings(findings: list[Finding], levels=('FAIL', 'WARN', 'NOTE', 'SKIP', 'OK'),
                   detail=True):
    """One line per check, grouped by tier."""
    tier = None
    for f in findings:
        if f.level not in levels:
            continue
        if f.tier != tier:
            tier = f.tier
            print(f'\n--- {tier} ---')
        line = f'[{f.level:4}] {f.name}'
        if detail and f.detail:
            line += f' — {f.detail}'
        print(line[:400])


def print_summary(findings: list[Finding]) -> int:
    """Print the FAIL/WARN roll-up. Returns the number of failing checks."""
    fails = [f for f in findings if f.level == 'FAIL']
    warns = [f for f in findings if f.level == 'WARN']
    print('\n' + '=' * 72)
    for label, group in [('FAIL', fails), ('WARN', warns)]:
        if not group:
            continue
        print(f'\n{label} ({len(group)} checks):')
        for f in sorted(group, key=lambda x: -x.count):
            print(f'  {f.count:>6}  {f.name}')
    print(f"\n{'FAILED' if fails else 'PASSED'}: {len(fails)} failing, "
          f'{len(warns)} warning check(s)')
    return len(fails)


def flagged_rows(df: pd.DataFrame, findings: list[Finding],
                 levels=('FAIL', 'WARN')) -> pd.DataFrame:
    """Long-form table of every flagged row: one row per (check, ProjectID)."""
    frames = []
    for f in findings:
        if f.level not in levels or not f.count:
            continue
        rows = f.rows(df)
        frames.append(rows.assign(qc_level=f.level, qc_tier=f.tier, qc_check=f.name)
                      [['qc_level', 'qc_tier', 'qc_check'] + list(rows.columns)])
    if not frames:
        return pd.DataFrame(columns=['qc_level', 'qc_tier', 'qc_check', 'ProjectID'])
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values(['qc_level', 'qc_tier', 'qc_check', 'ProjectID'],
                           key=lambda s: s.map(LEVEL_ORDER) if s.name == 'qc_level' else s)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__.split('\n\n')[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Reads are read-only and go through the sibling gem-db-ops repo.')
    p.add_argument('--tracker', default='ggit', choices=['ggit', 'goit'],
                   help="which tracker tab to check (default: ggit)")
    p.add_argument('--csv', help='check a CSV already pulled by gem-db-ops '
                                 'instead of reading the live sheet')
    p.add_argument('--header-row', type=int, default=2,
                   help='0-indexed header row in --csv (default: 2)')
    p.add_argument('--cycle-start', help='YYYY-MM-DD; enables the cycle-row checks')
    p.add_argument('--dump-rows', metavar='PATH',
                   help='write every flagged row to this CSV')
    p.add_argument('--levels', default='FAIL,WARN,NOTE,SKIP',
                   help='levels to print (default: all but OK)')
    p.add_argument('--today', help='YYYY-MM-DD; override "now" for the date checks')
    args = p.parse_args(argv)

    df = load_csv(args.csv, args.header_row) if args.csv else load_live(args.tracker)
    source = args.csv or f'live "{args.tracker}" tab'
    print(f'QC of {source} — {len(df)} rows x {len(df.columns)} columns')
    if args.cycle_start:
        print(f'cycle start {args.cycle_start}')

    findings = run_all(df, cycle_start=args.cycle_start, today=args.today)
    print_findings(findings, levels=tuple(args.levels.split(',')))
    n_fail = print_summary(findings)

    if args.dump_rows:
        rows = flagged_rows(df, findings)
        rows.to_csv(args.dump_rows, index=False)
        print(f'\nwrote {len(rows)} flagged rows to {args.dump_rows}')
    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(main())
