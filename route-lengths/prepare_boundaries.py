#!/usr/bin/env python3
"""Build the country-boundary layer that route_lengths.py overlays routes against.

Run occasionally (when a new EEZ or Natural Earth release lands, or when the
`Country dictionary` tab changes) -- not on every route update. The .gpkg it
produces is uploaded to the "Automation inputs" folder on the work Drive and
fetched from there by CI.

What this replaces
------------------
The notebook read the EEZ shapefile directly, then hand-carved Hong Kong and
Macao out of China with two hardcoded Natural Earth lookups, and hand-patched
three country names at the very end (Alaska->United States, Senkaku
Islands->Japan, and Canary Islands->Morocco but only on Nigeria-Morocco
pipelines). All of that is gone. Attribution is now derived from data:

  * every EEZ polygon resolves to a GEM entity by four ordered rules
  * the carve-out is generic -- any GEM entity that has no EEZ polygon of its
    own but does have Natural Earth geometry is cut out of its parent
  * region comes from geography (nearest neighbour), not from sovereignty,
    which is what made the Canary Islands special-case necessary in the first
    place

Outputs (all beside this file unless --out-dir says otherwise):

  boundaries-eez-land-union-v4-202410.gpkg   the layer itself
  boundaries.json                            source versions, SHA-256s, counts
  boundaries-attribution.csv                 every polygon, its GEM entity, and
                                             which rule resolved it

Usage
-----
    python prepare_boundaries.py                      # build everything
    python prepare_boundaries.py --emit-dictionary-diff  # step 2.5 preview only

--emit-dictionary-diff writes nothing to any Google Sheet. It prints the
proposed `Country dictionary` change set for review; applying it is a separate,
explicitly approved action.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

import sheets_client

HERE = Path(__file__).resolve().parent

DEFAULT_EEZ = Path(
    '~/Dropbox/_gis-data/eez/EEZ_land_union_v4_202410/EEZ_land_union_v4_202410.shp'
).expanduser()
DEFAULT_NE = Path(
    '~/Dropbox/_gis-data/_natural_earth_data/ne_10m_admin_0_countries_v5.1.2/'
    'ne_10m_admin_0_countries.shp'
).expanduser()

GPKG_NAME = 'boundaries-eez-land-union-v4-202410.gpkg'
GPKG_LAYER = 'countries'

# Source provenance. Both are the newest releases as of 2026-07-31: Marine
# Regions has not published a union newer than v4 (202410, built on World EEZ
# v12 / 20231025), and Natural Earth's last tag is v5.1.2 (2022-05-13).
SOURCES = {
    'eez_land_union': {
        'name': 'Marine Regions EEZ Land Union',
        'version': 'v4_202410',
        'released': '2024-10',
        'doi': 'https://doi.org/10.14284/698',
        'url': 'https://www.marineregions.org/downloads.php',
        'built_on': 'World EEZ v12 (20231025)',
        'note': 'Requires accepting the Marine Regions licence; not auto-downloadable.',
    },
    'natural_earth': {
        'name': 'Natural Earth 10m Admin 0 Countries',
        'version': 'v5.1.2',
        'released': '2022-05-13',
        'url': 'https://github.com/nvkelso/natural-earth-vector/tree/v5.1.2',
        'note': 'Used only to carve out entities that have no EEZ polygon of their own.',
    },
}

# POL_TYPE values that represent a single country's own space. Everything else
# is a joint regime, an overlapping claim, or a conflict zone.
SINGLE_COUNTRY_POL_TYPES = ('Union EEZ and country', 'Landlocked country')

# Degrees, roughly 1 km. Used only to speed up nearest-neighbour ranking, never
# for anything that reaches the output geometry or a length.
NEAREST_SIMPLIFY_TOLERANCE = 0.01

# GEM entities with no EEZ polygon of their own. Each is cut out of its parent's
# geometry using Natural Earth. Discovered by audit, not assumed: of 251 GEM
# entities, 245 already have their own EEZ polygon and these are the remainder.
# Joint Petroleum Development Area is listed for completeness -- it has no
# geometry in any source, correctly, since the Timor Sea JPDA lapsed in 2019.
CARVE_OUTS = [
    {'gem_name': 'Hong Kong',        'alpha3': 'HKG', 'parent': 'China'},
    {'gem_name': 'Macao',            'alpha3': 'MAC', 'parent': 'China'},
    {'gem_name': 'Aland Islands',    'alpha3': 'ALA', 'parent': 'Finland'},
    {'gem_name': 'British Indian Ocean Territory',
                                     'alpha3': 'IOT', 'parent': 'United Kingdom'},
    {'gem_name': 'Kosovo',           'alpha3': 'XXK', 'parent': 'Serbia'},
]

# Natural Earth does not use ISO alpha-3 consistently. ADM0_A3 is tried first,
# then ISO_A3_EH, then ISO_A3; these two need an explicit code because none of
# the three columns holds the GEM code.
NE_CODE_ALIASES = {
    'XXK': 'KOS',   # Kosovo: ADM0_A3=KOS, ISO_A3=-99 (no assigned ISO code)
    'ALA': 'ALD',   # Aland: ADM0_A3=ALD, but ISO_A3=ALA
}

NO_GEOMETRY_ANYWHERE = {
    'WQJ': 'Joint Petroleum Development Area -- lapsed 2019, no polygon in any source',
}

# ---------------------------------------------------------------------------
# Step 2.5: the proposed `Country dictionary` change set.
#
# These constants describe edits to the *sheet*, not to the boundary layer, and
# nothing here is applied automatically. --emit-dictionary-diff renders them for
# review. They live in this file because the same EEZ read that builds the
# boundary layer is what determines them.
# ---------------------------------------------------------------------------

# 7 dictionary rows whose EEZNamesIfDifferent alias points at an EEZ v2/v3 name
# that v4 renamed. Because the alias misses, rule (b) fires instead and silently
# credits the whole polygon to the first ISO party -- e.g. the Senkaku Islands
# were being attributed to Taiwan. Only column I changes; column A is untouched,
# so no live `Country ratios` row is orphaned.
ALIAS_FIXES = {
    'Conflict zone (China, Japan, Taiwan)':
        'Senkaku Islands',
    'Conflict zone (Japan, Russia)':
        'Kuril Islands',
    'Conflict zone (Japan, South Korea)':
        'Overlapping claim Liancourt Rocks: Japan / South Korea',
    'Joint regime area (Colombia, Jamaica)':
        'Joint regime area: Jamaica / Colombia',
    'Joint regime area (Japan, Korea)':
        'Joint regime area: South Korea / Japan',
    'Joint regime area (Nigeria, Sao Tome and Principe)':
        'Joint regime area: Sao Tome and Principe / Nigeria',
    'Protected zone (Australia, Papua New Guinea)':
        'Joint regime area Torres Strait Treaty: Papua New Guinea / Australia',
}

# 9 dictionary rows with no corresponding v4 polygon and no live rows in
# `Country ratios by pipeline`. They cannot be produced by any run, now or ever.
DEAD_ROWS = [
    'Area of overlap Australia/Indonesia',
    'Disputed (Barbados, Trinidad and Tobago)',
    'Disputed (Kenya, Somalia)',
    'Disputed (Peru)',
    'Disputed (Western Sahara/Mauritania)',
    'Joint development area (Australia/East Timor)',
    'Joint regime area (Peru, Ecuador)',
    'Joint regime area (Senegal/Guinea Bissau)',
    'Kuwait-Saudi Arabia',
    # The Timor Sea JPDA was dissolved by the 2018 Australia--Timor-Leste
    # treaty; v4 carries only `Australia` and `East Timor`, and this row has no
    # alias, so nothing can ever resolve to it. Listed last because "JPDA kind
    # of things" were called out as deliberate differences from GEM's
    # dictionary -- this is the one deletion most worth a second look, even
    # though the row is unreachable either way.
    'Joint Petroleum Development Area',
]

# Rows whose Region/SubRegion is simply wrong in the sheet today. Abu Musa and
# the Greater/Lesser Tunbs are islands in the Persian Gulf, but the row reads
# Europe / Southern Europe -- and unlike everything else in this change set it
# has a live `Country ratios` row, so it is a correction with visible effect
# rather than housekeeping.
REGION_FIXES = {
    'Disputed (Iran, United Arab Emirates)': ('Asia', 'Western Asia'),
}

# Spain's North African territories. Geographically Africa, same as the Canary
# Islands -- named here only so they get Northern Africa rather than whatever
# the nearest-neighbour rule lands on, since several are tiny rocks closer to
# a Spanish EEZ centroid than to Morocco's.
SPANISH_NORTH_AFRICA = [
    'Ceuta',
    'Melilla',
    'Alhucemas Islands',
    'Chafarinas Islands',
    'Perejil Island',
    'Peñón de Vélez de la Gomera',
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def shapefile_sha256s(shp_path):
    """Hash every sidecar too -- a .shp alone doesn't pin the attributes."""
    shp_path = Path(shp_path)
    out = {}
    for ext in ('.shp', '.shx', '.dbf', '.prj', '.cpg'):
        sidecar = shp_path.with_suffix(ext)
        if sidecar.exists():
            out[sidecar.name] = sha256(sidecar)
    return out


