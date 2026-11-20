/* GEM map template. Copy this folder with `python dataviz/new_map.py <new folder>`, then edit this file.
 *
 * The data in data/ is made up, so the template draws without any database or sheet access. Replace it by editing prep_data.py and running it.
 *
 * This file holds only what is specific to one map. Work down it in order:
 *   1. TEXT and OUT_NAME
 *   2. MAP_H, WINDOW and the projection
 *   3. label positions
 *   4. the styles and the order of the layers
 *   5. the legend
 * The figure frame (title, subtitle, legend, footer, logo, export) and the layer helpers come from dataviz/shared/gem-figure.js. Colors and sizes come from dataviz/tokens.json through GEM.colors. Don't type a hex code here.
 */

// 1. Text. The title states the takeaway in a short sentence. The subtitle says what is plotted. Leave `note` out if there is nothing to add.
const TEXT = {
  title: "Template: say the main point of the map here",
  subtitle: "Say what is plotted, with units and dates where they apply",
  source: "Source: Global Energy Monitor, Global Gas Infrastructure Tracker, Month Year",
  note: "Note: The lines and points on this map are made-up examples.",
};
// File name for the exported SVG and PNG. Tracker, subject, year and month.
const OUT_NAME = "GEM-template-map";

// 2. Map area. MAP_H is its height in px; the width is fixed by the style guide. WINDOW is the area that must be visible. Spare room shows real geography.
const MAP_H = 480;
const WINDOW = { lon0: -106.6, lon1: -88.4, lat0: 25.5, lat1: 33.4 };
// A conic projection suits a mid-latitude region. Set the two parallels about a sixth of the way in from the bottom and top of the window, and rotate by minus the central longitude.
const projection = () => d3.geoConicConformal().parallels([27, 32]).rotate([97.5, 0]);

// 3. Labels, hand-placed. Region names: [name, lon, lat, class] with class "country-label" or "state-label".
const REGION_LABELS = [
  ["TEXAS", -99.0, 31.6, "state-label"],
  ["LOUISIANA", -92.35, 31.25, "state-label"],
  ["MEXICO", -102.4, 27.5, "country-label"],
];
// Point label placement: [dx, dy, text-anchor]. The default is right of the dot. Add a label here only when the default collides with something.
const LABEL_POS = { "Example terminal B": [-9, 0, "end"] };

const lineTip = (p) => `<b>${p.name}</b><br><span class="meta">${p.status}</span>`;
const pointTip = (d) => `<b>${d.label}</b><br><span class="meta">${d.status}</span>`;

Promise.all([
  GEM.ready({ world: true, usStates: true }), // usStates draws US state borders; leave it out elsewhere
  d3.json("data/lines.geojson"),
  d3.json("data/context.geojson"),
  d3.csv("data/points.csv", (r) => ({ label: r.label, status: r.status, lat: +r.latitude, lon: +r.longitude })),
]).then(([{ world, usStates }, lines, context, points]) => {
  const C = GEM.colors;

  // 4. Styles. `cat` must match the `category` value in data/lines.geojson. `key` picks the .pipe--<key> line width in gem-figure.css. The first style listed is drawn on top.
  // One hue with solid and dashed lines keeps the map to the style guide's limit of a few colors.
  const LINE_STYLE = [
    { cat: "construction", key: "construction", label: "Pipeline, in construction", color: C.orange, dash: null },
    { cat: "proposed", key: "proposed", label: "Pipeline, proposed", color: C.orange, dash: "7,6" },
  ];
  const CONTEXT = { label: "Operating pipeline", color: C.background };
  const POINT_STYLE = {
    operating: { label: "Terminal, operating", fill: C.teal, stroke: C.white },
    "in development": { label: "Terminal, in development", fill: C.white, stroke: C.teal },
  };

  const fig = GEM.figure({ text: TEXT, mapH: MAP_H, outName: OUT_NAME });
  const proj = fig.fit(projection(), WINDOW);
  const path = d3.geoPath(proj);

  // Layers, drawn bottom to top.
  const g = fig.frame();
  GEM.layers.basemap(g, path, { world, usStates });
  GEM.layers.labels(g, proj, REGION_LABELS);
  GEM.layers.context(g, path, context.features, CONTEXT.color);
  GEM.layers.lines(g, path, lines.features, LINE_STYLE, { tip: lineTip });
  GEM.layers.points(g, proj, points, { styles: POINT_STYLE, labelPos: LABEL_POS, tip: pointTip });

  // 5. Legend. Put it in whichever corner of the map is empty.
  fig.legend(
    [
      ...LINE_STYLE.map((s) => ({ kind: "line", cls: `pipe--${s.key}`, ...s })),
      { kind: "line", cls: "context", ...CONTEXT },
      ...Object.values(POINT_STYLE).map((s) => ({ kind: "point", ...s })),
    ],
    { corner: "bottom-left" },
  );

  fig.finish(); // always last: draws the map outline and the logo, and switches on export
});
