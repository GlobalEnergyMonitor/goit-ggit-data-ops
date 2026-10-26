"""Canonical fuel buckets and status orderings for GEM tracker workflows.

Source of truth for the lists that GOIT/GGIT release notebooks would
otherwise re-declare inline (and drift out of sync).
"""

from __future__ import annotations

from ._loader import FUEL_ALIASES, FUELS, STATUSES
from .helpers import (
    SYSTEM_INFO_SEGMENT,
    collapse_gas_and_hydrogen,
    drop_system_info_rows,
    find_uncovered_fuels,
    is_system_info_row,
    normalize_fuels,
)

__version__ = "0.8.0"

# Fuel buckets — raw `Fuel` column values that count as each fuel type.
GAS_FUEL_OPTIONS: list[str] = FUELS["gas"]
GAS_HYDROGEN_FUEL_OPTIONS: list[str] = FUELS["gas_hydrogen"]
HYDROGEN_FUEL_OPTIONS: list[str] = FUELS["hydrogen"]
# The oil/ngl buckets are the canonical classification used by the
# data-requests release downloads and qc summary tables. Refined-product-only
# strings ('Oil products (only)', 'Naphtha (only)', 'Naphtha, oil products')
# and standalone 'Condensate' are neither Oil nor NGL; they appear only in
# OIL_NGL_COMBINED. See fuels.yaml for the full classification rule.
OIL_FUEL_OPTIONS: list[str] = FUELS["oil"]
NGL_FUEL_OPTIONS: list[str] = FUELS["ngl"]
OIL_NGL_COMBINED: list[str] = FUELS["oil_ngl_combined"]
# Raw Fuel strings that count as a bucket entry ('Coke oven gas' -> 'Gas').
FUEL_ALIASES: dict[str, str] = FUEL_ALIASES

# Pipeline statuses — GOIT/GGIT use lowercase.
PIPELINE_STATUS: list[str] = STATUSES["pipeline"]["base"]
PIPELINE_EXCEL_STATUS: list[str] = STATUSES["pipeline"]["excel"]
PIPELINE_IN_DEV_COL: str = STATUSES["pipeline_in_dev_col"]

# Terminal statuses — LNG terminal tracker uses Title case.
TERMINAL_STATUS: list[str] = STATUSES["terminal"]["base"]
TERMINAL_EXCEL_STATUS: list[str] = STATUSES["terminal"]["excel"]
TERMINAL_IN_DEV_COL: str = STATUSES["terminal_in_dev_col"]

__all__ = [
    "__version__",
    "GAS_FUEL_OPTIONS",
    "GAS_HYDROGEN_FUEL_OPTIONS",
    "HYDROGEN_FUEL_OPTIONS",
    "OIL_FUEL_OPTIONS",
    "NGL_FUEL_OPTIONS",
    "OIL_NGL_COMBINED",
    "FUEL_ALIASES",
    "PIPELINE_STATUS",
    "PIPELINE_EXCEL_STATUS",
    "PIPELINE_IN_DEV_COL",
    "TERMINAL_STATUS",
    "TERMINAL_EXCEL_STATUS",
    "TERMINAL_IN_DEV_COL",
    "SYSTEM_INFO_SEGMENT",
    "collapse_gas_and_hydrogen",
    "drop_system_info_rows",
    "find_uncovered_fuels",
    "is_system_info_row",
    "normalize_fuels",
]
