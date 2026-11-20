"""
Data prep for the Alaska LNG map (Nov 2026 gas release social posts).

Everything is read as it stands today, not from a release file. The reads and the file formats are shared with the other maps and live in dataviz/shared/gem_prep.py. This script only decides which rows go on this map.

Writes into data/:

  lng-pipelines.geojson      gas pipeline rows tied to Alaska LNG, any status: the associated-terminal column names Alaska LNG, or the pipeline or segment name mentions Alaska LNG or Alaska Gasline.
  operating-context.geojson  operating US gas pipelines inside the padded map frame, the grey background layer.
  terminals.csv              the Alaska LNG export terminal.
  route-lengths.txt          geodetic length of each highlighted route, in km and miles.
  raw/                       the full terminals pull, kept out of git.

Usage:
  python prep_data.py
"""

import pathlib
import sys

from pyproj import Geod

HERE = pathlib.Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / "dataviz").is_dir())
sys.path.insert(0, str(REPO / "dataviz" / "shared"))
import gem_prep  # noqa: E402

OUT = HERE / "data"

# The map window in map.js, padded so background lines run to the map edge.
FRAME_PAD = [-170, 55, -130, 72]  # [minlon, minlat, maxlon, maxlat]
TERM = gem_prep.TERMINAL_COLUMN


def main():
    OUT.mkdir(exist_ok=True)
    back = gem_prep.read_backend()
    routes = gem_prep.load_routes()

    named = (back["PipelineName"].str.contains("Alaska LNG|Alaska Gasline", case=False)
             | back["SegmentName"].str.contains("Alaska LNG|Alaska Gasline", case=False))
    flagged = back[back[TERM].str.contains("Alaska LNG", case=False) | named].copy()
    print(flagged[["ProjectID", "PipelineName", "SegmentName", "Status", TERM]].to_string())
    flagged["geometry"] = flagged["ProjectID"].map(routes)
    no_route = flagged[flagged["geometry"].isna()]
    hl = flagged[flagged["geometry"].notna()]

    n_lines = gem_prep.write_lines(OUT / "lng-pipelines.geojson", hl)

    geod = Geod(ellps="WGS84")
    lens = {r["ProjectID"]: geod.geometry_length(r["geometry"]) / 1000 for _, r in hl.iterrows()}
    (OUT / "route-lengths.txt").write_text("\n".join(f"{k}: {v:.1f} km = {v / 1.609344:.1f} miles" for k, v in lens.items()) + "\n")
    print("route lengths (geodetic, km):", {k: round(v, 1) for k, v in lens.items()})

    # Background: operating US gas lines (backend status today) inside the frame.
    op = back[(back["Status"] == "operating") & back["CountriesOrAreas"].str.contains("United States")]
    n_context = gem_prep.write_context(OUT / "operating-context.geojson", op, routes, FRAME_PAD)

    # Terminals served by the highlighted lines (all of them, routed or not).
    served = sorted({t for v in flagged[TERM] for t in gem_prep.split_terminals(v)})
    out = gem_prep.write_terminals(OUT / "terminals.csv", gem_prep.pull_terminals(OUT / "raw"), served)

    print(f"highlighted pipelines with routes: {n_lines} ({hl.Status.value_counts().to_dict()})")
    print("flagged rows with no route:", no_route[["ProjectID", "PipelineName", "SegmentName", "Status"]].values.tolist())
    print(f"operating context features: {n_context}")
    print("terminals:", [(o["label"], o["status"]) for o in out])
    missing = set(served) - {o["name"] for o in out}
    if missing:
        print("served terminals not plotted:", sorted(missing))


if __name__ == "__main__":
    main()
