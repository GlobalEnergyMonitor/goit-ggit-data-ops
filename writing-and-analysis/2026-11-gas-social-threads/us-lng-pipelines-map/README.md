# US LNG pipelines map (Nov 2026 gas release social posts)

A static GEM-style map of US gas pipelines in construction or proposed that the backend flags as associated with an LNG export terminal, the terminals they serve, and the operating gas network as a grey background. Built with the shared map kit in `dataviz/` at the repo root. See `dataviz/README.md` for how the kit works.

## Regenerate

Run these from the repo root.

```
python writing-and-analysis/2026-11-gas-social-threads/us-lng-pipelines-map/prep_data.py      # today's data: backend sheet (gws-gem, read-only), routes repo normalized branch, LNG terminals from the read-only DB -> data/
python dataviz/export.py writing-and-analysis/2026-11-gas-social-threads/us-lng-pipelines-map           # writes GGIT-US-LNG-pipelines-2026-11.png (2x) and .svg
python dataviz/export.py writing-and-analysis/2026-11-gas-social-threads/us-lng-pipelines-map --serve   # live preview while editing map.js
```

The small prepared files in `data/` and the PNG are let through by this folder's `.gitignore`. The full terminals pull in `data/raw/` stays out of git. Text, label offsets and the inset window all live at the top of `map.js`. Colors come from `dataviz/tokens.json`.

## Scope choices

- Highlighted lines: `AssociatedWithLNGExportOrImport = export`, status construction (solid) or proposed (dashed), `CountriesOrAreas` includes the United States. Routes come from `origin/normalized` of goit-ggit-pipeline-routes-normalized, read with `git archive`, joined on ProjectID. No release file is used; the map shows the data as it stands on the day `prep_data.py` runs. The source line is set by hand in `map.js` and reads "October 2026", the release's data vintage, not the run date.
- Flagged rows with no drawn route are left off the map, and the note says how many (five on 2026-11-19 after the route work that day, all upgrades that add no new pipe; none is a missing line, so the note no longer mentions one. P5509 was removed that day as a duplicate of P7798, and the Gillis Access extension, P7807, went into service and now draws in the grey background). Update that count in `map.js` after a rerun.
- The four shared hub lines (Blackcomb, Blackfin, Eiger Express, Pelican) are included and named in the note.
- "Louisiana LNG Terminal" in the pipelines sheet is treated as Woodside Louisiana LNG.
- Alaska LNG and the Ohio line are outside the frame. Saguaro Energía (Sonora, Mexico) is off the west edge: the Saguaro Connector (P5664) stops at the Rio Grande, so the Sierra Madre Gas Pipeline (P5795, Mexico, proposed) is added by hand through `ONWARD_LEGS` in `prep_data.py`, because the backend doesn't flag it as LNG-linked. An arrow at the frame edge points the way to the terminal.
- Terminal status is "operating" if any export unit is operating, otherwise "in development".

## House style

Checked against GEM's data visualization style guide (https://globalenergymonitor.org/data-visualization-style-guide) and the GEM color notebook (https://observablehq.com/d/76aaf1373f5dfdab) on 2026-11-19. The Alaska map follows the same rules.

The rules now live in `dataviz/STYLE.md` and the values in `dataviz/tokens.json`. The list below is how they apply to this map.

- Width: the figure is 800 px wide, the guide's maximum, so the default 2x export gives a 1600 px PNG. The width is set once, in `dataviz/tokens.json`.
- Fonts: Plus Jakarta Sans for the title (28 px bold), subtitle (18 px) and footer (14 px). Barlow Semi Condensed at 16 px for the legend, terminal labels, state labels, annotations and the inset title. The country label is 20 px. All text is #3A4A50.
- Colors: orange #FE4F2D for the highlighted pipelines, grey #BECCCF for the operating network, teal #016B83 for terminals and the logo, water #C8D5D9, land #F2F2EB, borders #555555 at 40% opacity for countries and 18% for states.
- Footer: the source line comes first and the note below it. The logo is 40 px high at the bottom right with a 28 px margin.
- Spacing: 32 px between the header, the map and the footer.
- Labels are placed by hand in pixels (`LABEL_POS`, `REGION_LABELS`), so check every label after changing the width, the map height or the inset window.
- One known departure: the gap between a legend sample and its label is 10 px. The guide says 4 px, which is written for small square swatches.
