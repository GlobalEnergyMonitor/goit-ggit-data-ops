"""
Data prep for the US LNG pipelines map (Nov 2026 gas release social posts).

Everything is read as it stands today, not from a release file. The reads and the file formats are shared with the other maps and live in dataviz/shared/gem_prep.py. This script only decides which rows go on this map.

Writes into data/:

  lng-pipelines.geojson      US gas pipelines in construction or proposed that the pipelines researcher flagged as associated with an LNG export terminal (AssociatedWithLNGExportOrImport = export), plus the onward leg to Saguaro.
  operating-context.geojson  all operating gas pipelines inside the padded map frame, the grey background layer.
  terminals.csv              the LNG export terminals those pipelines serve, one row per terminal.
  raw/                       the full terminals pull, kept out of git.

Usage:
  python prep_data.py
"""

import pathlib
import sys

import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / "dataviz").is_dir())
sys.path.insert(0, str(REPO / "dataviz" / "shared"))
import gem_prep  # noqa: E402

OUT = HERE / "data"

# The map window in map.js, padded so background lines run to the map edge.
FRAME_PAD = [-110, 22, -85, 36]  # [minlon, minlat, maxlon, maxlat]
HIGHLIGHT_STATUSES = ["construction", "proposed"]
# "Louisiana LNG Terminal" is the older name the Phase 3 Driftwood row uses for Woodside Louisiana LNG; its only terminal-tracker unit is cancelled.
TERMINAL_ALIASES = {"Louisiana LNG Terminal": "Woodside Louisiana LNG Terminal"}
# The Saguaro Connector (P5664) stops at the Rio Grande; the Sierra Madre Gas Pipeline (P5795, Mexico, proposed) carries that gas on to Puerto Libertad. The backend does not flag P5795 as LNG-linked, so it is added here by hand.
ONWARD_LEGS = {"P5795": "Saguaro Energía LNG Terminal"}
TERM = gem_prep.TERMINAL_COLUMN


def main():
    OUT.mkdir(exist_ok=True)
    back = gem_prep.read_backend()
    routes = gem_prep.load_routes()

    flagged = back[
        (back["AssociatedWithLNGExportOrImport"].str.strip().str.lower() == "export")
        & back["Status"].isin(HIGHLIGHT_STATUSES)
        & back["CountriesOrAreas"].str.contains("United States")
    ].copy()
    # Onward legs: lines that carry flagged US gas the rest of the way to a terminal but are not flagged themselves (Mexico-only rows).
    onward = back[back["ProjectID"].isin(ONWARD_LEGS)].copy()
    onward[TERM] = onward["ProjectID"].map(ONWARD_LEGS)
    flagged = pd.concat([flagged, onward], ignore_index=True)
    flagged["geometry"] = flagged["ProjectID"].map(routes)
    no_route = flagged[flagged["geometry"].isna()]
    hl = flagged[flagged["geometry"].notna()]

    n_lines = gem_prep.write_lines(OUT / "lng-pipelines.geojson", hl, aliases=TERMINAL_ALIASES)

    # Background: operating gas lines (backend status today) inside the frame.
    n_context = gem_prep.write_context(OUT / "operating-context.geojson", back[back["Status"] == "operating"], routes, FRAME_PAD)

    # Terminals served by the highlighted lines (all of them, routed or not).
    served = sorted({t for v in flagged[TERM] for t in gem_prep.split_terminals(v, TERMINAL_ALIASES)})
    out = gem_prep.write_terminals(OUT / "terminals.csv", gem_prep.pull_terminals(OUT / "raw"), served)

    print(f"highlighted pipelines with routes: {n_lines} "
          f"({(hl.Status == 'construction').sum()} construction, {(hl.Status == 'proposed').sum()} proposed)")
    print("flagged rows with no route:", no_route[["ProjectID", "PipelineName", "SegmentName", "Status"]].values.tolist())
    print(f"operating context features: {n_context}")
    print("terminals:", [(o["label"], o["status"]) for o in out])
    missing = set(served) - {o["name"] for o in out}
    if missing:
        print("served terminals not plotted:", sorted(missing))


if __name__ == "__main__":
    main()
