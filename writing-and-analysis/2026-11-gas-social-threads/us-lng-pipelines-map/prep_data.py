"""
Data prep for the US LNG pipelines map (Nov 2026 gas release social posts).

Writes three files into data/ (gitignored, like all data in this repo):

  lng-pipelines.geojson      US gas pipelines in construction or proposed that the
                             pipelines researcher flagged as associated with an LNG
                             export terminal (AssociatedWithLNGExportOrImport =
                             export). Flags and status come from the backend Gas
                             pipelines sheet, read-only through gws-gem; routes come
                             from the Nov 5 release gpkg, joined on ProjectID.
  operating-context.geojson  all operating gas pipelines inside the padded map frame
                             (geometry only, simplified), the grey background layer.
  terminals.csv              the LNG export terminals those pipelines serve, one row
                             per terminal, with an operating / in development status
                             rolled up from the Oct 2026 LNG terminals release.

Usage:
  python prep_data.py
"""

import json
import pathlib
import sys

import geopandas as gpd
import pandas as pd
from shapely.ops import linemerge

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]  # .../goit-ggit-data-ops
DATA_FILES = REPO / "releases" / "downloads" / "data-files"
PIPES_GPKG = DATA_FILES / "GEM-GGIT-Gas-Pipelines-2026-11.gpkg"
TERMS_GPKG = DATA_FILES / "GEM-GGIT-LNG-Terminals-2026-10.gpkg"
OUT = HERE / "data"

sys.path.insert(0, str(REPO / "route-lengths"))
import sheets_client  # noqa: E402  (gws-gem, read-only)

# Map frame in map.js, padded so context lines run to the frame edge.
FRAME_PAD = [-110, 22, -85, 36]  # [minlon, minlat, maxlon, maxlat]
HIGHLIGHT_STATUSES = ["construction", "proposed"]
# "Louisiana LNG Terminal" is the older name the Phase 3 Driftwood row uses for
# Woodside Louisiana LNG; its only terminal-tracker unit is cancelled.
TERMINAL_ALIASES = {"Louisiana LNG Terminal": "Woodside Louisiana LNG Terminal"}


def read_backend():
    header, rows = sheets_client.read_table(
        sheets_client.PIPELINES_SHEET_KEY, "Gas pipelines", header_row=3)
    n = len(header)
    df = pd.DataFrame([(r + [""] * n)[:n] for r in rows], columns=header)
    df = df.loc[:, ~pd.Index(df.columns).duplicated()]
    return df[df["ProjectID"].str.strip() != ""]


def split_terminals(v):
    names = [TERMINAL_ALIASES.get(x.strip(), x.strip()) for x in str(v).split(";")]
    return [x for x in names if x]


def main():
    OUT.mkdir(exist_ok=True)
    back = read_backend()
    flagged = back[
        (back["AssociatedWithLNGExportOrImport"].str.strip().str.lower() == "export")
        & back["Status"].isin(HIGHLIGHT_STATUSES)
        & back["CountriesOrAreas"].str.contains("United States")
    ].copy()

    geo = gpd.read_file(PIPES_GPKG).to_crs(epsg=4326)
    routes = geo[["ProjectID", "geometry"]]
    hl = routes.merge(flagged, on="ProjectID", how="right")
    no_route = hl[hl.geometry.isna()]
    hl = gpd.GeoDataFrame(hl[~hl.geometry.isna()], geometry="geometry", crs=4326)

    feats = []
    for _, r in hl.iterrows():
        feats.append({
            "type": "Feature",
            "properties": {
                "id": r["ProjectID"],
                "name": r["PipelineName"],
                "segment": r["SegmentName"],
                "status": r["Status"],
                "category": r["Status"],
                "terminal": "; ".join(split_terminals(r["AssociatedLNGTerminal(s)"])),
                "capacity_bcmy": r["CapacityBcm/y"],
            },
            "geometry": r.geometry.simplify(0.003).__geo_interface__,
        })
    (OUT / "lng-pipelines.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")

    # Background: operating gas lines in the frame (release file status).
    minx, miny, maxx, maxy = FRAME_PAD
    ctx = geo[(geo["Status"] == "operating") & ~geo.geometry.isna()].cx[minx:maxx, miny:maxy]
    # Some network rows are thousands of two-point segments; merge them into
    # long lines first so simplify can actually thin the vertices.
    ctx_geoms = ctx.geometry.apply(
        lambda g: linemerge(g) if g.geom_type == "MultiLineString" else g
    ).simplify(0.008, preserve_topology=False)
    (OUT / "operating-context.geojson").write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {}, "geometry": g.__geo_interface__}
                     for g in ctx_geoms if not g.is_empty]}), encoding="utf-8")

    # Terminals served by the highlighted lines (all of them, routed or not).
    served = sorted({t for v in flagged["AssociatedLNGTerminal(s)"] for t in split_terminals(v)})
    terms = gpd.read_file(TERMS_GPKG)
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
            "latitude": grp["Latitude"].astype(float).mean(),
            "longitude": grp["Longitude"].astype(float).mean(),
        })
    pd.DataFrame(out).to_csv(OUT / "terminals.csv", index=False)

    print(f"highlighted pipelines with routes: {len(feats)} "
          f"({(hl.Status == 'construction').sum()} construction, "
          f"{(hl.Status == 'proposed').sum()} proposed)")
    print("flagged rows with no route:",
          no_route[["ProjectID", "PipelineName", "SegmentName", "Status"]].values.tolist())
    print(f"operating context features: {len(ctx_geoms)}")
    print("terminals:", [(o["label"], o["status"]) for o in out])
    missing = set(served) - {o["name"] for o in out}
    if missing:
        print("served terminals not plotted:", sorted(missing))


if __name__ == "__main__":
    main()