def norm(value):
    return str(value or '').strip()


def find_header_row(sheet_key, tab, marker, backend=None, search_rows=5):
    """Locate the header row by looking for a known column name.

    These tabs have gained and lost banner rows above the header more than once
    (the `Country dictionary` banner was removed 2026-08-02, which silently
    shifted its header from row 2 to row 1). Hardcoding the row number means the
    next such edit reads the first data row as the header, so derive it.
    """
    values = sheets_client.read_range(
        sheet_key, f"'{tab}'!A1:Z{search_rows}", backend=backend)
    for offset, row in enumerate(values):
        if any(norm(cell) == marker for cell in row):
            return offset + 1
    raise SystemExit(
        f'{tab!r}: no header row in the first {search_rows} rows '
        f'(looked for a cell reading {marker!r})'
    )


def load_dictionaries(sheet_key=None, backend=None):
    """Read the two dictionary tabs.

    `Country dictionary` is GEM-pipelines-specific: it carries Region,
    SubRegion, PipelineBubbleRegion and the EEZNamesIfDifferent aliases.
    `Country dictionary (imported for ref.)` is a mirror of GEM's org-wide
    naming sheet and is the authority for alpha-3 codes and `Territory of`.
    """
    sheet_key = sheet_key or sheets_client.PIPELINES_SHEET_KEY
    country_dict = sheets_client.read_dataframe(
        sheet_key, 'Country dictionary', backend=backend,
        header_row=find_header_row(sheet_key, 'Country dictionary',
                                   'Country', backend=backend))
    imported_tab = 'Country dictionary (imported for ref.)'
    imported = sheets_client.read_dataframe(
        sheet_key, imported_tab, backend=backend,
        header_row=find_header_row(sheet_key, imported_tab,
                                   'GEM Standard Country Name', backend=backend))

    country_dict['Country'] = country_dict['Country'].map(norm)
    country_dict = country_dict[country_dict['Country'] != ''].copy()

    # The imported tab's headers are long prose; address it positionally, which
    # is stable, rather than by header text, which is not.
    imported.columns = ['ISOName', 'GEMName', 'SameAsISO', 'Numeric', 'Alpha2',
                        'Alpha3', 'Territory', 'TerritoryOf', 'Longitude',
                        'InPlantData'][:imported.shape[1]]
    for col in ('GEMName', 'Alpha3', 'TerritoryOf'):
        imported[col] = imported[col].map(norm)
    imported = imported[imported['GEMName'] != ''].copy()

    return country_dict, imported


