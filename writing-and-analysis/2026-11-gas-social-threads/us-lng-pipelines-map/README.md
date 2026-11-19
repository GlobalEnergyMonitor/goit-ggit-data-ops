# US LNG pipelines map (Nov 2026 gas release social posts)

A static GEM-style map of US gas pipelines in construction or proposed that the backend flags as associated with an LNG export terminal, the terminals they serve, and the operating gas network as a grey background. Built from the Hormuz D3 SVG template in `writing-and-analysis/2026-06-goit-release/hormuz-alternatives/map/`.

## Regenerate

```
python prep_data.py          # today's data: backend sheet (gws-gem, read-only), routes repo normalized branch, LNG terminals from the read-only DB -> data/
python export.py --scale 2   # writes GGIT-US-LNG-pipelines-2026-11.png and .svg
python export.py --serve     # live preview while editing map.js
```

`data/` and the exports are gitignored. Text, colors, label offsets and the inset window all live at the top of `map.js`.

## Scope choices

- Highlighted lines: `AssociatedWithLNGExportOrImport = export`, status construction (solid) or proposed (dashed), `CountriesOrAreas` includes the United States. Routes come from `origin/normalized` of goit-ggit-pipeline-routes-normalized, read with `git archive`, joined on ProjectID. No release file is used; the map shows the data as it stands on the day `prep_data.py` runs, and the source line carries that date.
- Flagged rows with no drawn route are left off the map, and the note says how many (six on 2026-11-19 after the route work that day: five upgrades that add no new pipe, and P5509, which duplicates the mapped Sabine Crossing row P7798; none is a missing line, so the note no longer mentions one). Update that count in `map.js` after a rerun.
- The four shared hub lines (Blackcomb, Blackfin, Eiger Express, Pelican) are included and named in the note.
- "Louisiana LNG Terminal" in the pipelines sheet is treated as Woodside Louisiana LNG.
- Alaska LNG and the Ohio line are outside the frame. Saguaro Energía (Sonora, Mexico) is shown by an arrow.
- Terminal status is "operating" if any export unit is operating, otherwise "in development".
