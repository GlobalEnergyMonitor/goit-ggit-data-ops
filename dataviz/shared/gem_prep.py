"""
Shared data prep for GEM map figures: the reads and the file writers that every pipeline map repeats.

A figure's own prep_data.py decides WHICH rows go on the map. This module does the rest:

  read_backend()        the backend Gas pipelines sheet as it stands today, read-only through gws-gem
  load_routes()         every drawn gas route from the routes repo's normalized branch
  pull_terminals(dir)   a fresh LNG terminals pull from the read-only GEM database
  split_terminals(v)    the terminal names in one "AssociatedLNGTerminal(s)" cell
  write_lines(...)      highlighted pipelines   -> a .geojson the map colors by `category`
  write_context(...)    background network      -> a .geojson of plain simplified lines
  write_terminals(...)  LNG export terminals    -> a .csv with one row per terminal

Nothing here writes to a Google Sheet or a database. It expects two sibling checkouts next to this repo: goit-ggit-pipeline-routes-normalized (routes) and gem-db-ops (terminals).

Use it from a figure's prep_data.py:

  import pathlib, sys
  REPO = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "dataviz").is_dir())
  sys.path.insert(0, str(REPO / "dataviz" / "shared"))
  import gem_prep
"""

import io
import json
import pathlib
import subprocess
import sys
import tarfile

import geopandas as gpd
import pandas as pd
from shapely.ops import linemerge

REPO = pathlib.Path(__file__).resolve().parents[2]  # .../goit-ggit-data-ops
GEM_ROOT = REPO.parent
ROUTES_REPO = GEM_ROOT / "goit-ggit-pipeline-routes-normalized"
ROUTES_REF = "origin/normalized"
ROUTES_PATH = "data/individual-routes/gas-pipelines"
LNG_PULL = GEM_ROOT / "gem-db-ops" / "lng" / "pull.py"

TERMINAL_COLUMN = "AssociatedLNGTerminal(s)"
# Simplify tolerances in degrees. Highlighted lines keep more detail than the background network.
LINE_TOLERANCE = 0.003
CONTEXT_TOLERANCE = 0.008


def read_backend(tab="Gas pipelines"):
    """The backend pipelines sheet as a DataFrame of strings, one row per ProjectID."""
    sys.path.insert(0, str(REPO / "route-lengths"))
    import sheets_client  # gws-gem, read-only

    header, rows = sheets_client.read_table(sheets_client.PIPELINES_SHEET_KEY, tab, header_row=3)
    n = len(header)
    df = pd.DataFrame([(r + [""] * n)[:n] for r in rows], columns=header)
    df = df.loc[:, ~pd.Index(df.columns).duplicated()]
    df["ProjectID"] = df["ProjectID"].str.strip()
    return df[df["ProjectID"] != ""]


def load_routes():
    """{ProjectID: geometry} for every gas route with geometry on the normalized branch.

    Read with `git archive`, so the routes checkout's working tree is never touched.
    """
    git = ["git", "-C", str(ROUTES_REPO)]
    subprocess.run(git + ["fetch", "-q", "origin", "normalized"], check=True)
    sha = subprocess.run(git + ["rev-parse", "--short", ROUTES_REF], capture_output=True, text=True, check=True).stdout.strip()
    tar = subprocess.run(git + ["archive", ROUTES_REF, ROUTES_PATH], capture_output=True, check=True).stdout
    routes = {}
    with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
        for m in tf.getmembers():
            if not m.name.endswith(".geojson"):
                continue
            feats = [f for f in json.load(tf.extractfile(m))["features"] if f.get("geometry")]
            if not feats:
                continue  # placeholder file, no drawn route yet
            g = gpd.GeoDataFrame.from_features(feats, crs=4326).geometry.union_all()
            if not g.is_empty:
                routes[pathlib.Path(m.name).stem] = g
    print(f"routes: {len(routes)} gas routes with geometry at {ROUTES_REF} {sha}")
    return routes


def pull_terminals(raw_dir):
    """Pull the LNG terminals table into raw_dir and return it. raw_dir holds the full pull and is not committed."""
    raw_dir = pathlib.Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / "lng-terminals-today.csv"
    subprocess.run([sys.executable, str(LNG_PULL), "--output", str(out)], check=True, capture_output=True)
    return pd.read_csv(out)


def split_terminals(v, aliases=None):
    """The terminal names in one semicolon-separated cell, with old names mapped to current ones."""
    aliases = aliases or {}
    names = [aliases.get(x.strip(), x.strip()) for x in str(v).split(";")]
    return [x for x in names if x]


def write_lines(path, rows, aliases=None, category=lambda r: r["Status"]):
    """Write the highlighted pipelines. `rows` is backend rows with a `geometry` column; returns the feature count.

    `category` sets the value map.js styles by. It defaults to the backend status.
    """
    feats = []
    for _, r in rows.iterrows():
        feats.append({
            "type": "Feature",
            "properties": {
                "id": r["ProjectID"],
                "name": r["PipelineName"],
                "segment": r["SegmentName"],
                "status": r["Status"],
                "category": category(r),
                "terminal": "; ".join(split_terminals(r[TERMINAL_COLUMN], aliases)),
                "capacity_bcmy": r["CapacityBcm/y"],
            },
            "geometry": r["geometry"].simplify(LINE_TOLERANCE).__geo_interface__,
        })
    pathlib.Path(path).write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
    return len(feats)


def write_context(path, rows, routes, frame):
    """Write the background network: the routes of `rows` inside `frame`, geometry only. Returns the feature count.

    `frame` is [minlon, minlat, maxlon, maxlat], set a little wider than the map window so lines run to the map edge.
    """
    geoms = gpd.GeoSeries([routes[p] for p in rows["ProjectID"] if p in routes], crs=4326)
    minx, miny, maxx, maxy = frame
    geoms = geoms.cx[minx:maxx, miny:maxy]
    # Some network rows are thousands of two-point segments. Merge them into long lines first so simplify can thin the vertices.
    geoms = geoms.apply(lambda g: linemerge(g) if g.geom_type == "MultiLineString" else g).simplify(CONTEXT_TOLERANCE, preserve_topology=False)
    pathlib.Path(path).write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {}, "geometry": g.__geo_interface__} for g in geoms if not g.is_empty],
    }), encoding="utf-8")
    return len(geoms)


def write_terminals(path, terminals, served):
    """Write one row per LNG export terminal named in `served`. Returns the rows written.

    A terminal with any operating unit is "operating". One with only construction or proposed units is "in development". Anything else is left off the map.
    """
    terms = terminals[terminals["TerminalName"].isin(served) & (terminals["FacilityType"] == "export")]
    out = []
    for name, grp in terms.groupby("TerminalName"):
        statuses = set(grp["Status"])
        if "operating" in statuses:
            status = "operating"
        elif statuses & {"construction", "proposed"}:
            status = "in development"
        else:
            continue
        out.append({
            "name": name,
            "label": name.replace(" Terminal", ""),
            "status": status,
            "unit_statuses": ", ".join(sorted(statuses)),
            "country": grp["Country/Area"].iloc[0],
            "latitude": pd.to_numeric(grp["Latitude"], errors="coerce").mean(),
            "longitude": pd.to_numeric(grp["Longitude"], errors="coerce").mean(),
        })
    pd.DataFrame(out).to_csv(path, index=False)
    return out
