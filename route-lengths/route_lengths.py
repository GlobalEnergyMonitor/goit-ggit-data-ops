#!/usr/bin/env python3
"""Compute pipeline lengths and per-country splits from normalized route geometry.

This is the library-plus-CLI port of releases/estimate-length/estimate-length.ipynb.
It produces the two things the backend tracker sheet needs:

  * a length per pipeline           -> `Length estimates by pipeline`
  * a length and fraction per country per pipeline
                                    -> `Country ratios by pipeline`

Both used to be exported to .xlsx and pasted in by hand. The CLI defaults to
--dry-run and prints a reconciliation report; writing to the sheet is
sheet_writer.py's job and never happens implicitly.

Method
------
Lengths are geodetic, on the WGS84 ellipsoid via pyproj.Geod -- not planar, and
not reprojected per-country, so a pipeline's length does not depend on which UTM
zone it happens to fall in.

The country split intersects each route with the boundary layer built by
prepare_boundaries.py, then normalises each pipeline's per-country lengths by
that pipeline's *clipped* total rather than its full length. Fractions therefore
sum to exactly 1 even where a route crosses water the boundary layer does not
cover, or crosses a named joint area that overlaps a claimant's own polygon.
Neither discrepancy is silently redistributed: both are reported per pipeline,
as `unattributed_km` and `overlap_km` respectively.

Pipelines with no route file fall back to dividing their known length evenly
across the countries named in `CountriesOrAreas`, which is what the tracker
itself assumes when it has no geometry.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
from shapely.geometry import LineString

import sheets_client

HERE = Path(__file__).resolve().parent
DEFAULT_BOUNDARIES = HERE / 'boundaries-eez-land-union-v4-202410.gpkg'
BOUNDARIES_LAYER = 'countries'

DEFAULT_ROUTES = Path(
    '~/Dropbox/_git_ALL/_github-repos-gem/goit-ggit-pipeline-routes-normalized/'
    'data/individual-routes/'
).expanduser()

# Hydrogen routes live in the same tree but are not part of GOIT/GGIT lengths.
EXCLUDED_ROUTE_SUBFOLDERS = ('hydrogen-pipelines',)
ROUTE_GLOB = '*/?????.geojson'

# Tracker tabs and the row their header sits on. `Removed oil/NGL/gas pipelines`
# keeps a long preamble above its table, hence 708.
PIPELINE_TABS = [
    ('Gas pipelines', 3),
    ('Oil/NGL pipelines', 3),
]
REMOVED_TAB = ('Removed oil/NGL/gas pipelines', 708)

GEOD = pyproj.Geod(ellps='WGS84')


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def load_pipelines(sheet_key=None, backend=None, include_removed=False):
    """Read the pipeline tabs and concatenate gas + oil/NGL into one frame.

    The tracker writes '--' for 'not applicable'; it becomes NaN here so the
    numeric columns are actually numeric.
    """
    sheet_key = sheet_key or sheets_client.PIPELINES_SHEET_KEY
    backend = backend or sheets_client.get_backend()

    frames = []
    tabs = list(PIPELINE_TABS) + ([REMOVED_TAB] if include_removed else [])
    for tab, header_row in tabs:
        df = sheets_client.read_dataframe(
            sheet_key, tab, header_row=header_row, backend=backend)
        df['SourceTab'] = tab
        frames.append(df)
        print(f'  {tab:34s} {len(df):5d} rows')

    pipes = pd.concat(frames, axis=0, ignore_index=True)
    with pd.option_context('future.no_silent_downcasting', True):
        pipes = pipes.replace({'--': np.nan, '': np.nan}).infer_objects(copy=False)

    pipes['PipelineName'] = pipes['PipelineName'].astype('string')
    pipes = pipes[pipes['PipelineName'].notna() & (pipes['PipelineName'].str.strip() != '')]

    for col in ('LengthKnownKm', 'LengthEstimateKm', 'NumberOfCountries'):
        if col in pipes.columns:
            pipes[col] = pd.to_numeric(pipes[col], errors='coerce')

    # A pipeline can be listed in both the gas and the oil/NGL tab -- P2041 is
    # today's example. There is only ever one route file per ProjectID, so
    # measuring it twice would double the pipeline's country fractions. Keep the
    # first listing and say so rather than silently summing them.
    duplicated = pipes['ProjectID'].duplicated(keep=False)
    if duplicated.any():
        for pid, group in pipes[duplicated].groupby('ProjectID'):
            print(f'  ProjectID {pid} listed in {", ".join(group["SourceTab"])} '
                  f'-- keeping the first')
        pipes = pipes.drop_duplicates(subset='ProjectID', keep='first')

    return pipes.reset_index(drop=True)


def _load_route(filepath):
    """One route file -> one geometry, or None. Multi-part routes are dissolved.

    A file whose features all have `"geometry": null` is a placeholder for a
    pipeline the routes repo knows about but has no drawn route for. That is
    normal and expected -- roughly a sixth of the tree -- so it returns None
    quietly and the pipeline falls through to the known-length path.
    """
    try:
        geom = gpd.read_file(filepath).dissolve().geometry.iloc[0]
    except Exception as exc:                                  # noqa: BLE001
        return ('error', str(exc))
    if geom is None or geom.is_empty:
        return ('placeholder', None)
    return ('ok', geom)


def load_routes(routes_dir=DEFAULT_ROUTES, max_workers=8):
    """Read every per-pipeline route file into {ProjectID: geometry}.

    Files are named <ProjectID>.geojson, five characters, one folder per
    tracker. I/O-bound, so threads help and the GIL doesn't hurt.
    """
    routes_dir = Path(routes_dir)
    if not routes_dir.is_dir():
        raise SystemExit(f'routes directory not found: {routes_dir}')

    paths = [
        p for p in glob.glob(str(routes_dir / ROUTE_GLOB))
        if os.path.basename(os.path.dirname(p)) not in EXCLUDED_ROUTE_SUBFOLDERS
    ]
    print(f'  {len(paths)} route files under {routes_dir}')

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(_load_route, paths))

    routes, placeholders, errors = {}, 0, []
    for path, (kind, payload) in zip(paths, results):
        if kind == 'ok':
            routes[Path(path).stem] = payload
        elif kind == 'placeholder':
            placeholders += 1
        else:
            errors.append((os.path.basename(path), payload))

    print(f'  {len(routes)} with geometry, {placeholders} placeholders '
          f'(geometry: null), {len(errors)} unreadable')
    for name, message in errors:
        print(f'  failed to read {name}: {message}', file=sys.stderr)
    return routes


def load_boundaries(path=DEFAULT_BOUNDARIES):
    if not Path(path).exists():
        raise SystemExit(
            f'boundary layer not found: {path}\n'
            'Build it with:  python prepare_boundaries.py'
        )
    boundaries = gpd.read_file(path, layer=BOUNDARIES_LAYER)
    print(f'  {len(boundaries)} boundary polygons from {Path(path).name}')
    return boundaries


# ---------------------------------------------------------------------------
# lengths
# ---------------------------------------------------------------------------

def attach_routes(pipes, routes):
    """Join geometry onto the pipeline table and keep only measurable rows.

    A pipeline stays if it has geometry, or a known length we can divide across
    its listed countries. Everything else has nothing to contribute.
    """
    gdf = gpd.GeoDataFrame(
        pipes.copy(),
        geometry=[routes.get(str(pid).strip()) for pid in pipes['ProjectID']],
        crs='EPSG:4326',
    )
    has_route = gdf.geometry.notna()
    has_known = gdf['LengthKnownKm'].notna() if 'LengthKnownKm' in gdf.columns \
        else pd.Series(False, index=gdf.index)

    print(f'  {int(has_route.sum())} pipelines with route geometry, '
          f'{int((~has_route & has_known).sum())} with known length only, '
          f'{int((~has_route & ~has_known).sum())} dropped')

    gdf = gdf[has_route | has_known].copy()
    gdf['geometry'] = gdf.geometry.fillna(LineString())
    return gdf


def pipeline_lengths(gdf):
    """Geodetic length per pipeline, in km, for rows that have geometry."""
    with_route = gdf[~gdf.geometry.is_empty].copy()
    with_route['LengthEstimateKm'] = (
        with_route.geometry.apply(GEOD.geometry_length) / 1000.0)
    return with_route


def _split_named_countries(row):
    """Fallback split for a pipeline with no geometry.

    `CountriesOrAreas` is a comma-separated list; the known length is divided
    evenly across it. Crude, but it is the same assumption the tracker's own
    country counts already encode, and it keeps these pipelines from vanishing
    from the ratios tab entirely.
    """
    names = [n.strip() for n in str(row.get('CountriesOrAreas') or '').split(',')]
    names = [n for n in names if n]
    if not names:
        return []
    n = len(names)
    known = row.get('LengthKnownKm')
    per_country = (float(known) / n) if pd.notna(known) else np.nan
    return [
        {
            'PipelineName': row['PipelineName'],
            'SegmentName': row.get('SegmentName'),
            'ProjectID': row['ProjectID'],
            'Country': name,
            'length_per_country': per_country,
            'length_per_country_fract': 1.0 / n,
            'basis': 'named-countries',
        }
        for name in names
    ]


def country_split(gdf_with_routes, boundaries):
    """Intersect routes with country polygons and normalise per pipeline."""
    pipes_for_overlay = gdf_with_routes[
        ['PipelineName', 'SegmentName', 'ProjectID', 'geometry']
    ].copy()

    countries = boundaries[['gem_entity', 'geometry']].rename(
        columns={'gem_entity': 'Country'})

    intersected = gpd.overlay(
        pipes_for_overlay, countries, how='intersection', keep_geom_type=False)
    intersected['length_per_country'] = (
        intersected.geometry.apply(GEOD.geometry_length) / 1000.0)

    # One pipeline can hit several polygons of the same entity -- a country's
    # mainland and its island EEZ, say -- so collapse to one row per country.
    intersected = (
        intersected
        .groupby(['PipelineName', 'SegmentName', 'ProjectID', 'Country'], dropna=False,
                 as_index=False)['length_per_country']
        .sum()
    )

    clipped_total = intersected.groupby('ProjectID')['length_per_country'].transform('sum')
    intersected['length_per_country_fract'] = np.where(
        clipped_total > 0, intersected['length_per_country'] / clipped_total, np.nan)
    intersected['basis'] = 'geometry'
    return intersected


def coverage_report(gdf_with_routes, split):
    """Per pipeline, how the clipped total compares with the measured length.

    It can miss in both directions, and the two mean opposite things:

    unattributed_km  route length that fell outside every boundary polygon.
                     Usually a sliver of open water at a coastline; a large
                     value means a genuine hole in the boundary layer.

    overlap_km       route length counted more than once, because joint-regime
                     and overlapping-claim polygons deliberately overlap the
                     claimant countries' own polygons. This is expected under
                     --overlap-policy keep (the "never collapse a named joint
                     area" decision) and matches what the notebook already did.
                     It dilutes a claimant's share in the affected zone, since
                     fractions are normalised by the clipped total.

    Both are reported rather than netted, because a pipeline can have some of
    each and a single signed number would cancel them out.
    """
    clipped = split.groupby('ProjectID')['length_per_country'].sum()
    totals = gdf_with_routes.groupby('ProjectID')['LengthEstimateKm'].sum()
    report = pd.DataFrame({'LengthEstimateKm': totals, 'clipped_km': clipped})
    report['clipped_km'] = report['clipped_km'].fillna(0)
    difference = report['LengthEstimateKm'] - report['clipped_km']
    report['unattributed_km'] = difference.clip(lower=0)
    report['overlap_km'] = (-difference).clip(lower=0)
    return report.reset_index()


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------

def compute(routes_dir=DEFAULT_ROUTES, boundaries_path=DEFAULT_BOUNDARIES,
            sheet_key=None, backend=None, max_workers=8):
    """Run the whole calculation. Returns (by_pipeline, by_country, diagnostics)."""
    print('loading pipelines from the tracker sheet')
    pipes = load_pipelines(sheet_key=sheet_key, backend=backend)
    print('loading routes')
    routes = load_routes(routes_dir, max_workers=max_workers)
    print('loading boundaries')
    boundaries = load_boundaries(boundaries_path)

    print('measuring')
    gdf = attach_routes(pipes, routes)
    with_routes = pipeline_lengths(gdf)
    no_routes = gdf[gdf.geometry.is_empty]

    split = country_split(with_routes, boundaries)

    fallback_rows = [r for _, row in no_routes.iterrows()
                     for r in _split_named_countries(row)]
    fallback = pd.DataFrame(fallback_rows) if fallback_rows else pd.DataFrame(
        columns=split.columns)

    by_country = (
        pd.concat([split, fallback], ignore_index=True)
        .sort_values(['ProjectID', 'Country'])
        .reset_index(drop=True)
    )
    by_country = by_country.rename(
        columns={'length_per_country': 'LengthEstimateKmByCountry',
                 'length_per_country_fract': 'LengthPerCountryFraction'})

    by_pipeline = (
        with_routes[['ProjectID', 'LengthEstimateKm']]
        .dropna(subset=['ProjectID'])
        .reset_index(drop=True)
    )

    diagnostics = coverage_report(with_routes, split)
    return by_pipeline, by_country, diagnostics


def reconciliation_report(by_pipeline, by_country, diagnostics, tolerance_km=0.01):
    """Everything worth refusing to write over. Returns (lines, problems)."""
    lines, problems = [], []

    lines.append(f'pipelines with a computed length : {len(by_pipeline)}')
    lines.append(f'country rows                     : {len(by_country)}')
    lines.append(f'distinct countries               : {by_country["Country"].nunique()}')

    dupes = by_pipeline['ProjectID'].duplicated().sum()
    lines.append(f'duplicate ProjectIDs             : {dupes}')
    if dupes:
        problems.append(f'{dupes} ProjectIDs appear more than once in the length table')

    fractions = by_country.groupby('ProjectID')['LengthPerCountryFraction'].sum()
    off = fractions[(fractions - 1).abs() > 1e-6].dropna()
    lines.append(f'pipelines whose fractions != 1   : {len(off)}')
    if len(off):
        problems.append(f'{len(off)} pipelines have country fractions that do not sum to 1')
        for pid, total in off.head(10).items():
            lines.append(f'    {pid}  sum={total:.6f}')

    blank = by_country['Country'].isna() | (by_country['Country'].astype(str).str.strip() == '')
    lines.append(f'country rows with no country     : {int(blank.sum())}')
    if blank.any():
        problems.append(f'{int(blank.sum())} country rows have a blank Country')

    stray = diagnostics[diagnostics['unattributed_km'] > tolerance_km]
    lines.append(f'pipelines with length outside all boundaries (> {tolerance_km} km) '
                 f': {len(stray)}')
    for _, row in stray.sort_values('unattributed_km', ascending=False).head(10).iterrows():
        lines.append(f'    {row["ProjectID"]}  {row["unattributed_km"]:.2f} km '
                     f'unattributed of {row["LengthEstimateKm"]:.2f} km')

    overlapping = diagnostics[diagnostics['overlap_km'] > tolerance_km]
    lines.append(f'pipelines double-counted across overlapping claims (> {tolerance_km} km) '
                 f': {len(overlapping)}')
    lines.append('    (expected under --overlap-policy keep; these pipelines cross a '
                 'named joint area)')
    for _, row in overlapping.sort_values('overlap_km', ascending=False).head(10).iterrows():
        lines.append(f'    {row["ProjectID"]}  {row["overlap_km"]:.2f} km '
                     f'overlap of {row["LengthEstimateKm"]:.2f} km')

    negative = by_pipeline[by_pipeline['LengthEstimateKm'] <= 0]
    if len(negative):
        problems.append(f'{len(negative)} pipelines have a non-positive length')

    return lines, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--routes-dir', type=Path, default=DEFAULT_ROUTES)
    parser.add_argument('--boundaries', type=Path, default=DEFAULT_BOUNDARIES)
    parser.add_argument('--sheet-key', default=None)
    parser.add_argument('--out-dir', type=Path, default=None,
                        help='also write the two tables as CSVs here')
    parser.add_argument('--max-workers', type=int, default=8)
    parser.add_argument('--dry-run', dest='dry_run', action='store_true', default=True,
                        help='compute and report without touching the sheet (default)')
    parser.add_argument('--write', dest='dry_run', action='store_false',
                        help='write the results to the tracker sheet')
    parser.add_argument('--validate-write', action='store_true',
                        help='build the write plan and validate every request '
                             'against gws --dry-run, without sending any of it')
    parser.add_argument('--keep-note', action='store_true',
                        help="leave the length tab's A1 note stamp alone")
    parser.add_argument('--fill-formulas', choices=['all', 'new-rows'], default='all',
                        help="'all' (default) refills G:AH on every ratios data "
                             "row, repairing rows the manual paste left short; "
                             "'new-rows' only fills rows the write adds")
    args = parser.parse_args(argv)

    by_pipeline, by_country, diagnostics = compute(
        routes_dir=args.routes_dir, boundaries_path=args.boundaries,
        sheet_key=args.sheet_key, max_workers=args.max_workers)

    lines, problems = reconciliation_report(by_pipeline, by_country, diagnostics)
    print('\n--- reconciliation ---')
    for line in lines:
        print(line)

    if args.out_dir:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        by_pipeline.to_csv(args.out_dir / 'length-estimates-by-pipeline.csv', index=False)
        by_country.to_csv(args.out_dir / 'country-ratios-by-pipeline.csv', index=False)
        diagnostics.to_csv(args.out_dir / 'length-diagnostics.csv', index=False)
        print(f'\nwrote CSVs to {args.out_dir}')

    if problems:
        print('\nPROBLEMS:', file=sys.stderr)
        for problem in problems:
            print(f'  {problem}', file=sys.stderr)

    import sheet_writer

    writer_kwargs = dict(sheet_key=args.sheet_key,
                         update_note=not args.keep_note,
                         fill_formulas=args.fill_formulas)

    if args.dry_run or args.validate_write:
        plan_dict = sheet_writer.plan(by_pipeline, by_country, **writer_kwargs)
        print('\n--- write plan ---')
        print(sheet_writer.describe(plan_dict))
        if args.validate_write:
            backend = sheets_client.get_backend(require_write=True)
            sheet_writer.write_all(by_pipeline, by_country, backend=backend,
                                   plan_dict=plan_dict, dry_run=True,
                                   **writer_kwargs)
            print('\nevery request validated by gws --dry-run; nothing was sent.')
        else:
            print('\ndry run -- nothing written to the sheet. Pass --write to write.')
        return 1 if problems else 0

    if problems:
        raise SystemExit('refusing to write: the reconciliation report found problems')

    plan_dict = sheet_writer.write_all(by_pipeline, by_country, **writer_kwargs)
    print('\n--- written ---')
    print(sheet_writer.describe(plan_dict))
    remaining = sheet_writer.verify(plan_dict)
    if remaining:
        print('\nVERIFY FAILED:', file=sys.stderr)
        for problem in remaining:
            print(f'  {problem}', file=sys.stderr)
        return 1
    print('\nverified: row extents, banding and the formula block all line up.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
