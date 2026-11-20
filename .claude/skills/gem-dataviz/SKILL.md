---
name: gem-dataviz
description: Make or edit a static GEM-style map figure (SVG and PNG) with the kit in dataviz/. Use when asked for a map, a figure for a report or social post, or a change to an existing map in this repo.
---

# GEM map figures

The kit, its instructions and its style rules are in `dataviz/`. Read these before writing any code:

- `dataviz/README.md` for the steps and the folder layout.
- `dataviz/STYLE.md` for the style rules and the pre-publish checklist.
- `dataviz/template-map/map.js` for the shape of a figure.

## Steps

1. Run `python dataviz/new_map.py <new folder> --name <output name>`. Put the folder beside the writing it belongs to, usually under `writing-and-analysis/<release folder>/`. Name the output by tracker, subject, year and month, for example `GGIT-Alaska-LNG-2026-11`.
2. Edit the new folder's `prep_data.py` to write real data, using the readers in `dataviz/shared/gem_prep.py`. They read the pipelines sheet, the routes and the terminals read-only. Unset `GDRIVE_API_CREDENTIALS` in the shell first. Print the rows that were selected and the rows that had no route.
3. Edit the new folder's `map.js`: text, window, projection, labels, styles, legend.
4. Run `python dataviz/export.py <folder>`, then open the PNG and look at it. Fix overlapping labels and export again. Repeat until the checklist in `dataviz/STYLE.md` passes.
5. Write a `README.md` in the figure folder saying what the map shows and which rows were chosen, and add the figure to `dataviz/GALLERY.md`.

## Rules

- Take colors from `GEM.colors`. Never type a hex code into a figure. A missing or wrong value is fixed in `dataviz/tokens.json`.
- Do not copy `gem-figure.js`, `gem-figure.css` or `export.py` into a figure folder. Figures share them.
- Do not change the width. It is fixed at 800 px by the style guide.
- Dashed lines must be drawn unclipped, or the dashes shift. `GEM.layers.lines` already does this. Follow it for any custom dashed layer.
- A change in `dataviz/shared/` or `tokens.json` affects every figure. After one, export the template and one real map again and compare the PNGs with the previous ones.
- The Hormuz map under `writing-and-analysis/2026-06-goit-release/` is legacy. Do not copy from it.
- The repo is public. A figure's `data/` folder is committed only when the user says so.
- Charts are not supported yet. See `dataviz/FUTURE.md`.
