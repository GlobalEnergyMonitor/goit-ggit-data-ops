# Alaska LNG map (Nov 2026 gas release social posts)

A static GEM-style map of the proposed Alaska LNG gas pipeline, the Alaska LNG export terminal at Nikiski, and the operating gas pipelines in Alaska as a grey background. Sibling of `../us-lng-pipelines-map/`. Both are built with the shared map kit in `dataviz/` at the repo root. See `dataviz/README.md` for how the kit works.

## Regenerate

Run these from the repo root.

```
python writing-and-analysis/2026-11-gas-social-threads/alaska-lng-map/prep_data.py      # today's data: backend sheet (gws-gem, read-only), routes repo normalized branch, LNG terminals from the read-only DB -> data/
python dataviz/export.py writing-and-analysis/2026-11-gas-social-threads/alaska-lng-map           # writes GGIT-Alaska-LNG-2026-11.png (2x) and .svg
python dataviz/export.py writing-and-analysis/2026-11-gas-social-threads/alaska-lng-map --serve   # live preview while editing map.js
```

The small prepared files in `data/` and the PNG are let through by this folder's `.gitignore`. The full terminals pull in `data/raw/` stays out of git. Text, place labels and the map window live at the top of `map.js`. Colors come from `dataviz/tokens.json`.

## Scope choices

- Highlighted lines: every Gas pipelines row whose `AssociatedLNGTerminal(s)` mentions Alaska LNG, plus any row whose name or segment mentions Alaska LNG or Alaska Gasline. On 2026-11-19 that is P0147 (Alaska LNG Pipeline, AKLNG) and P6534 (Point Thomson Unit Gas Transmission Pipeline), both proposed, both with routes. The note names the Point Thomson feeder.
- Length: the drawn P0147 route measures 1,393.6 km (866 miles) geodetic; the backend `LengthKnownKm` is 1,298.74 km (807 miles). The title says 800 miles, which matches the backend figure and the project's published length. P6534 adds 99.8 km (62 miles).
- Context: operating gas pipelines with `CountriesOrAreas` containing United States, inside the Alaska frame.
- Terminal: Alaska LNG Terminal (Nikiski, units T1 to T3, all proposed), drawn as in development.
- Legend shows only the categories on the map (no construction line, no operating terminal).

Sizes, fonts, colors and footer layout follow `dataviz/STYLE.md`. The source line reads "October 2026", the release's data vintage.
