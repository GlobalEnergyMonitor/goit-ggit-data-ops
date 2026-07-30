"""GEM pipeline data-file exports: library + CLI.

Single source of truth for the logic behind
convert-ggit-goit-to-tracker-release-downloads.ipynb (the notebook imports
from this module) and for CI map builds
(.github/workflows/build-map-data.yml).

Which to use when: run THIS module as a CLI for a standard, no-inspection
release run (one command, outputs in data-files/); use the notebook when you
want to inspect as you go (tweak config, eyeball the ID-reconciliation
report and dataframes before exporting, ad-hoc filtered data requests).
Either way, logic changes go here — never in notebook cells.

Pipeline modes: Oil-NGL | Oil | NGL | Gas | Gas-Hydrogen | Hydrogen | Oil-and-Gas

CLI examples:

    # full release exports (xlsx/geojson/gpkg/shp) into data-files/
    python pipeline_exports.py --pipeline-type Oil-NGL --simplify-fuels Oil-and-NGL

    # map geojson only (what CI runs)
    python pipeline_exports.py --pipeline-type Oil-NGL --simplify-fuels Oil-and-NGL \
        --routes-path /path/to/pipeline-routes/data/individual-routes \
        --map-only --map-output out/goit_map_latest.geojson

Requires the GDRIVE_API_CREDENTIALS env var (Google service-account JSON)
and an on-disk checkout of the goit-ggit-pipeline-routes `normalized` branch.
"""

import argparse
import datetime
import os
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import geopandas as gpd
import pygsheets
from shapely import set_precision

# Canonical fuel buckets. Source of truth: the in-repo gem-tracker-constants
# package (repo root; `pip install ./gem-tracker-constants` or editable).
# OIL_FUEL_OPTIONS / NGL_FUEL_OPTIONS define which raw Fuel values qualify as
# Oil / NGL pipelines — used by simplify_fuel_types() for the simplified
# release downloads, and by the QC summary sheets, so the two align.
from gem_tracker_constants import (
    GAS_FUEL_OPTIONS,
    GAS_HYDROGEN_FUEL_OPTIONS,
    HYDROGEN_FUEL_OPTIONS,
    OIL_NGL_COMBINED,
    OIL_FUEL_OPTIONS,
    NGL_FUEL_OPTIONS,
    collapse_gas_and_hydrogen,
)

PIPELINES_SHEET_KEY = '1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek'

# Local default for interactive runs; CI passes --routes-path to its own
# checkout of the `normalized` branch instead.
DEFAULT_ROUTES_PATH = (
    '/Users/baird/Dropbox/_git_ALL/_github-repos-gem/'
    'goit-ggit-pipeline-routes-normalized/data/individual-routes/'
)

ALL_FORMATS = ('xlsx', 'geojson', 'gpkg', 'shp')

# Publish guardrails for map output: a degraded run (empty routes checkout,
# sheet fetch gone wrong) must never overwrite the public map file.
MIN_MAP_FEATURES = 1000
MIN_MAP_BYTES = 10 * 1024 * 1024
MAX_MAP_BYTES = 95 * 1024 * 1024  # raw.githubusercontent.com can't serve blobs >100 MB

# Map pipeline type to the relevant repo folder(s)
FOLDER_MAP = {
    'Oil-NGL':      ['liquid-pipelines'],
    'Oil':          ['liquid-pipelines'],
    'NGL':          ['liquid-pipelines'],
    'Gas':          ['gas-pipelines'],
    'Gas-Hydrogen': ['gas-pipelines', 'hydrogen-pipelines'],
    'Hydrogen':     ['hydrogen-pipelines'],
    'Oil-and-Gas':  ['liquid-pipelines', 'gas-pipelines', 'hydrogen-pipelines'],
}


def refresh_routes(routes_path):
    """git pull the pinned routes worktree so exports use fresh geometries.

    Fast-forward only. On any failure (offline, dirty worktree, non-ff),
    warns and falls back to the on-disk files rather than blocking the run.
    """
    import subprocess
    repo = str(Path(routes_path))
    try:
        branch = subprocess.run(
            ['git', '-C', repo, 'branch', '--show-current'],
            capture_output=True, text=True, timeout=30).stdout.strip()
        r = subprocess.run(
            ['git', '-C', repo, 'pull', '--ff-only'],
            capture_output=True, text=True, timeout=180)
        if r.returncode == 0:
            msg = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else 'ok'
            print(f"✓ Routes worktree ('{branch}'): {msg}")
        else:
            print(f"⚠ Routes pull failed on '{branch}' — using existing files:\n"
                  f"  {r.stderr.strip()}")
    except Exception as exc:
        print(f"⚠ Could not refresh routes — using existing files: {exc}")