def build_lookups(country_dict, imported):
    dict_names = set(country_dict['Country'])
    aliases = {
        norm(row.get('EEZNamesIfDifferent')): row['Country']
        for _, row in country_dict.iterrows()
        if norm(row.get('EEZNamesIfDifferent'))
    }
    alpha3_to_gem = {
        row['Alpha3'].upper(): row['GEMName']
        for _, row in imported.iterrows()
        if row['Alpha3']
    }
    regions = {
        row['Country']: (norm(row.get('Region')),
                         norm(row.get('SubRegion')),
                         norm(row.get('PipelineBubbleRegion')))
        for _, row in country_dict.iterrows()
    }
    territory_of = {
        row['GEMName']: row['TerritoryOf']
        for _, row in imported.iterrows()
    }
    return dict_names, aliases, alpha3_to_gem, regions, territory_of


def resolve_entity(union, iso_ter1, iso_sov1, dict_names, aliases, alpha3_to_gem):
    """Four ordered rules, most specific first. Returns (gem_entity, rule)."""
    union = norm(union)
    if union in dict_names:
        return union, 'a-dictionary-name'
    if union in aliases:
        return aliases[union], 'a-dictionary-alias'
    ter = norm(iso_ter1).upper()
    if ter in alpha3_to_gem:
        return alpha3_to_gem[ter], 'b-iso-ter1'
    sov = norm(iso_sov1).upper()
    if sov in alpha3_to_gem:
        return alpha3_to_gem[sov], 'c-iso-sov1'
    return '', 'd-unresolved'


def build_anchors(frame, regions):
    """The polygons that define where each GEM region physically is.

    Only a country's own primary space qualifies -- single-country POL_TYPEs
    resolved to an entity that carries a Region in the dictionary. Joint and
    overlapping polygons are deliberately excluded: they are the things being
    located, not landmarks to locate against.
    """
    anchors = frame[
        frame['POL_TYPE'].isin(SINGLE_COUNTRY_POL_TYPES)
        & frame['gem_entity'].map(lambda e: bool(regions.get(e, ('',))[0]))
    ]
    return gpd.GeoDataFrame(
        {'gem': anchors['gem_entity'].tolist()},
        geometry=anchors.geometry.tolist(),
        crs=frame.crs,
    )


