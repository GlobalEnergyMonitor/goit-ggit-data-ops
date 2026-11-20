"""
Data prep for the Alaska LNG map (Nov 2026 gas release social posts).

Everything is read as it stands today, not from a release file:

  - pipeline flags and statuses: the backend Gas pipelines sheet, read-only
    through gws-gem (route-lengths/sheets_client.py);
  - pipeline routes: the routes repo's normalized branch (origin/normalized of
    goit-ggit-pipeline-routes-normalized), read with `git archive` so the local
    checkout's working tree is never touched;
  - LNG terminals: a fresh pull from the read-only GEM database through
    gem-db-ops/lng/pull.py.

Writes into data/ (gitignored, like all data in this repo):

  lng-pipelines.geojson      Gas pipeline rows tied to Alaska LNG: AssociatedLNGTerminal(s) names
                             Alaska LNG Terminal, or PipelineName/SegmentName mentions Alaska LNG
                             or Alaska Gasline, any status.
  operating-context.geojson  operating US gas pipelines inside the Alaska frame (simplified).
  terminals.csv              the Alaska LNG export terminal, status rolled up from its units.
  (data/route-lengths.txt)   geodetic length of each highlighted route, in km and miles.

  terminals.csv              the LNG export terminals those pipelines serve, one row
                             per terminal, with an operating / in development status
                             rolled up from the terminal's export units.

Usage:
  python prep_data.py
"""

import io
import json
import pathlib
import subprocess
import sys
import tarfile

import geopandas as gpd
import pandas as pd
from pyproj import Geod
from shapely.ops import linemerge

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]  # .../goit-ggit-data-ops
GEM_ROOT = REPO.parent
ROUTES_REPO = GEM_ROOT / "goit-ggit-pipeline-routes-normalized"
ROUTES_REF = "origin/normalized"
ROUTES_PATH = "data/individual-routes/gas-pipelines"
LNG_PULL = GEM_ROOT / "gem-db-ops" / "lng" / "pull.py"
OUT = HERE / "data"

sys.path.insert(0, str(REPO / "route-lengths"))
import sheets_client  # noqa: E402  (gws-gem, read-only)

# Map frame in map.js, padded so context lines run to the frame edge.
FRAME_PAD = [-170, 55, -130, 72]  # [minlon, minlat, maxlon, maxlat]
TERMINAL_ALIASES = {}
TERMINAL_NAME = "Alaska LNG Terminal"


def read_backend():
    header, rows = sheets_client.read_table(
        sheets_client.PIPELINES_SHEET_KEY, "Gas pipelines", header_row=3)
    n = len(header)
    df = pd.DataFrame([(r + [""] * n)[:n] for r in rows], columns=header)
    df = df.loc[:, ~pd.Index(df.columns).duplicated()]
    df["ProjectID"] = df["ProjectID"].str.strip()
    return df[df["ProjectID"] != ""]


def load_routes():
    """{ProjectID: geometry} for every gas route with geometry on the normalized branch."""
    git = ["git", "-C", str(ROUTES_REPO)]
    subprocess.run(git + ["fetch", "-q", "origin", "normalized"], check=True)
    sha = subprocess.run(git + ["rev-parse", "--short", ROUTES_REF],
                         capture_output=True, text=True, check=True).stdout.strip()
    tar = subprocess.run(git + ["archive", ROUTES_REF, ROUTES_PATH],
                         capture_output=True, check=True).stdout
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


def pull_terminals():
    out = OUT / "lng-terminals-today.csv"
    subprocess.run([sys.executable, str(LNG_PULL), "--output", str(out)],
                   check=True, capture_output=True)
    return pd.read_csv(out)


def split_terminals(v):
    names = [TERMINAL_ALIASES.get(x.strip(), x.strip()) for x in str(v).split(";")]
    return [x for x in names if x]


def main():
    OUT.mkdir(exist_ok=True)
    back = read_backend()
    routes = load_routes()

    term_col = "AssociatedLNGTerminal(s)"
    named = (back["PipelineName"].str.contains("Alaska LNG|Alaska Gasline", case=False)
             | back["SegmentName"].str.contains("Alaska LNG|Alaska Gasline", case=False))
    flagged = back[back[term_col].str.contains("Alaska LNG", case=False) | named].copy()
    print(flagged[["ProjectID", "PipelineName", "SegmentName", "Status", term_col]].to_string())
    flagged["geometry"] = flagged["ProjectID"].map(routes)
    no_route = flagged[flagged["geometry"].isna()]
    hl = flagged[flagged["geometry"].notna()]

    feats = []
    for _, r in hl.iterrows():
        feats.append({
            "type": "Feature",
            "properties": {
                "id": r["ProjectID"],
                "name": r["PipelineName"],
                "segment": r["SegmentName"],
                "status": r["Status"],
                "category": "proposed" if r["Status"] == "proposed" else r["Status"],
                "terminal": "; ".join(split_terminals(r["AssociatedLNGTerminal(s)"])),
                "capacity_bcmy": r["CapacityBcm/y"],
            },
            "geometry": r["geometry"].simplify(0.003).__geo_interface__,
        })
    geod = Geod(ellps="WGS84")
    lens = {r["ProjectID"]: geod.geometry_length(r["geometry"]) / 1000 for _, r in hl.iterrows()}
    (OUT / "route-lengths.txt").write_text("\n".join(
        f"{k}: {v:.1f} km = {v / 1.609344:.1f} miles" for k, v in lens.items()) + "\n")
    print("route lengths (geodetic, km):", {k: round(v, 1) for k, v in lens.items()})
    (OUT / "lng-pipelines.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")

    # Background: operating gas lines (backend status today) inside the frame.
    op = back[(back["Status"] == "operating")
              & back["CountriesOrAreas"].str.contains("United States")]
    op_geoms = gpd.GeoSeries([routes[p] for p in op["ProjectID"] if p in routes], crs=4326)
    minx, miny, maxx, maxy = FRAME_PAD
    op_geoms = op_geoms.cx[minx:maxx, miny:maxy]
    # Some network rows are thousands of two-point segments; merge them into
    # long lines first so simplify can actually thin the vertices.
    ctx_geoms = op_geoms.apply(
        lambda g: linemerge(g) if g.geom_type == "MultiLineString" else g
    ).simplify(0.008, preserve_topology=False)
    (OUT / "operating-context.geojson").write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {}, "geometry": g.__geo_interface__}
                     for g in ctx_geoms if not g.is_empty]}), encoding="utf-8")

    # Terminals served by the highlighted lines (all of them, routed or not).
    served = sorted({t for v in flagged["AssociatedLNGTerminal(s)"] for t in split_terminals(v)})
    terms = pull_terminals()
    terms = terms[terms["TerminalName"].isin(served) & (terms["FacilityType"] == "export")]
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
    pd.DataFrame(out).to_csv(OUT / "terminals.csv", index=False)

    print(f"highlighted pipelines with routes: {len(feats)} "
          f"({hl.Status.value_counts().to_dict()})")
    print("flagged rows with no route:",
          no_route[["ProjectID", "PipelineName", "SegmentName", "Status"]].values.tolist())
    print(f"operating context features: {len(ctx_geoms)}")
    print("terminals:", [(o["label"], o["status"]) for o in out])
    missing = set(served) - {o["name"] for o in out}
    if missing:
        print("served terminals not plotted:", sorted(missing))


if __name__ == "__main__":
    main()