def get_config(ptype):
    """Pipeline configuration lookup. Fuel buckets come from
    gem-tracker-constants; 'CO2' is kept inline because it isn't part
    of the canonical oil/NGL bucket but the GOIT export includes it."""
    configs = {
        'Oil-NGL': {
            'fuel_options': list(OIL_NGL_COMBINED) + ['CO2'],
            'folder': 'liquid-pipelines', 'tracker': 'GOIT',
            'sheet': 'Oil/NGL pipelines', 'dict_sheet': 'Data dictionary - Oil/NGL pipelines',
            'copyright_sheet': 'Copyright - GOIT'
        },
        'Oil': {
            'fuel_options': list(OIL_FUEL_OPTIONS),
            'folder': 'liquid-pipelines', 'tracker': 'GOIT',
            'sheet': 'Oil/NGL pipelines', 'dict_sheet': 'Data dictionary - Oil/NGL pipelines',
            'copyright_sheet': 'Copyright - GOIT'
        },
        'NGL': {
            'fuel_options': list(NGL_FUEL_OPTIONS),
            'folder': 'liquid-pipelines', 'tracker': 'GOIT',
            'sheet': 'Oil/NGL pipelines', 'dict_sheet': 'Data dictionary - Oil/NGL pipelines',
            'copyright_sheet': 'Copyright - GOIT'
        },
        'Gas': {
            'fuel_options': list(GAS_FUEL_OPTIONS),
            'folder': 'gas-pipelines', 'tracker': 'GGIT',
            'sheet': 'Gas pipelines', 'dict_sheet': 'Data dictionary - Gas pipelines',
            'copyright_sheet': 'Copyright - GGIT'
        },
        'Gas-Hydrogen': {
            'fuel_options': list(GAS_HYDROGEN_FUEL_OPTIONS),
            'folder': 'gas-pipelines', 'tracker': 'GGIT',
            'sheet': 'Gas pipelines', 'dict_sheet': 'Data dictionary - Gas pipelines',
            'copyright_sheet': 'Copyright - GGIT'
        },
        'Hydrogen': {
            'fuel_options': list(HYDROGEN_FUEL_OPTIONS),
            'folder': 'gas-pipelines', 'tracker': 'GGIT',
            'sheet': 'Gas pipelines', 'dict_sheet': 'Data dictionary - Gas pipelines',
            'copyright_sheet': 'Copyright - GGIT'
        },
        'Oil-and-Gas': {
            'fuel_options': list(OIL_NGL_COMBINED) + ['CO2'] + list(GAS_FUEL_OPTIONS),
            'folder': None, 'tracker': 'GOIT-GGIT', 'sheet': None, 'dict_sheet': None, 'copyright_sheet': None
        }
    }
    return configs[ptype]


def fetch_pipeline_data(ss, config):
    """Fetch and initial filter of pipeline data from a worksheet."""
    t0 = time.time()
    df = ss.worksheet('title', config['sheet']).get_as_df(start='A3', include_tailing_empty=False)
    df_dict = ss.worksheet('title', config['dict_sheet']).get_as_df(include_tailing_empty=False)
    df_copy = ss.worksheet('title', config['copyright_sheet']).get_as_df(include_tailing_empty=False)
    print(f"  Sheets fetched in {time.time() - t0:.1f}s")

    if df_copy.shape[1] > 1:
        df_copy = pd.DataFrame(df_copy.iloc[:, 0])

    # Standard initial filters
    mask = (
        df['Fuel'].isin(config['fuel_options']) &
        (df['Status'] != 'N/A') &
        (df['PipelineName'] != '') &
        (df['RouteAccuracy'] != '')
    )
    df = df[mask].copy()

    # Dataset-specific adjustments
    if config['tracker'] == 'GGIT':
        collapse_gas_and_hydrogen(df)

    return df, df_dict, df_copy


def filter_by_countries(df, countries, col='CountriesOrAreas'):
    """Filter dataframe by country list."""
    if not countries:
        return df
    # word boundaries so e.g. 'Niger' doesn't also match 'Nigeria'
    pattern = r'\b(?:' + '|'.join(re.escape(c) for c in countries) + r')\b'
    mask = df[col].astype(str).str.contains(pattern, na=False)
    return df[mask]


