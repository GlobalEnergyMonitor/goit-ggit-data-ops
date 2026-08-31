# Hormuz crude-oil alternatives — map figure

Static map of Strait of Hormuz crude-oil alternative pipeline routes for the
GOIT June 2026 release, built to the GEM chart-anatomy spec (one self-contained
SVG → drops in next to the report's Flourish figures).

Structured the way a newsroom graphics desk would: **data prep is separate from
rendering, and the figure is hand-editable HTML/CSS/JS** (no code-in-strings).

## Files

| File | What it is |
|------|------------|
| `index.html` | page structure; loads `style.css` + `map.js` |
| `style.css`  | GEM chart-anatomy styling (fonts, palette) — **edit the look here** |
| `map.js`     | the D3 figure — **edit the chart here** (style config + layout at top) |
| `data/`      | inputs: highlighted routes (geojson), markers (csv), operating context (geojson) |
| `assets/`    | `gem-logo-midnight.svg` (inlined into the figure) |
| `prep_data.py` | regenerates `data/operating-context-2026-06.geojson` from the release gpkg |
| `export.py`  | renders publication PNG + SVG via headless Chrome |

## Live editing (recommended)

The figure `fetch()`es `data/`, which browsers block over `file://`, so it needs
a local server. Use one with **auto-reload** so CSS/JS edits show up live:

- **VS Code Live Server** (zero terminal): right-click `index.html` → *Open with
  Live Server* (or click **Go Live**). Edit `style.css` / `map.js`, save, and the
  browser reloads instantly.
- **Terminal one-liner** (no install, no project): `npx live-server map` — serves
  `map/` and auto-reloads on save.

Then **export from the browser**: the figure has its own **Download SVG** /
**Download PNG** buttons (PNG scale 2×/3×/4×). That's the whole loop — edit →
auto-reload → click to export.

> Plain `python -m http.server` also serves the folder, but has **no auto-reload**
> (manual refresh each edit), so prefer Live Server for tweaking.

`d3`, `topojson-client`, and the country basemap load from CDN, so an internet
connection is needed to view or export.

## Headless export (optional)

`export.py` regenerates the assets from the command line without opening a
browser — handy for "rebuild the final asset and move on". It produces the same
SVG/PNG as the Download buttons, so it's optional.

```bash
python export.py              # write PNG (3×) + SVG next to this folder
python export.py --scale 2    # PNG at 2× instead
python export.py --serve      # plain dev server (no auto-reload) + Ctrl-C
```

### Quick edit map

| Change | Where |
|--------|-------|
| Route colours / dashes | `CATEGORY_STYLE` in `map.js` |
| Line widths (map **and** legend together) | `--pipe-w-*` vars in `style.css` |
| Grey context-layer colour/label | `CONTEXT_STYLE` in `map.js` (width: `--pipe-w-context`) |
| Figure size | `Wfig` / `Hfig` + layout block in `map.js` (and `FIG_W/H` in `export.py`) |
| Map window (lon/lat) | `FRAME` in `map.js` |
| Title / subtitle / source text | the `.text("…")` calls in `map.js` |
| Marker positions / labels | `data/flourish-hormuz-points.csv` |
| Fonts / palette | `style.css` |

## Data prep

`prep_data.py` keeps the operating-context layer reproducible from source:
reads the June 2026 GOIT release gpkg, keeps operating oil/NGL pipelines (status
bucket from `gem_tracker_constants`, so it matches release/QC totals), clips to a
padded map frame, and writes geometry-only geojson.

```bash
python prep_data.py           # dry run — report feature count vs saved file
python prep_data.py --write   # overwrite data/operating-context-2026-06.geojson
```

The highlighted routes (`flourish-hormuz-lines.geojson`) and markers
(`flourish-hormuz-points.csv`) are hand-curated, not regenerated.
