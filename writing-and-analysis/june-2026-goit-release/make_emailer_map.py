"""
Hero map for the June 2026 GOIT emailer.

Eastern-Hemisphere-focused map of in-development (construction + proposed)
oil & NGL pipelines, drawn over the faint operating network, with a subtle
marker on the Strait of Hormuz. Construction vs proposed are colored
separately to support the "shrinkage is in proposals, not construction" point.

Data: scripts/data-file-creation/data-files/GEM-GOIT-Oil-NGL-Pipelines-2026-06.gpkg
Status buckets come from gem_tracker_constants so this matches release/QC totals.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd

HERE = __import__("pathlib").Path(__file__).resolve().parent
GPKG = (HERE / ".." / ".." / "scripts" / "data-file-creation" / "data-files"
        / "GEM-GOIT-Oil-NGL-Pipelines-2026-06.gpkg").resolve()
OUT = HERE / "GOIT-June2026-emailer-map.png"

# Eastern-Hemisphere extent: Africa + Asia [lon_min, lon_max, lat_min, lat_max]
EXTENT = [-22, 150, -38, 74]

# Palette (GEM-ish, colorblind-safe-ish)
C_OPERATING = "#cfcabf"   # faint warm gray
C_CONSTRUCTION = "#c0392b"  # bold red — actively being built
C_PROPOSED = "#2f6f9f"    # blue — proposed
HORMUZ = (56.4, 26.6)     # approx Strait of Hormuz

def main():
    g = gpd.read_file(GPKG)
    g = g[~g.geometry.isna()].to_crs(epsg=4326)

    operating = g[g["Status"] == "operating"]
    construction = g[g["Status"] == "construction"]
    proposed = g[g["Status"] == "proposed"]

    proj = ccrs.PlateCarree()
    fig = plt.figure(figsize=(12, 8), dpi=200)
    ax = plt.axes(projection=proj)
    ax.set_extent(EXTENT, crs=proj)

    # Basemap
    ax.add_feature(cfeature.OCEAN, facecolor="#f4f7f9", zorder=0)
    ax.add_feature(cfeature.LAND, facecolor="#ffffff", zorder=0)
    ax.add_feature(cfeature.COASTLINE, edgecolor="#b9c2c9", linewidth=0.4, zorder=1)
    ax.add_feature(cfeature.BORDERS, edgecolor="#e3e8ec", linewidth=0.3, zorder=1)

    # Operating network (context)
    if len(operating):
        operating.plot(ax=ax, color=C_OPERATING, linewidth=0.5, zorder=2)
    # In-development on top
    if len(proposed):
        proposed.plot(ax=ax, color=C_PROPOSED, linewidth=1.3, zorder=3, alpha=0.9)
    if len(construction):
        construction.plot(ax=ax, color=C_CONSTRUCTION, linewidth=1.6, zorder=4)

    # Strait of Hormuz marker
    ax.plot(*HORMUZ, marker="o", markersize=6, markerfacecolor="none",
            markeredgecolor="#222", markeredgewidth=1.2, transform=proj, zorder=6)
    ax.annotate("Strait of Hormuz", xy=HORMUZ, xytext=(HORMUZ[0] + 6, HORMUZ[1] + 7),
                transform=proj, fontsize=9, color="#222",
                arrowprops=dict(arrowstyle="-", color="#222", lw=0.8), zorder=6)

    # Legend
    handles = [
        Line2D([0], [0], color=C_CONSTRUCTION, lw=2.4, label="Under construction"),
        Line2D([0], [0], color=C_PROPOSED, lw=2.0, label="Proposed"),
        Line2D([0], [0], color=C_OPERATING, lw=1.4, label="Operating"),
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=9, frameon=True,
              framealpha=0.9, title="Oil & NGL pipelines", title_fontsize=10)

    ax.set_title("The world keeps building for oil — and the buildout has shifted to Asia and Africa",
                 fontsize=13, fontweight="bold", pad=10)
    fig.text(0.5, 0.045,
             "~32,400 km of oil pipelines in development worldwide  ·  Global Oil Infrastructure Tracker, June 2026  ·  Global Energy Monitor",
             ha="center", fontsize=8.5, color="#555")

    ax.spines["geo"].set_edgecolor("#cfd6db")
    fig.savefig(OUT, bbox_inches="tight", facecolor="white")
    print("wrote", OUT)
    print(f"operating={len(operating)} construction={len(construction)} proposed={len(proposed)}")

if __name__ == "__main__":
    main()
