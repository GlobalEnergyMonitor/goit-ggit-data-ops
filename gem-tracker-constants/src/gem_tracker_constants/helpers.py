"""Behavioral helpers that belong with the constants.

Kept here (not in the YAML) because they encode rules, not data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from ._loader import FUEL_ALIASES, FUELS

if TYPE_CHECKING:
    import pandas as pd


def collapse_gas_and_hydrogen(
    df: "pd.DataFrame", fuel_col: str = "Fuel"
) -> "pd.DataFrame":
    """Rewrite 'Gas and Hydrogen' to 'Gas' in `fuel_col`.

    Used when running a gas-only analysis on GGIT data — the gas fuel bucket
    includes both 'Gas' and 'Gas and Hydrogen', but downstream aggregation
    wants a single label. Returns the same DataFrame (mutates in place).
    """
    mask = df[fuel_col] == "Gas and Hydrogen"
    df.loc[mask, fuel_col] = "Gas"
    return df


def _canonical_fuel_map() -> dict[str, str]:
    """casefolded raw string -> canonical bucket spelling, aliases included."""
    canon = {v.casefold(): v for bucket in FUELS.values() for v in bucket}
    canon.update({k.casefold(): v for k, v in FUEL_ALIASES.items()})
    return canon


def normalize_fuels(
    df: "pd.DataFrame", fuel_col: str = "Fuel"
) -> "pd.DataFrame":
    """Rewrite `fuel_col` to the canonical bucket spelling.

    Run before any `Fuel.isin(<bucket>)` filter: the buckets are case-sensitive
    and the tracker sheets are not ('gas' vs 'Gas'). Matching strips
    whitespace and ignores case; aliases from fuels.yaml are applied too
    ('coke oven gas' -> 'Gas'). Values that match nothing are left untouched so
    they still surface in find_uncovered_fuels(). Returns the same DataFrame
    (mutates in place).
    """
    canon = _canonical_fuel_map()
    raw = df[fuel_col]
    mapped = raw.map(
        lambda v: canon.get(v.strip().casefold(), v) if isinstance(v, str) else v
    )
    df[fuel_col] = mapped
    return df


# SegmentName prefix of the per-system summary rows. They describe a whole
# network (often with its total km) alongside the segment rows, so counting
# them in a release double-counts or adds km that has no segment breakdown.
# 'SYSTEM/NETWORK ROUTE' rows carry a real route and are kept.
SYSTEM_INFO_SEGMENT = "SYSTEM/NETWORK INFO"


def is_system_info_row(
    df: "pd.DataFrame", segment_col: str = "SegmentName"
) -> "pd.Series":
    """Boolean mask of SYSTEM/NETWORK INFO rows (case and whitespace ignored)."""
    import pandas as pd

    if segment_col not in df.columns:
        return pd.Series(False, index=df.index)
    seg = df[segment_col].astype(str).str.strip().str.upper()
    return seg.str.startswith(SYSTEM_INFO_SEGMENT)


def drop_system_info_rows(
    df: "pd.DataFrame", segment_col: str = "SegmentName"
) -> "pd.DataFrame":
    """Return `df` without its SYSTEM/NETWORK INFO rows (a new DataFrame).

    Release outputs (downloads, map, summary sheets) leave these rows out.
    Matches 'SYSTEM/NETWORK INFO' and variants such as
    'SYSTEM/NETWORK INFO (Main Line)'.
    """
    return df[~is_system_info_row(df, segment_col)].copy()


def find_uncovered_fuels(
    data: "pd.DataFrame | pd.Series | Iterable[str]",
    fuel_col: str = "Fuel",
    buckets: Iterable[str] | None = None,
    verbose: bool = True,
) -> list[str]:
    """Report the unique `Fuel` values in `data` not covered by any bucket.

    QC check for the tracker backend: pass the pipelines DataFrame (or just
    its Fuel column) and get back the fuel strings that none of the buckets
    in fuels.yaml would catch — i.e. pipelines that would silently drop out
    of every filter. Run it after pulling a fresh copy of the backend so new
    or mistyped Fuel values surface immediately.

    `data` may be a DataFrame (uses `fuel_col`), a Series, or any iterable of
    strings. `buckets` narrows the check to specific bucket names from
    fuels.yaml (e.g. ['oil', 'ngl']); default is all of them. Case is ignored
    and aliases count as covered, matching normalize_fuels(). NaN/None values
    are ignored. When `verbose`, prints each uncovered value as a repr so
    stray whitespace and case differences are visible.
    """
    values = data[fuel_col] if hasattr(data, "columns") else data
    unique = values.unique() if hasattr(values, "unique") else set(values)

    names = list(buckets) if buckets is not None else list(FUELS)
    covered = set()
    for name in names:
        covered.update(FUELS[name])

    # Same matching as normalize_fuels(), except stray whitespace is still
    # reported so it gets fixed in the sheet.
    canon = _canonical_fuel_map()
    uncovered = sorted(
        v for v in unique
        if isinstance(v, str) and canon.get(v.casefold(), v) not in covered
    )
    if verbose:
        if uncovered:
            print(f"{len(uncovered)} fuel value(s) not covered by {names}:")
            for v in uncovered:
                print(f"  {v!r}")
        else:
            print(f"all fuel values covered by {names}")
    return uncovered