def filter_by_status(df, statuses, col='Status'):
    """Filter dataframe by status list."""
    if not statuses:
        return df
    mask = df[col].isin(statuses)
    filtered = df[mask]
    print(f"  Status filter {statuses}: {len(df)} → {len(filtered)} rows")
    return filtered


def simplify_fuel_types(df, strategy):
    """Relabel fuels using the canonical buckets from gem-tracker-constants
    and drop rows outside the requested category.

      - 'Oil':         rows with Fuel in OIL_FUEL_OPTIONS -> 'Oil'
      - 'NGL':         rows with Fuel in NGL_FUEL_OPTIONS -> 'NGL'
      - 'Oil-and-NGL': union of the two; oil-bucket rows -> 'Oil',
                       ngl-bucket rows -> 'NGL'. The buckets are disjoint:
                       dual-fuel strings ('Oil, NGL', 'Oil, NGL, naphtha')
                       live in the oil bucket, so they become 'Oil'
      - 'Gas':         rows with Fuel in GAS_FUEL_OPTIONS -> 'Gas'
    """
    if not strategy or strategy == 'None':
        return df

    oil_fuels, ngl_fuels = set(OIL_FUEL_OPTIONS), set(NGL_FUEL_OPTIONS)
    before = len(df)

    if strategy == 'Oil':
        df = df[df['Fuel'].isin(oil_fuels)].copy()
        df['Fuel'] = 'Oil'
    elif strategy == 'NGL':
        df = df[df['Fuel'].isin(ngl_fuels)].copy()
        df['Fuel'] = 'NGL'
    elif strategy == 'Oil-and-NGL':
        df = df[df['Fuel'].isin(oil_fuels | ngl_fuels)].copy()
        oil_mask = df['Fuel'].isin(oil_fuels)
        ngl_mask = df['Fuel'].isin(ngl_fuels) & ~oil_mask
        df.loc[oil_mask, 'Fuel'] = 'Oil'
        df.loc[ngl_mask, 'Fuel'] = 'NGL'
    elif strategy == 'Gas':
        df = df[df['Fuel'].isin(GAS_FUEL_OPTIONS)].copy()
        df['Fuel'] = 'Gas'

    dropped = before - len(df)
    if dropped:
        print(f"  Fuel simplification '{strategy}': dropped {dropped} rows with non-matching fuels")

    return df


def _count_geom_points(geom):
    """Count total coordinate points across all parts of a geometry."""
    if hasattr(geom, 'geoms'):
        return sum(_count_geom_points(g) for g in geom.geoms)
    coords = getattr(geom, 'coords', None)
    return len(coords) if coords is not None else 0


def _scan_route_files(routes_path):
    """Pre-scan a routes directory and return a set of available ProjectIDs."""
    try:
        return {os.path.splitext(f)[0] for f in os.listdir(routes_path) if f.endswith('.geojson')}
    except FileNotFoundError:
        return set()


def check_no_route_geojson_files(df, routes_path):
    """Check all 'no route' pipelines against geojson files on disk.

    Flags pipelines where the sheet says 'no route' but the geojson file
    in the GitHub routes directory has actual geometry. Separates into
    simple routes (<=5 points, should be nulled) and complex routes
    (>5 points, need review).
    """
    no_route_mask = df['RouteAccuracy'].str.lower().str.strip() == 'no route'
    no_route_pids = (
        df.loc[no_route_mask, 'ProjectID']
        .astype(str).str.strip()
        .loc[lambda s: (s != '') & s.notna()]
        .unique()
    )

    if len(no_route_pids) == 0:
        print("  No-route check: no 'no route' pipelines found in sheet")
        return

    available_files = _scan_route_files(routes_path)

    simple = []   # <=5 points
    complex_ = [] # >5 points
    read_errors = []
    for pid in no_route_pids:
        if pid not in available_files:
            continue
        route_file = routes_path / f"{pid}.geojson"
        try:
            gdf = gpd.read_file(route_file)
            if gdf.empty or gdf.geometry.isna().all():
                continue
            geom = gdf.geometry.union_all() if hasattr(gdf.geometry, 'union_all') else gdf.unary_union
            n_pts = _count_geom_points(geom)
            if n_pts <= 5:
                simple.append((pid, n_pts))
            else:
                complex_.append((pid, n_pts))
        except Exception as exc:
            read_errors.append((pid, str(exc)))

    if not simple and not complex_:
        print(f"  ✓ No-route check: all {len(no_route_pids)} 'no route' pipelines "
              f"have null/missing geojson files")
        if read_errors:
            print(f"  ⚠ {len(read_errors)} file(s) failed to read: {[pid for pid, _ in read_errors]}")
        return

    total = len(simple) + len(complex_)
    print(f"  ⚠ NO-ROUTE CONFLICT: {total} pipeline(s) marked 'no route' in sheet "
          f"but have geometry in geojson files:")

    if simple:
        print(f"\n    Simple routes (<=5 points, should be nulled) — {len(simple)}:")
        for pid, n in sorted(simple):
            print(f"      {pid} ({n} pts)")

    if complex_:
        print(f"\n    Complex routes (>5 points, need review) — {len(complex_)}:")
        for pid, n in sorted(complex_):
            print(f"      {pid} ({n} pts)")

    if read_errors:
        print(f"\n    ⚠ Failed to read {len(read_errors)} file(s):")
        for pid, reason in read_errors:
            print(f"      {pid}: {reason}")


