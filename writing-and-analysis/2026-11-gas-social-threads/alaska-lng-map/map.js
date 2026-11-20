/* Alaska LNG pipeline map, GGIT November 2026.
 *
 * This file holds only what is specific to this map: the text, the map window and projection, the label positions and the order of the layers. The figure frame (title, subtitle, legend, footer, logo, export) and the layer helpers come from dataviz/shared/gem-figure.js, and the style values from dataviz/tokens.json.
 *
 * Data comes from data/, made by prep_data.py. View or export with dataviz/export.py, because a browser blocks data loading from a file opened directly.
 */

const TEXT = {
  title: "Alaska LNG would pipe North Slope gas 800 miles to Cook Inlet",
  subtitle:
    "Gas pipeline in development to supply the proposed Alaska LNG export terminal, shown with the operating pipeline network",
  source: "Source: Global Energy Monitor, Global Gas Infrastructure Tracker, October 2026",
  note: "Note: Includes the Point Thomson feeder line, which would carry gas from the Point Thomson field to the main pipeline.",
};
const OUT_NAME = "GGIT-Alaska-LNG-2026-11";

// Height of the map area in px. The width is fixed by the style guide.
const MAP_H = 568;
// Geographic window. The projection is fitted so this box is contained in the map area; spare room shows real geography.
const WINDOW = { lon0: -158.5, lon1: -138.5, lat0: 59.0, lat1: 71.3 };

// Region names, hand-placed: [name, lon, lat, class]
const REGION_LABELS = [
  ["CANADA", -136.5, 66.3, "country-label"],
  ["ALASKA", -155.5, 66.2, "state-label"],
];
// Small place names: [name, lon, lat, dx, dy, anchor, dot?]
const PLACES = [
  ["Prudhoe Bay", -148.35, 70.25, 9, -8, "start", true],
  ["Fairbanks", -147.72, 64.84, 9, 4, "start", true],
  ["Anchorage", -149.9, 61.22, 9, 4, "start", true],
  ["Cook Inlet", -152.6, 59.55, 0, 0, "start", false],
];
// Terminal label placement: [dx, dy, text-anchor]. The default is right of the dot.
const LABEL_POS = { "Alaska LNG": [-10, 5, "end"] };

const lineTip = (p) =>
  `<b>${p.name}${p.segment ? " (" + p.segment + ")" : ""}</b><br>` +
  `<span class="meta">${p.status}${p.capacity_bcmy ? " · " + p.capacity_bcmy + " bcm/y" : ""}</span><br>` +
  `${p.terminal ? "Linked terminal: " + p.terminal : "No named terminal"}`;
const pointTip = (d) => `<b>${d.name}</b><br><span class="meta">${d.status} (units: ${d.units})</span>`;

Promise.all([
  GEM.ready({ world: true, usStates: true }),
  d3.json("data/lng-pipelines.geojson"),
  d3.json("data/operating-context.geojson"),
  d3.csv("data/terminals.csv", (r) => ({
    name: r.name,
    label: r.label,
    status: r.status,
    units: r.unit_statuses,
    lat: +r.latitude,
    lon: +r.longitude,
  })),
]).then(([{ world, usStates }, lines, operating, terminals]) => {
  const C = GEM.colors;
  // `cat` must match the `category` value in data/lng-pipelines.geojson. `key` picks the .pipe--<key> line width.
  const LINE_STYLE = [
    { cat: "construction", key: "construction", label: "LNG-linked pipeline, in construction", color: C.orange, dash: null },
    { cat: "proposed", key: "proposed", label: "LNG-linked pipeline, proposed", color: C.orange, dash: "7,6" },
  ];
  const CONTEXT = { label: "Operating gas pipeline", color: C.background };
  // Teal for terminals: filled is operating, open is in development.
  const TERMINAL_STYLE = {
    operating: { label: "LNG export terminal, operating", fill: C.teal, stroke: C.white },
    "in development": { label: "LNG export terminal, in development", fill: C.white, stroke: C.teal },
  };

  const fig = GEM.figure({ text: TEXT, mapH: MAP_H, outName: OUT_NAME });
  const proj = fig.fit(d3.geoConicConformal().parallels([55, 65]).rotate([150, 0]), WINDOW);
  const path = d3.geoPath(proj);

  const g = fig.frame();
  GEM.layers.basemap(g, path, { world, usStates });
  GEM.layers.labels(g, proj, REGION_LABELS);
  GEM.layers.context(g, path, operating.features, CONTEXT.color);
  GEM.layers.lines(g, path, lines.features, LINE_STYLE, { tip: lineTip });
  GEM.layers.points(g, proj, terminals, { styles: TERMINAL_STYLE, labelPos: LABEL_POS, tip: pointTip });
  GEM.layers.places(g, proj, PLACES);

  // The legend lists only the categories that are on the map.
  const present = new Set(lines.features.map((f) => f.properties.category));
  fig.legend(
    [
      ...LINE_STYLE.filter((s) => present.has(s.cat)).map((s) => ({ kind: "line", cls: `pipe--${s.key}`, ...s })),
      { kind: "line", cls: "context", ...CONTEXT },
      ...Object.entries(TERMINAL_STYLE)
        .filter(([status]) => terminals.some((t) => t.status === status))
        .map(([, s]) => ({ kind: "point", ...s })),
    ],
    { corner: "top-left" },
  );

  fig.finish();
});