def nearest_entities(frame, anchors, tolerance=NEAREST_SIMPLIFY_TOLERANCE):
    """Nearest anchor for each row, by polygon-to-polygon distance.

    True geometry distance, not a centroid approximation -- which matters for
    enclaves like Ceuta, whose centroid sits nearer a Spanish EEZ centroid than
    Morocco's while the polygon itself is embedded in Morocco.

    Geometries are simplified first. EEZ polygons carry enough vertices that
    exact distance over the full set runs for many minutes, and the answer here
    is only ever used to rank neighbours -- a ~1 km tolerance cannot change
    which country is closest. Call this with the smallest frame that needs it.
    """
    if frame.empty or anchors.empty:
        return {}
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        targets = frame[['geometry']].copy()
        targets['geometry'] = targets.geometry.simplify(tolerance)
        simplified = anchors.copy()
        simplified['geometry'] = simplified.geometry.simplify(tolerance)
        joined = gpd.sjoin_nearest(targets, simplified, how='left')
    joined = joined[~joined.index.duplicated(keep='first')]   # ties -> first
    return joined['gem'].to_dict()


def region_for(union, gem_entity, iso_ter1, nearest, regions, alpha3_to_gem):
    """Resolve one polygon's Region/SubRegion. Returns (region3, rule).

    Order matters, and it is the opposite of the old notebook's instinct:

      1. Spain's North African territories are Africa by explicit decision.
      2. An entity with its own dictionary row uses that row -- the kilometres
         are credited to that entity, so the sheet will look up that same row.
      3. Multi-party polygons inherit from ISO_TER1. They are often mid-ocean,
         where the nearest landmass belongs to neither party.
      4. Everything else takes the region of the physically nearest country.

    Rule 4 is why the Canary Islands need no special case any more: geography,
    not sovereignty, decides. It also matches GEM's own treatment of Reunion
    and Mayotte (Africa) and New Caledonia and French Polynesia (Oceania),
    every one of which sovereignty-inheritance gets wrong.
    """
    if union in SPANISH_NORTH_AFRICA:
        return ('Africa', 'Northern Africa', 'Africa'), 'spanish-north-africa'

    own = regions.get(gem_entity)
    if own and own[0]:
        return own, 'own-dictionary-row'

    if ' / ' in union:
        parent = alpha3_to_gem.get(norm(iso_ter1).upper(), '')
        return regions.get(parent, ('', '', '')), f'multi-party-inherits-{parent or "none"}'

    if nearest:
        return regions.get(nearest, ('', '', '')), f'nearest-{nearest}'
    return ('', '', ''), 'unassigned'


def assign_regions(frame, regions, alpha3_to_gem):
    """Two passes, so the expensive rule runs on as few polygons as possible.

    Pass one resolves everything the cheap rules can reach and marks the rest
    'unassigned'. Pass two computes nearest neighbours for only those.
    """
    def resolve(idx, row, nearest):
        return region_for(norm(row['UNION']), row['gem_entity'], row.get('ISO_TER1'),
                          nearest, regions, alpha3_to_gem)

    out = {}
    pending = []
    for idx, row in frame.iterrows():
        region, rule = resolve(idx, row, None)
        if rule == 'unassigned':
            pending.append(idx)
        else:
            out[idx] = tuple(region) + (rule,)

    if pending:
        nearest = nearest_entities(frame.loc[pending], build_anchors(frame, regions))
        for idx in pending:
            region, rule = resolve(idx, frame.loc[idx], nearest.get(idx))
            out[idx] = tuple(region) + (rule,)

    return out


def carve_out_entities(eez, natural_earth, alpha3_to_gem, territory_of):
    """Give territories without their own EEZ polygon geometry of their own.

    Generalises the notebook's two hardcoded Hong Kong / Macao lines: each
    carve-out becomes a new row whose geometry is subtracted from its parent's,
    so the layer stays a partition and no kilometre is double-counted.
    """
    by_name = {norm(u): idx for idx, u in eez['UNION'].items()}
    new_rows, adjusted, missing = [], [], []

    for spec in CARVE_OUTS:
        parent_idx = by_name.get(spec['parent'])
        if parent_idx is None:
            missing.append(f"{spec['gem_name']}: parent {spec['parent']!r} not in EEZ layer")
            continue

        code = NE_CODE_ALIASES.get(spec['alpha3'], spec['alpha3'])
        match = None
        for column in ('ADM0_A3', 'ISO_A3_EH', 'ISO_A3'):
            if column not in natural_earth.columns:
                continue
            hit = natural_earth[natural_earth[column].map(norm).str.upper() == code]
            if len(hit):
                match = hit
                break
        if match is None:
            missing.append(f"{spec['gem_name']}: no Natural Earth geometry for {code}")
            continue

        geom = match.geometry.union_all() if hasattr(match.geometry, 'union_all') \
            else match.geometry.unary_union

        parent_geom = eez.at[parent_idx, 'geometry']
        eez.at[parent_idx, 'geometry'] = parent_geom.difference(geom)
        adjusted.append((spec['parent'], spec['gem_name']))

        new_rows.append({
            'UNION': spec['gem_name'],
            'POL_TYPE': 'Union EEZ and country',
            'ISO_TER1': spec['alpha3'],
            'ISO_SOV1': next(
                (a3 for a3, name in alpha3_to_gem.items()
                 if name == territory_of.get(spec['gem_name'], spec['parent'])),
                '',
            ),
            'geometry': geom,
            'gem_entity': spec['gem_name'],
            'resolution_rule': 'carve-out-natural-earth',
        })

    return new_rows, adjusted, missing