def enforce_no_route_null_geometry(df):
    """Ensure pipelines with 'no route' RouteAccuracy have null geometry in export."""
    no_route_mask = df['RouteAccuracy'].str.lower().str.strip() == 'no route'
    no_route_count = no_route_mask.sum()
    if no_route_count == 0:
        return df

    df = df.copy()
    had_geometry = no_route_mask & df['geometry'].notna()
    bad_count = had_geometry.sum()

    if bad_count > 0:
        bad_ids = df.loc[had_geometry, 'ProjectID'].tolist()
        print(f"  ⚠ {bad_count} 'no route' pipeline(s) had non-null geometry — set to null: {bad_ids}")

    df.loc[no_route_mask, 'geometry'] = None
    print(f"  ✓ No-route export fix: {no_route_count} 'no route' pipelines set to null geometry")
    return df


def load_geometries(df, routes_path, name, progress_every=25):
    """Load route geometries for pipelines sequentially (GDAL is not thread-safe)."""
    df = df.copy()
    pid_series = df['ProjectID'].astype('string').str.strip()
    unique_ids = pid_series[pid_series.notna() & (pid_series != '')].unique().tolist()
    geom_map = {}
    missing = []
    failed = []
    start = time.time()

    # Pre-scan directory to avoid per-file existence checks
    available_files = _scan_route_files(routes_path)

    print(f"Loading {name} geometries ({len(unique_ids)} unique IDs, {len(available_files)} files on disk)...")

    for idx, pid in enumerate(unique_ids, 1):
        if pid not in available_files:
            missing.append(pid)
            continue

        route_file = routes_path / f"{pid}.geojson"
        try:
            gdf = gpd.read_file(route_file)
            if gdf.empty or gdf.geometry.isna().all():
                missing.append(pid)
                continue
            geom = gdf.geometry.union_all() if hasattr(gdf.geometry, 'union_all') else gdf.unary_union
            geom_map[pid] = set_precision(geom, grid_size=1e-6)
        except Exception as exc:
            failed.append((pid, str(exc)))

        if idx % progress_every == 0 or idx == len(unique_ids):
            elapsed = time.time() - start
            print(f"  {idx}/{len(unique_ids)} ({idx/len(unique_ids)*100:.0f}%) | elapsed {elapsed:.1f}s")

    df['geometry'] = pid_series.map(geom_map)
    print(f"  ✓ Loaded: {len(geom_map)}/{len(unique_ids)} unique files | Missing: {len(missing)} | Failed: {len(failed)}")
    if failed:
        sample = '; '.join([f"{pid}: {reason}" for pid, reason in failed[:10]])
        suffix = ' ...' if len(failed) > 10 else ''
        print(f"  Failed samples: {sample}{suffix}")

    df = enforce_no_route_null_geometry(df)
    return df


