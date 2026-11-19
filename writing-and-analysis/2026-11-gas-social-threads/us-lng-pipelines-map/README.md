# US LNG pipelines map (Nov 2026 gas release social posts)

A static GEM-style map of US gas pipelines in construction or proposed that the backend flags as associated with an LNG export terminal, the terminals they serve, and the operating gas network as a grey background. Built from the Hormuz D3 SVG template in `writing-and-analysis/2026-06-goit-release/hormuz-alternatives/map/`.

## Regenerate

```
python prep_data.py          # backend flags via gws-gem (read-only) + Nov 2026 pipelines gpkg + Oct 2026 LNG terminals gpkg -> data/
python export.py --scale 2   # writes GGIT-US-LNG-pipelines-2026-11.png and .svg
python export.py --serve     # live preview while editing map.js
```

`data/` and the exports are gitignored. Text, colors, label offsets and the inset window all live at the top of `map.js`.

## Scope choices

- Highlighted lines: `AssociatedWithLNGExportOrImport = export`, status construction (solid) or proposed (dashed), `CountriesOrAreas` includes the United States. Routes are joined from the release gpkg on ProjectID.
- Eleven flagged rows have no route in the release file, including the Commonwealth LNG pipeline, so they are not drawn. The note on the map says so.
- The four shared hub lines (Blackcomb, Blackfin, Eiger Express, Pelican) are included and named in the note.
- "Louisiana LNG Terminal" in the pipelines sheet is treated as Woodside Louisiana LNG.
- Alaska LNG and the Ohio line are outside the frame. Saguaro Energía (Sonora, Mexico) is shown by an arrow.
- Terminal status is "operating" if any export unit is operating, otherwise "in development".