# ---------------------------------------------------------------------------
# main build
# ---------------------------------------------------------------------------

def build(eez_path, ne_path, out_dir, overlap_policy='keep', sheet_key=None):
    print(f'reading EEZ         {eez_path}')
    eez = gpd.read_file(eez_path)
    print(f'reading NaturalEarth {ne_path}')
    natural_earth = gpd.read_file(ne_path)
    print(f'reading dictionaries from {sheet_key or sheets_client.PIPELINES_SHEET_KEY}')
    country_dict, imported = load_dictionaries(sheet_key)
    dict_names, aliases, alpha3_to_gem, regions, territory_of = build_lookups(
        country_dict, imported)
    print(f'  {len(eez)} EEZ polygons, {len(natural_earth)} NE polygons, '
          f'{len(dict_names)} dictionary rows, {len(alpha3_to_gem)} GEM entities')

    resolved = {}
    for idx, row in eez.iterrows():
        resolved[idx] = resolve_entity(
            row['UNION'], row.get('ISO_TER1'), row.get('ISO_SOV1'),
            dict_names, aliases, alpha3_to_gem)

    counts = pd.Series([rule for _, rule in resolved.values()]).value_counts()
    print('\nresolution:')
    for rule, n in counts.items():
        print(f'  {rule:24s} {n:4d}')

    unresolved = [norm(eez.at[idx, 'UNION'])
                  for idx, (_, rule) in resolved.items() if rule == 'd-unresolved']
    if unresolved:
        print('\nUNRESOLVED polygons -- every one of these would silently drop '
              'kilometres on the floor:', file=sys.stderr)
        for name in unresolved:
            print(f'  {name}', file=sys.stderr)
        raise SystemExit(
            f'{len(unresolved)} of {len(eez)} EEZ polygons could not be mapped to a '
            'GEM entity. Add them to the Country dictionary (or an alias) and re-run.'
        )

    eez = eez.copy()
    eez['gem_entity'] = [resolved[idx][0] for idx in eez.index]
    eez['resolution_rule'] = [resolved[idx][1] for idx in eez.index]

    # Carve-outs first: they add rows and shrink their parents, and the region
    # pass has to see the finished set of polygons.
    new_rows, adjusted, missing = carve_out_entities(
        eez, natural_earth, alpha3_to_gem, territory_of)
    print(f'\ncarve-outs: {len(new_rows)} added')
    for parent, child in adjusted:
        print(f'  {child} subtracted from {parent}')
    for note in missing:
        print(f'  SKIPPED {note}', file=sys.stderr)
    for code, why in NO_GEOMETRY_ANYWHERE.items():
        print(f'  (no geometry by design) {code}: {why}')

    if new_rows:
        crs = eez.crs
        eez = gpd.GeoDataFrame(
            pd.concat([eez, gpd.GeoDataFrame(new_rows, geometry='geometry', crs=crs)],
                      ignore_index=True),
            geometry='geometry', crs=crs)

    region_map = assign_regions(eez, regions, alpha3_to_gem)
    eez['Region'] = [region_map[idx][0] for idx in eez.index]
    eez['SubRegion'] = [region_map[idx][1] for idx in eez.index]
    eez['PipelineBubbleRegion'] = [region_map[idx][2] for idx in eez.index]
    eez['region_rule'] = [region_map[idx][3] for idx in eez.index]

    unassigned = eez[eez['Region'] == '']
    if len(unassigned):
        print(f'\n{len(unassigned)} polygons have no Region:', file=sys.stderr)
        for _, row in unassigned.iterrows():
            print(f'  {row["UNION"]} ({row["region_rule"]})', file=sys.stderr)

    if overlap_policy == 'drop':
        before = len(eez)
        eez = eez[eez['POL_TYPE'].isin(SINGLE_COUNTRY_POL_TYPES)].copy()
        print(f'\noverlap-policy=drop: {before - len(eez)} joint/overlapping '
              'polygons removed')

    keep = ['UNION', 'POL_TYPE', 'ISO_TER1', 'ISO_SOV1', 'gem_entity',
            'resolution_rule', 'Region', 'SubRegion', 'PipelineBubbleRegion',
            'region_rule', 'geometry']
    keep = [c for c in keep if c in eez.columns]
    eez = eez[keep]

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    gpkg_path = out_dir / GPKG_NAME
    if gpkg_path.exists():
        gpkg_path.unlink()   # GPKG append semantics would stack layers otherwise
    eez.to_file(gpkg_path, layer=GPKG_LAYER, driver='GPKG')
    print(f'\nwrote {gpkg_path}  ({len(eez)} polygons)')

    attribution = pd.DataFrame(eez.drop(columns='geometry'))
    attribution_path = out_dir / 'boundaries-attribution.csv'
    attribution.sort_values('UNION').to_csv(attribution_path, index=False)
    print(f'wrote {attribution_path}')

    manifest = {
        'layer': GPKG_LAYER,
        'gpkg': GPKG_NAME,
        'gpkg_sha256': sha256(gpkg_path),
        'polygon_count': int(len(eez)),
        'overlap_policy': overlap_policy,
        'built_by': 'route-lengths/prepare_boundaries.py',
        'sources': {
            'eez_land_union': dict(SOURCES['eez_land_union'],
                                   path=str(eez_path),
                                   sha256=shapefile_sha256s(eez_path)),
            'natural_earth': dict(SOURCES['natural_earth'],
                                  path=str(ne_path),
                                  sha256=shapefile_sha256s(ne_path)),
            'country_dictionary': {
                'spreadsheet': sheet_key or sheets_client.PIPELINES_SHEET_KEY,
                'tabs': ['Country dictionary',
                         'Country dictionary (imported for ref.)'],
                'row_count': int(len(country_dict)),
            },
        },
        'resolution_counts': {rule: int(n) for rule, n in counts.items()},
        'carve_outs': [row['UNION'] for row in new_rows],
        'no_geometry_anywhere': NO_GEOMETRY_ANYWHERE,
    }
    manifest_path = out_dir / 'boundaries.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    print(f'wrote {manifest_path}')
    return eez


