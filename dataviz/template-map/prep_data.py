"""
Data prep for this map. Run it whenever the source data changes, then export the figure again.

As copied from the template, this script writes made-up example data, so the template draws without any database or sheet access. To use real data, replace example_data() with the block under "Real data" below.

Writes into data/:

  lines.geojson    the highlighted lines. Each feature needs a `category` that map.js has a style for.
  context.geojson  the grey background network, geometry only.
  points.csv       labeled points: label, status, latitude, longitude.

Usage:
  python prep_data.py
"""

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / "dataviz").is_dir())
OUT = HERE / "data"


def line(name, status, coords):
    return {"type": "Feature", "properties": {"name": name, "status": status, "category": status},
            "geometry": {"type": "LineString", "coordinates": coords}}


def example_data():
    lines = [
        line("Example pipeline A", "construction", [[-102.0, 31.9], [-99.5, 30.6], [-97.2, 29.3], [-95.4, 28.95]]),
        line("Example pipeline B", "proposed", [[-100.5, 28.6], [-98.9, 27.6], [-97.5, 26.0]]),
    ]
    context = [
        line("", "", [[-104.0, 31.5], [-101.0, 32.4], [-97.0, 32.6], [-94.0, 31.6], [-91.2, 30.4]]),
        line("", "", [[-97.0, 32.6], [-96.6, 30.0], [-97.4, 27.8]]),
        line("", "", [[-96.6, 30.0], [-94.1, 29.9], [-91.2, 30.4]]),
    ]
    for f in context:
        f["properties"] = {}
    points = "label,status,latitude,longitude\nExample terminal A,operating,28.95,-95.4\nExample terminal B,in development,26.0,-97.5\n"
    (OUT / "lines.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": lines}), encoding="utf-8")
    (OUT / "context.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": context}), encoding="utf-8")
    (OUT / "points.csv").write_text(points, encoding="utf-8")
    print(f"wrote example data: {len(lines)} lines, {len(context)} context lines, 2 points")


# ---- Real data ----
# For a gas pipeline map, delete example_data() and use the shared readers. They read the backend sheet, the routes repo and the terminals database as they stand today, all read-only. The two November 2026 LNG maps under writing-and-analysis/2026-11-gas-social-threads/ are full worked examples, including the file names their map.js expects.
#
#   sys.path.insert(0, str(REPO / "dataviz" / "shared"))
#   import gem_prep
#
#   back = gem_prep.read_backend()
#   routes = gem_prep.load_routes()
#   rows = back[back["Status"].isin(["construction", "proposed"]) & back["CountriesOrAreas"].str.contains("United States")].copy()
#   rows["geometry"] = rows["ProjectID"].map(routes)
#   gem_prep.write_lines(OUT / "lines.geojson", rows[rows["geometry"].notna()])
#   gem_prep.write_context(OUT / "context.geojson", back[back["Status"] == "operating"], routes, frame=[-110, 22, -85, 36])
#   served = sorted({t for v in rows[gem_prep.TERMINAL_COLUMN] for t in gem_prep.split_terminals(v)})
#   gem_prep.write_terminals(OUT / "points.csv", gem_prep.pull_terminals(OUT / "raw"), served)
#
# Print the rows that were selected and the rows that had no route, so a reader of the terminal output can check the map against the data.


def main():
    OUT.mkdir(exist_ok=True)
    example_data()


if __name__ == "__main__":
    main()