def export_files(gdf, base_name, dict_df=None, acronyms_df=None, copyright_df=None,
                 formats=ALL_FORMATS):
    """Export to Excel, GeoJSON, GeoPackage, and/or zipped Shapefile.

    `formats` selects which of ('xlsx', 'geojson', 'gpkg', 'shp') to write;
    default is all four (the release handoff set).
    """
    files = []
    t0 = time.time()

    # Shapefile field names: deliberate <=10-char names from the data
    # dictionary's ShapefileFieldName column (the tracker sheet is the
    # source of truth). Columns without an entry keep their full name and
    # GDAL truncates them at write time.
    shp_fields = {}
    if 'shp' in formats:
        if dict_df is not None and 'ShapefileFieldName' in dict_df.columns:
            pairs = dict_df[['VariableName', 'ShapefileFieldName']].astype(str)
            shp_fields = {v: s.strip() for v, s in pairs.itertuples(index=False)
                          if s.strip() not in ('', 'nan')}
            data_cols = [c for c in gdf.columns if c != 'geometry']
            missing = [c for c in data_cols if c not in shp_fields]
            if missing:
                print(f"  ⚠ no ShapefileFieldName for {len(missing)} column(s) — GDAL will truncate: {missing}")
            shorts = [shp_fields[c] for c in data_cols if c in shp_fields]
            too_long = sorted({s for s in shorts if len(s) > 10})
            dupes = sorted({s for s in shorts if shorts.count(s) > 1})
            if too_long or dupes:
                raise ValueError(f"bad ShapefileFieldName values in data dictionary — "
                                 f">10 chars: {too_long}, duplicates: {dupes}")
        elif dict_df is not None:
            print("  ⚠ reminder: this data dictionary has no ShapefileFieldName column — "
                  "add one to the tracker sheet (see the Oil/NGL dictionary for the "
                  "pattern) so shapefile field names aren't GDAL-truncated")

    # Excel
    if 'xlsx' in formats:
        xlsx = f"{base_name}.xlsx"
        with pd.ExcelWriter(xlsx, engine='openpyxl') as writer:
            gdf.drop(columns=['geometry']).to_excel(writer, sheet_name='Data', index=False)
            if dict_df is not None:
                dict_df.to_excel(writer, sheet_name='Data dictionary', index=False)
            if acronyms_df is not None:
                acronyms_df.to_excel(writer, sheet_name='Acronyms', index=False)
            if copyright_df is not None:
                copyright_df.to_excel(writer, sheet_name='Copyright', index=False)
        files.append(xlsx)

    # GeoJSON & GeoPackage (sequential — GDAL is not thread-safe)
    if 'geojson' in formats:
        gjson = f"{base_name}.geojson"
        gdf.to_file(gjson, driver='GeoJSON')
        files.append(gjson)
    if 'gpkg' in formats:
        gpkg = f"{base_name}.gpkg"
        gdf.to_file(gpkg, driver='GPKG')
        files.append(gpkg)

    # Shapefile, zipped. Columns are renamed to the data dictionary's
    # <=10-char ShapefileFieldName values (DBF limit) so GDAL doesn't chop
    # names mid-word; text values longer than 254 chars are still truncated
    # by the format — the driver warns once per layer.
    if 'shp' in formats:
        shp_dir = Path(f"{base_name}-shp")
        if shp_dir.exists():
            shutil.rmtree(shp_dir)
        shp_dir.mkdir()
        gdf.rename(columns=shp_fields).to_file(shp_dir / f"{Path(base_name).name}.shp", driver='ESRI Shapefile')
        shp_zip = f"{base_name}-shp.zip"
        with zipfile.ZipFile(shp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for part in sorted(shp_dir.iterdir()):
                zf.write(part, part.name)
        shutil.rmtree(shp_dir)
        files.append(shp_zip)

    print(f"\n✓ Exported in {time.time() - t0:.1f}s: {', '.join([f.split('/')[-1] for f in files])}")
    return files


def process_single_dataset(ss, cfg, label, routes_path,
                           filter_status=None, filter_countries=None,
                           simplify_fuels=None):
    """Fetch, filter, and load geometries for one pipeline dataset."""
    routes_path = Path(routes_path)
    df, df_dict, df_copy = fetch_pipeline_data(ss, cfg)
    raw_ids = set(df['ProjectID'].dropna().astype(str).str.strip()) - {''}

    print(f"\nChecking {label} no-route conflicts...")
    check_no_route_geojson_files(df, routes_path / cfg['folder'])

    df = filter_by_status(df, filter_status)
    df = simplify_fuel_types(filter_by_countries(df, filter_countries), simplify_fuels)
    df = load_geometries(df, routes_path / cfg['folder'], label)

    return df, df_dict, df_copy, raw_ids


def build_release(pipeline_type, routes_path,
                  simplify_fuels=None, filter_status=None, filter_countries=None,
                  sheet_key=PIPELINES_SHEET_KEY,
                  creds_env='GDRIVE_API_CREDENTIALS'):
    """Full release build: Google Sheets auth → fetch/filter/geometry-join →
    Data-dictionary column selection.

    Returns a dict with:
      gdf_export   GeoDataFrame with the handoff column subset + geometry
      dict_export  data-dictionary rows for the exported columns
      acronyms     Acronyms worksheet
      copyright    Copyright worksheet (combined for Oil-and-Gas)
      config       get_config(pipeline_type)
      gdf_full     the pre-column-subset GeoDataFrame (for diagnostics)
      raw_db_ids   ProjectIDs in the raw sheet before filtering
    """
    t_total = time.time()

    gc = pygsheets.authorize(service_account_env_var=creds_env)
    ss = gc.open_by_key(sheet_key)
    config = get_config(pipeline_type)

    if pipeline_type == 'Oil-and-Gas':
        oil_cfg, gas_cfg = get_config('Oil-NGL'), get_config('Gas')

        oil_df, oil_dict, oil_copy, raw_oil_ids = process_single_dataset(
            ss, oil_cfg, 'Oil-NGL', routes_path,
            filter_status, filter_countries, simplify_fuels)
        gas_df, gas_dict, gas_copy, raw_gas_ids = process_single_dataset(
            ss, gas_cfg, 'Gas', routes_path,
            filter_status, filter_countries, simplify_fuels)

        raw_db_ids = raw_oil_ids | raw_gas_ids

        # Combine DataFrames
        oil_gdf = gpd.GeoDataFrame(oil_df, geometry='geometry', crs='EPSG:4326')
        gas_gdf = gpd.GeoDataFrame(gas_df, geometry='geometry', crs='EPSG:4326')
        common_cols = sorted(set(oil_gdf.columns) & set(gas_gdf.columns))
        pipes_gdf = pd.concat([oil_gdf[common_cols], gas_gdf[common_cols]], ignore_index=True)
        pipes_gdf = gpd.GeoDataFrame(pipes_gdf, geometry='geometry', crs='EPSG:4326')

        # Combine metadata
        common_fields = set(oil_dict['VariableName']) & set(gas_dict['VariableName'])
        pipes_dict = pd.concat([oil_dict, gas_dict[~gas_dict['VariableName'].isin(common_fields)]], ignore_index=True)
        pipes_copy = pd.DataFrame({'Copyright': ['=== GOIT ===', *oil_copy.iloc[:, 0].tolist(), '', '=== GGIT ===', *gas_copy.iloc[:, 0].tolist()]})
        pipes_acro = ss.worksheet('title', 'Acronyms').get_as_df(include_tailing_empty=False)

    else:
        # Single dataset mode
        pipes_df, pipes_dict, pipes_copy, raw_db_ids = process_single_dataset(
            ss, config, pipeline_type, routes_path,
            filter_status, filter_countries, simplify_fuels)
        pipes_gdf = gpd.GeoDataFrame(pipes_df, geometry='geometry', crs='EPSG:4326')
        pipes_acro = ss.worksheet('title', 'Acronyms').get_as_df(include_tailing_empty=False)

    # Select and order columns for export
    export_mask = (pipes_dict['IncludeWithDataRelease'] == 'Yes') & (pipes_dict['DataReleaseColumnOrder'].notna())
    export_cols = pipes_dict[export_mask].sort_values('DataReleaseColumnOrder')['VariableName'].tolist()
    export_cols = [c for c in export_cols if c in pipes_gdf.columns]

    dict_cols = [c for c in ['VariableName', 'ShapefileFieldName', 'Definition'] if c in pipes_dict.columns]
    pipes_dict_export = pipes_dict[pipes_dict['VariableName'].isin(export_cols)][dict_cols]
    pipes_gdf_export = pipes_gdf[export_cols + ['geometry']].copy()

    print(f"\n✓ Export ready: {len(pipes_gdf_export)} pipelines, {len(export_cols)} columns")
    print(f"  Total build time: {time.time() - t_total:.1f}s")

    return {
        'gdf_export': pipes_gdf_export,
        'dict_export': pipes_dict_export,
        'acronyms': pipes_acro,
        'copyright': pipes_copy,
        'config': config,
        'gdf_full': pipes_gdf,
        'raw_db_ids': raw_db_ids,
    }


def report_id_reconciliation(pipes_gdf, raw_db_ids, routes_path, pipeline_type):
    """Compare database ProjectIDs with the routes repo files.

    Print-only diagnostic — never fails the run.
    """
    def normalize_ids(series):
        return set(series.dropna().astype(str).str.strip()) - {''}

    routes_base = Path(routes_path)
    db_ids = normalize_ids(pipes_gdf['ProjectID'])

    # Collect repo ProjectIDs from the relevant folder(s)
    repo_ids = set()
    for folder in FOLDER_MAP[pipeline_type]:
        folder_path = routes_base / folder
        try:
            files = os.listdir(folder_path)
            folder_ids = {os.path.splitext(f)[0].strip() for f in files if f.endswith('.geojson')}
            print(f"{folder}: {len(folder_ids)} .geojson files (exists: {folder_path.exists()})")
        except Exception as e:
            folder_ids = set()
            print(f"{folder}: ERROR - {e}")
        repo_ids |= folder_ids

    # Compare
    in_db_not_repo = sorted(db_ids - repo_ids)
    in_repo_not_db = sorted(repo_ids - db_ids)
    in_repo_raw_db = sorted(pid for pid in in_repo_not_db if pid in raw_db_ids)
    in_repo_missing_raw = sorted(pid for pid in in_repo_not_db if pid not in raw_db_ids)

    print(f"\nDatabase (filtered): {len(db_ids)} | Raw sheet: {len(raw_db_ids)} | Repo: {len(repo_ids)} | In both: {len(db_ids & repo_ids)}")

    print()
    if in_db_not_repo:
        print(f"In DATABASE but NOT in repo ({len(in_db_not_repo)}):")
        for pid in in_db_not_repo:
            print(f"  {pid}")
    else:
        print("All database ProjectIDs have a .geojson in the repo.")

    print()
    if in_repo_not_db:
        print(f"In REPO but NOT in database ({len(in_repo_not_db)}):")
        for pid in in_repo_not_db:
            print(f"  {pid}")
        print()
        if in_repo_raw_db:
            print(f"  Present in raw Google Sheet before filtering ({len(in_repo_raw_db)}):")
            for pid in in_repo_raw_db:
                print(f"    {pid}")
        else:
            print("  None are present in the raw Google Sheet before filtering.")
        print()
        if in_repo_missing_raw:
            print(f"  Missing entirely from the raw Google Sheet ({len(in_repo_missing_raw)}):")
            for pid in in_repo_missing_raw:
                print(f"    {pid}")
        else:
            print("  None are missing entirely from the raw Google Sheet.")
    else:
        print("All repo .geojson files have a matching ProjectID in the database.")


def release_base_name(out_dir, config, pipeline_type,
                      filter_status=None, filter_countries=None, date=None):
    """Build the GEM-{tracker}-{type}-Pipelines[-{status}][-{countries}]-YYYY-MM
    output path (no extension)."""
    today = date or datetime.date.today()
    base_name = f"{out_dir}/GEM-{config['tracker']}-{pipeline_type}-Pipelines"

    # Add status suffix if filtering
    if filter_status:
        status_suffix = '-'.join([s.replace(' ', '') for s in filter_status])
        base_name += f"-{status_suffix}"

    # Add country suffix if filtering
    if filter_countries:
        country_suffix = '-'.join([c.replace(' ', '') for c in filter_countries])
        base_name += f"-{country_suffix}"

    # Date stamp: year-month only
    base_name += f"-{today:%Y-%m}"
    return base_name


# Columns not in the data release but appended to the map geojson when the
# sheet has them (copied from gdf_full; currently only the Gas sheet has
# RouteCreator — 'CB' marks AI-created routes, flagged in the map popup)
MAP_ONLY_COLUMNS = ['RouteCreator']


def derive_map_fields(gdf_export, gdf_full=None):
    """Adapt the handoff GeoDataFrame for the interim maps.

    The map file is deliberately the handoff file with THREE divergences:
      - rows without geometry are dropped (the handoff keeps 'no route'
        rows with null geometry via enforce_no_route_null_geometry; the
        web map can't draw them)
      - CountriesOrAreas becomes '; '-separated instead of ', ' — the map
        app's country filter (goit-ggit-interim-maps src/site.js) splits on
        semicolons
      - MAP_ONLY_COLUMNS present in the sheet (but excluded from the data
        release) are appended from gdf_full
    Columns are otherwise identical, so the map configs in
    goit-ggit-interim-maps read handoff column names directly.
    """
    gdf = gdf_export[gdf_export.geometry.notna()].copy()
    dropped = len(gdf_export) - len(gdf)
    if dropped:
        print(f"  Map output: dropped {dropped} null-geometry row(s)")
    if 'CountriesOrAreas' in gdf.columns:
        gdf['CountriesOrAreas'] = gdf['CountriesOrAreas'].str.replace(', ', '; ', regex=False)
    if gdf_full is not None:
        for col in MAP_ONLY_COLUMNS:
            if col in gdf_full.columns and col not in gdf.columns:
                gdf[col] = gdf_full.loc[gdf.index, col]
                print(f"  Map output: appended map-only column {col}")
    return gdf


def write_map_geojson(gdf_export, map_output, gdf_full=None):
    """Write the map geojson with publish guardrails.

    Raises if the output looks degraded (too few features / too small a
    file) so CI never overwrites the public map file with a broken build.
    """
    gdf = derive_map_fields(gdf_export, gdf_full=gdf_full)

    map_output = Path(map_output)
    map_output.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(map_output, driver='GeoJSON')

    n_features = len(gdf)
    n_bytes = map_output.stat().st_size
    if n_features < MIN_MAP_FEATURES:
        raise RuntimeError(f"map output guardrail: only {n_features} features "
                           f"(< {MIN_MAP_FEATURES}) — refusing to publish")
    if n_bytes < MIN_MAP_BYTES:
        raise RuntimeError(f"map output guardrail: file is {n_bytes/1e6:.1f} MB "
                           f"(< {MIN_MAP_BYTES/1e6:.0f} MB) — refusing to publish")
    if n_bytes > MAX_MAP_BYTES:
        raise RuntimeError(f"map output guardrail: file is {n_bytes/1e6:.1f} MB "
                           f"(> {MAX_MAP_BYTES/1e6:.0f} MB) — GitHub raw can't serve "
                           f"blobs over 100 MB; rethink map hosting before publishing")

    print(f"✓ Map geojson: {map_output} ({n_features} features, {n_bytes/1e6:.1f} MB)")
    return map_output


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Build GEM pipeline release data files and/or the interim-map geojson.')
    parser.add_argument('--pipeline-type', required=True,
                        choices=['Oil-NGL', 'Oil', 'NGL', 'Gas', 'Gas-Hydrogen', 'Hydrogen', 'Oil-and-Gas'])
    parser.add_argument('--simplify-fuels', default=None,
                        choices=['Oil', 'NGL', 'Oil-and-NGL', 'Gas'],
                        help='fuel simplification strategy (default: none)')
    parser.add_argument('--routes-path', default=DEFAULT_ROUTES_PATH,
                        help='path to the normalized routes data/individual-routes directory')
    parser.add_argument('--out-dir', default='data-files',
                        help='output directory for release files')
    parser.add_argument('--sheet-key', default=PIPELINES_SHEET_KEY)
    parser.add_argument('--status', nargs='+', default=None,
                        help='status filter, e.g. --status operating construction')
    parser.add_argument('--countries', nargs='+', default=None,
                        help='country filter, e.g. --countries Iran Iraq')
    parser.add_argument('--formats', nargs='+', default=list(ALL_FORMATS),
                        choices=list(ALL_FORMATS),
                        help='release formats to write (default: all)')
    parser.add_argument('--map-output', default=None,
                        help='also write the map geojson (handoff columns + map-only columns, null geometries dropped) to this path')
    parser.add_argument('--map-only', action='store_true',
                        help='skip the release exports; requires --map-output')
    parser.add_argument('--refresh-routes', action='store_true',
                        help='git pull --ff-only the routes checkout before building (local runs)')
    args = parser.parse_args(argv)

    if args.map_only and not args.map_output:
        parser.error('--map-only requires --map-output')

    if args.refresh_routes:
        refresh_routes(args.routes_path)

    release = build_release(
        pipeline_type=args.pipeline_type,
        routes_path=args.routes_path,
        simplify_fuels=args.simplify_fuels,
        filter_status=args.status,
        filter_countries=args.countries,
        sheet_key=args.sheet_key,
    )

    report_id_reconciliation(release['gdf_full'], release['raw_db_ids'],
                             args.routes_path, args.pipeline_type)

    if not args.map_only:
        Path(args.out_dir).mkdir(parents=True, exist_ok=True)
        base_name = release_base_name(args.out_dir, release['config'], args.pipeline_type,
                                      args.status, args.countries)
        export_files(release['gdf_export'], base_name,
                     release['dict_export'], release['acronyms'], release['copyright'],
                     formats=tuple(args.formats))

    if args.map_output:
        write_map_geojson(release['gdf_export'], args.map_output,
                          gdf_full=release['gdf_full'])

    return 0


if __name__ == '__main__':
    sys.exit(main())