# ---------------------------------------------------------------------------
# step 2.5 -- dictionary diff preview (prints only, never writes)
# ---------------------------------------------------------------------------

def compute_dictionary_changes(eez_path, sheet_key=None):
    """Work out the step-2.5 change set. Reads sheets; writes nothing.

    Returns a dict consumed by both emit_dictionary_diff (which prints it) and
    sheet_writer.plan_dictionary (which turns it into API requests).
    """
    eez = gpd.read_file(eez_path)
    country_dict, imported = load_dictionaries(sheet_key)
    dict_names, aliases, alpha3_to_gem, regions, territory_of = build_lookups(
        country_dict, imported)
    gem_names = set(alpha3_to_gem.values())

    # The proposed rows must be scored by the same geographic rule the built
    # layer uses, or the preview would recommend exactly the sovereignty
    # inheritance the Canary Islands decision threw out.
    eez = eez.copy()
    eez['gem_entity'] = [
        resolve_entity(row['UNION'], row.get('ISO_TER1'), row.get('ISO_SOV1'),
                       dict_names, aliases, alpha3_to_gem)[0]
        for _, row in eez.iterrows()
    ]
    # Aliases already fixed count as covered, so a polygon isn't proposed twice.
    covered = dict_names | set(aliases) | set(ALIAS_FIXES.values())
    multi_party_types = [t for t in eez['POL_TYPE'].unique()
                         if t not in SINGLE_COUNTRY_POL_TYPES]

    candidates = [
        idx for idx, row in eez[eez['POL_TYPE'].isin(multi_party_types)].iterrows()
        if norm(row['UNION']) not in covered and norm(row['UNION']) not in gem_names
    ]
    nearest = nearest_entities(eez.loc[candidates], build_anchors(eez, regions))

    additions = []
    for idx in candidates:
        row = eez.loc[idx]
        union = norm(row['UNION'])
        # Scored as an entity in its own right -- passing '' for the entity
        # stops the sovereign's dictionary row from pre-empting the geography.
        region, basis = region_for(union, '', row.get('ISO_TER1'),
                                   nearest.get(idx), regions, alpha3_to_gem)
        additions.append({
            'Country': union,
            'Region': region[0],
            'SubRegion': region[1],
            'PipelineBubbleRegion': region[2],
            'POL_TYPE': row['POL_TYPE'],
            'basis': basis,
        })
    # Empty once the change set has been applied -- the normal steady state, not
    # an error, so give the frame its columns explicitly rather than letting an
    # empty list produce a column-less frame.
    addition_columns = ['Country', 'Region', 'SubRegion', 'PipelineBubbleRegion',
                        'POL_TYPE', 'basis']
    additions = pd.DataFrame(additions, columns=addition_columns)
    additions = additions.sort_values('Country')

    canary = country_dict[country_dict['Country'] == 'Canary Islands']
    canary_row = None
    if len(canary):
        row = canary.iloc[0]
        canary_row = {
            'Country': 'Canary Islands',
            'alpha3_current': norm(row.get('CountryISO3166-1alpha-3')),
            'alpha3_new': '',
            'Region': norm(row.get('Region')),
            'SubRegion': norm(row.get('SubRegion')),
            'notes_current': norm(row.get('Notes')),
            'notes_new': ('geographically Africa; region is assigned by geography, '
                          'not sovereignty (see route-lengths/)'),
        }
        if (canary_row['alpha3_current'] == canary_row['alpha3_new']
                and canary_row['notes_current'] == canary_row['notes_new']):
            canary_row = None                       # already applied

    # Only a column-A change can orphan a live `Country ratios` row, and the only
    # column-A changes here are the deletions -- the alias fixes touch column I.
    # So the sequencing constraint is exactly: does anything being deleted still
    # appear in the live tab? Re-derived every run rather than assumed.
    live = collections.Counter(
        norm(row[0]) for row in sheets_client.read_range(
            sheet_key or sheets_client.PIPELINES_SHEET_KEY,
            "'Country ratios by pipeline'!D2:D") if row
    )

    # Every section below reports what is still *pending*, not what the constants
    # describe -- so a second run after a successful write shows an empty change
    # set instead of re-proposing work the sheet already has. The constants stay
    # the declaration of intent; the live sheet decides what is left to do.
    current_alias = {
        row['Country']: norm(row.get('EEZNamesIfDifferent'))
        for _, row in country_dict.iterrows()
    }

    def _region_of(name, column):
        return norm(country_dict.loc[country_dict['Country'] == name,
                                     column].iloc[0])

    return {
        'alias_fixes': {name: alias for name, alias in ALIAS_FIXES.items()
                        if current_alias.get(name) != alias},
        'region_fixes': {
            name: {'to': target,
                   'from': (_region_of(name, 'Region'),
                            _region_of(name, 'SubRegion')),
                   'live_rows': live.get(name, 0)}
            for name, target in REGION_FIXES.items()
            if name in dict_names
            and (_region_of(name, 'Region'),
                 _region_of(name, 'SubRegion')) != tuple(target)
        },
        'additions': additions,
        'deletions': [n for n in DEAD_ROWS if n in dict_names],
        'deletions_absent': [n for n in DEAD_ROWS if n not in dict_names],
        'canary': canary_row,
        'at_risk': {name: live[name] for name in DEAD_ROWS if live.get(name)},
        'dict_size': len(dict_names),
    }


