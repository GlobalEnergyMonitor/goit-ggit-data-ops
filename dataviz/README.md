# dataviz

A small kit for making static maps in GEM house style. Each map is one SVG that holds the title, subtitle, map, legend, source line, note and logo, so the exported file is complete on its own. A PNG is exported alongside it.

The kit covers maps only for now. Plans for charts are in [FUTURE.md](FUTURE.md). The style rules are in [STYLE.md](STYLE.md). Finished figures are listed in [GALLERY.md](GALLERY.md).

## Make a new map

You need Python 3 and Google Chrome. Nothing is downloaded at run time: D3, the basemaps and the fonts are all in this folder.

1. Copy the template. The new folder can sit anywhere in this repo.

   ```
   python dataviz/new_map.py writing-and-analysis/2027-03-some-report/my-map --name GGIT-my-map-2027-03
   ```

2. Open it in a browser while you work. Leave this running and reload the page after each edit. Use a hard reload (Cmd-Shift-R) if a change does not show up.

   ```
   python dataviz/export.py writing-and-analysis/2027-03-some-report/my-map --serve
   ```

3. Edit `prep_data.py` in the new folder so it writes real data into `data/`, then run it. As copied, it writes made-up example data. The comments in that file show the block to use for gas pipelines and LNG terminals.

4. Edit `map.js` in the new folder. Work down it in order: the text, the map window and projection, the label positions, the line and point styles, the legend. The comments in the file explain each step.

5. Export the SVG and the PNG into the figure folder.

   ```
   python dataviz/export.py writing-and-analysis/2027-03-some-report/my-map
   ```

6. Check the PNG by eye against the checklist at the bottom of [STYLE.md](STYLE.md). Then add a `README.md` to the figure folder that says what the map shows and which rows were chosen, and add the figure to [GALLERY.md](GALLERY.md).

## What is in this folder

```
dataviz/
├── README.md             this file
├── STYLE.md              the style rules, a dated copy of GEM's style guide
├── GALLERY.md            figures made with the kit
├── FUTURE.md             what the kit does not do yet
├── tokens.json           every color, font and size, in one file
├── export.py             writes the SVG and PNG, or serves a figure for editing
├── new_map.py            copies the template into a new figure folder
├── shared/
│   ├── gem-figure.js     the figure frame, the legend, the layer helpers and the export
│   ├── gem-figure.css    the styles, written with the values from tokens.json
│   ├── gem-fonts.css     the two GEM fonts, embedded
│   ├── gem_prep.py       readers for the pipelines sheet, the routes and the LNG terminals
│   ├── assets/           the GEM logo
│   └── vendor/           D3, topojson and the basemaps, pinned (see vendor/README.md)
└── template-map/         the starting point for a new map, with made-up data
```

## How a figure is put together

A figure folder holds four things.

- `prep_data.py` reads the source data and writes small files into `data/`. It is the only part that needs access to GEM data.
- `data/` holds those small files: the highlighted lines, the grey background network and the labeled points.
- `map.js` holds what is specific to this map: the text, the map window, the projection, the label positions and the styles.
- `index.html` loads the shared kit and `map.js`. It rarely needs editing.

Everything shared comes from `dataviz/shared/`. `gem-figure.js` draws the title, subtitle, legend, footer and logo at the sizes and spacing in `tokens.json`, so a new map gets the house layout without any layout code. Labels and the projection are still set by hand for each map, because those are judgment calls that differ every time.

Colors come from `GEM.colors` in `map.js`, which reads `tokens.json`. Do not type a hex code into a figure. If a value is wrong or missing, fix `tokens.json` so every figure gets the fix.

## What gets committed

This repo ignores data files and PNGs by default. A figure folder made from the template carries its own `.gitignore` that lets its small prepared data files and its PNG through, so the figure can be rebuilt and viewed from GitHub. The full database pull that `prep_data.py` saves under `data/raw/` stays out of git.

This repo is public. Committing a figure's `data/` folder publishes that data. Commit it only when the data is already public or is cleared to be.

## Changing the shared kit

A change in `shared/` or `tokens.json` changes every figure that uses the kit the next time it is exported. After a change, export the template and at least one real map again and compare the new PNGs with the old ones.

The Hormuz map from June 2026 was made before this kit and does not use it. See [GALLERY.md](GALLERY.md).
