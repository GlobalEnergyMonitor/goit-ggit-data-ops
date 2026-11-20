# Future plans

The kit makes static maps. These are the things it does not do yet, roughly in the order they are likely to be wanted. Nothing here is started.

## Charts

Add chart support so a bar or line chart can sit beside a map with the same header, footer, fonts and colors.

- A `template-chart/` folder next to `template-map/`, built on the same `GEM.figure()` frame. The frame already draws the title, subtitle, footer and logo and handles export, so a chart only needs its own body. D3 alone would do it. Observable Plot is worth a look because it needs much less code for standard charts.
- Chart helpers in `shared/gem-figure.js`: axes and gridlines at the style guide's sizes, and a legend with square swatches at the guide's 4 px gap.
- A matplotlib style file generated from `tokens.json`, for charts made in the release notebooks. This would give notebook figures the same fonts and colors without leaving Python.
- `tokens.json` already holds the chart values from the style guide, such as the gridline color.

## A config-driven map builder

Today each map has a hand-written `map.js`. A simple map could instead be described in a short settings file that names the data, the window and the text, with labels placed automatically. This was left out on purpose for now, because label placement and projection choice are where most of the work and judgment go, and three maps are too few to know what the settings should be.

## Automatic label placement

Labels are placed by hand in pixels. A helper that proposes non-overlapping positions would save the most time per map, even if the result still needs a check by eye.

## More data readers

`shared/gem_prep.py` reads gas pipelines, pipeline routes and LNG terminals. Oil and NGL pipelines, power plants and extraction sites would each need a reader.

## Move the kit to its own repo

The kit lives here because the first maps were made here. If other GEM teams start using it, it should move to its own repo so they do not need this one. The `dataviz/` folder is self-contained to make that move simple. Figures would then load the kit from the new repo instead of by a relative path.

## An Observable version

GEM's color guide already lives in an Observable notebook. The same template could be published there, so people can make a map in the browser without Python or Chrome on their computer.

## Bring the Hormuz map onto the kit

The June 2026 Hormuz map has its own copy of the styles and the export script, at the older 1000 px width. Moving it onto the kit would mean re-placing every label for 800 px. Do this only if that map needs to be published again.

## Checks

- A test that exports the template and compares it with a saved PNG, so a change to the shared kit that moves something is caught.
- A check that fails if a figure's `map.js` contains a hex code.
