"""
Data-prep step for the Hormuz figure — regenerate the faint grey context layer.

Newsroom pattern: keep data wrangling out of the render code. This reads the
June 2026 GOIT release gpkg, keeps the operating *oil* pipelines (oil fuel bucket,
NGL excluded), clips them to a padded version of the map frame, drops attributes
(geometry only — the context layer is unlabelled), and writes
data/operating-context-2026-06.geojson.

The two highlighted inputs in data/ — flourish-hormuz-lines.geojson and
flourish-hormuz-points.csv — are hand-curated, not regenerated here.

Usage:
  python prep_data.py            # dry run: report feature count vs the saved file
  python prep_data.py --write    # overwrite data/operating-context-2026-06.geojson

Status + fuel buckets come from gem_tracker_constants so it matches release/QC totals.
"""

import argparse
import json
import pathlib

import geopandas as gpd
from gem_tracker_constants import OIL_FUEL_OPTIONS

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]  # .../goit-ggit-data-ops
GPKG = REPO / "scripts" / "data-file-creation" / "data-files" / "GEM-GOIT-Oil-NGL-Pipelines-2026-06.gpkg"
OUT = HERE / "data" / "operating-context-2026-06.geojson"

# Map frame is lon 34–60E, lat 21–39N (see FRAME in map.js); pad ~2° so lines
# that exit the frame still draw to its edge rather than being clipped short.
FRAME_PAD = [32, 19, 60, 41]  # [minlon, minlat, maxlon, maxlat]


def build(write=False):
    g = gpd.read_file(GPKG)
    g = g[~g.geometry.isna()].to_crs(epsg=4326)
    g = g[g["Status"] == "operating"]
    g = g[g["Fuel"].isin(OIL_FUEL_OPTIONS)]  # oil only — exclude NGL lines
    minx, miny, maxx, maxy = FRAME_PAD
    g = g.cx[minx:maxx, miny:maxy]  # bbox spatial filter

    # geometry only — the context layer is unlabelled, so strip attributes to
    # keep the inlined/served file small.
    geoms = gpd.GeoSeries(g.geometry.values, crs=g.crs)
    fc = {"type": "FeatureCollection",
          "features": [{"type": "Feature", "properties": {}, "geometry": geom.__geo_interface__}
                       for geom in geoms]}

    n_existing = None
    if OUT.exists():
        n_existing = len(json.loads(OUT.read_text())["features"])

    print(f"operating in frame: {len(fc['features'])} features"
          + (f"  (saved file has {n_existing})" if n_existing is not None else ""))

    if write:
        OUT.write_text(json.dumps(fc), encoding="utf-8")
        print("wrote", OUT)
    else:
        print("dry run — pass --write to overwrite", OUT.name)


def main():
    ap = argparse.ArgumentParser(description="Regenerate the operating-context layer.")
    ap.add_argument("--write", action="store_true", help="overwrite the saved geojson")
    main_args = ap.parse_args()
    build(write=main_args.write)


if __name__ == "__main__":
    main()