def emit_dictionary_diff(eez_path, sheet_key=None):
    changes = compute_dictionary_changes(eez_path, sheet_key)
    additions = changes['additions']

    print('=' * 78)
    print('PROPOSED `Country dictionary` CHANGE SET  --  PREVIEW ONLY, NOTHING WRITTEN')
    print('=' * 78)

    print(f'\n1. ALIAS FIXES -- column I (EEZNamesIfDifferent) only, '
          f'{len(changes["alias_fixes"])} rows')
    print('   Column A is not touched, so no live `Country ratios` row is orphaned.')
    print('   Each of these currently misses, and rule (b) credits the polygon to')
    print('   the first ISO party instead -- a silent misattribution.')
    for country, new_alias in changes['alias_fixes'].items():
        print(f'     {country}')
        print(f'       -> {new_alias}')

    print(f'\n2. NEW ROWS -- {len(additions)}')
    if len(additions):
        print(additions[['Country', 'Region', 'SubRegion', 'POL_TYPE', 'basis']]
              .to_string(index=False))

    deletions = changes['deletions']
    print(f'\n3. DELETE -- {len(deletions)} rows with no v4 polygon and 0 live ratios rows')
    for name in DEAD_ROWS:
        absent = name in changes['deletions_absent']
        print(f'     {name}{"   (already absent)" if absent else ""}')

    canary_row = changes['canary']
    print(f'\n4. CLEAN -- {1 if canary_row else 0} row')
    if canary_row:
        print(f'     Canary Islands: alpha-3 {canary_row["alpha3_current"]!r} -> \'\' '
              '(no ISO 3166-1 code exists; ES-CN is a subdivision)')
        print(f'       Region stays {canary_row["Region"]} / {canary_row["SubRegion"]}')
        print('       Notes: replace the Nigeria-Morocco justification with the '
              'geographic rule')

    region_fixes = changes['region_fixes']
    print(f'\n5. REGION FIXES -- {len(region_fixes)} row(s)')
    for name, fix in sorted(region_fixes.items()):
        print(f'     {name}')
        print(f'       {fix["from"][0]} / {fix["from"][1]}  ->  '
              f'{fix["to"][0]} / {fix["to"][1]}')
        print(f'       {fix["live_rows"]} live `Country ratios` row(s) change region')

    print('\n6. PLACEMENT -- rows sitting outside their Region/SubRegion block')
    print('   The tab is grouped by Region/SubRegion, not sorted by name, so a row')
    print('   whose region is corrected (or was misfiled) has to move to stay with')
    print('   its block. Worked out at write time from the live row order.')

    total = changes['dict_size'] + len(additions) - len(deletions)
    print(f'\nNET: {changes["dict_size"]} rows -> {total} rows '
          f'(+{len(additions)} new, -{len(deletions)} deleted, '
          f'{len(changes["alias_fixes"])} aliases repointed, '
          f'{1 if canary_row else 0} cleaned)')
    if not any([len(additions), len(deletions), changes['alias_fixes'],
                region_fixes, canary_row]):
        print('\nNOTHING PENDING -- the live tab already matches this change set.')
        return changes

    print('\nSEQUENCING')
    at_risk = changes['at_risk']
    if at_risk:
        for name, count in sorted(at_risk.items()):
            print(f'  {name!r} still has {count} live row(s) -- delete it and that '
                  'row loses its Region lookup.')
        print('  Apply the deletions and the length write together.')
    else:
        print(f'  None of the {len(deletions)} deletions appear in the live '
              '`Country ratios` tab,')
        print('  and the alias fixes only touch column I, so nothing can be')
        print('  orphaned. This change set and the length write are independent.')

    print('\nNothing above has been written. Applying it is a separate, explicitly')
    print('approved action.')
    return changes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--eez', type=Path, default=DEFAULT_EEZ,
                        help='EEZ land union shapefile (default: %(default)s)')
    parser.add_argument('--natural-earth', type=Path, default=DEFAULT_NE,
                        help='Natural Earth 10m admin 0 shapefile (default: %(default)s)')
    parser.add_argument('--out-dir', type=Path, default=HERE,
                        help='where to write the .gpkg and sidecars (default: this folder)')
    parser.add_argument('--overlap-policy', choices=('keep', 'drop'), default='keep',
                        help="'keep' retains joint-regime and overlapping-claim "
                             "polygons as named entities (the decision on record); "
                             "'drop' restricts the layer to single-country space")
    parser.add_argument('--sheet-key', default=None,
                        help='override the pipelines spreadsheet key')
    parser.add_argument('--emit-dictionary-diff', action='store_true',
                        help='print the proposed Country dictionary change set and '
                             'exit without building anything or writing to any sheet')
    parser.add_argument('--apply-dictionary-diff', action='store_true',
                        help='apply that change set to the Country dictionary tab. '
                             'Simulates the whole request sequence locally first and '
                             'refuses to write if the simulation does not reproduce '
                             'the expected table')
    parser.add_argument('--validate-write', action='store_true',
                        help='with --apply-dictionary-diff, send every request through '
                             'gws --dry-run instead of writing')
    args = parser.parse_args(argv)

    for path in (args.eez, args.natural_earth):
        if not Path(path).exists():
            parser.error(f'missing source file: {path}')

    if args.emit_dictionary_diff:
        emit_dictionary_diff(args.eez, args.sheet_key)
        return 0

    if args.apply_dictionary_diff:
        import sheet_writer

        changes = emit_dictionary_diff(args.eez, args.sheet_key)
        sheet_key = args.sheet_key or sheets_client.PIPELINES_SHEET_KEY
        plan = sheet_writer.plan_dictionary(changes, sheet_key=sheet_key)
        print('\n--- write plan ---')
        print(sheet_writer.describe_dictionary(plan))

        problems, _ = sheet_writer.simulate_dictionary(plan, sheet_key=sheet_key)
        if problems:
            print(f'\nSIMULATION FAILED ({len(problems)} problems) -- nothing written')
            for problem in problems[:20]:
                print(f'  {problem}')
            return 1
        print('\nsimulation clean: replaying the requests locally reproduces the '
              'expected table exactly.')

        if args.validate_write:
            backend = sheets_client.get_backend(require_write=True)
            sheet_writer.write_dictionary(plan, sheet_key=sheet_key,
                                          backend=backend, dry_run=True)
            print('every request validated by gws --dry-run; nothing was sent.')
            return 0

        sheet_writer.write_dictionary(plan, sheet_key=sheet_key)
        problems = sheet_writer.verify_dictionary(plan, sheet_key=sheet_key)
        if problems:
            print('\nVERIFY FAILED:')
            for problem in problems:
                print(f'  {problem}')
            return 1
        print(f'\nwritten and verified: {plan["data_rows"]} rows, '
              f'{len(plan["added"])} added, {len(plan["deleted"])} deleted, '
              f'{len(plan["moved"])} moved, {len(plan["cell_edits"])} cells edited.')
        return 0

    build(args.eez, args.natural_earth, args.out_dir,
          overlap_policy=args.overlap_policy, sheet_key=args.sheet_key)
    return 0


if __name__ == '__main__':
    sys.exit(main())
