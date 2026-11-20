/* US LNG-linked gas pipelines map, GGIT November 2026.
 *
 * This file holds only what is specific to this map: the text, the map window and projection, the inset, the label positions, the Saguaro annotation and the order of the layers. The figure frame (title, subtitle, legend, footer, logo, export) and the layer helpers come from dataviz/shared/gem-figure.js, and the style values from dataviz/tokens.json.
 *
 * Data comes from data/, made by prep_data.py. View or export with dataviz/export.py, because a browser blocks data loading from a file opened directly.
 */

const TEXT = {
  title: "The US is building gas pipelines to feed LNG exports",
  subtitle:
    "Gas pipelines in development to supply the growing US LNG export market, shown with the specific LNG terminals they will serve and the broader operating pipeline network",
  source: "Source: Global Energy Monitor, Global Gas Infrastructure Tracker, October 2026",
  note: "Note: Includes four pipelines in construction (Blackcomb, Blackfin, Eiger Express and Pelican) that will deliver gas to hubs that feed LNG plants and other buyers. Alaska LNG is not shown.",
};
const OUT_NAME = "GGIT-US-LNG-pipelines-2026-11";

// Height of the map area in px, tall enough for the legend to sit below the Rio Grande labels. The width is fixed by the style guide.
const MAP_H = 560;
// Geographic window. The projection is fitted so this box is contained in the map area; spare room shows real geography.
const WINDOW = { lon0: -106.6, lon1: -88.4, lat0: 23.7, lat1: 33.4 };
const projection = () => d3.geoConicConformal().parallels([27, 32]).rotate([97.5, 0]);
// Gap in px between the map edge and both the legend and the inset.
const MARGIN = 10;

// Inset: zoom on the Sabine Pass and Lake Charles cluster, in the map's bottom right corner.
const INSET = {
  window: { lon0: -94.43, lon1: -93.03, lat0: 29.56, lat1: 30.24 },
  w: 310,
  h: 205,
  titleH: 26, // room for the inset title
  title: "Sabine Pass and Lake Charles area",
};

// Region names, hand-placed: [name, lon, lat, class]
const REGION_LABELS = [
  ["TEXAS", -99.0, 32.75, "state-label"],
  ["LOUISIANA", -92.35, 31.25, "state-label"],
  ["NEW MEXICO", -105.0, 32.85, "state-label"],
  ["MISSISSIPPI", -89.7, 32.3, "state-label"],
  ["MEXICO", -102.4, 27.5, "country-label"],
];

// Terminal label placement: [dx, dy, text-anchor]. The default is right of the dot.
const LABEL_POS = {
  main: {
    "Rio Grande LNG": [-8, -9, "end"],
    "Texas LNG": [-8, 9, "end"],
    "Freeport LNG": [8, 10, "start"],
    "Plaquemines LNG": [-9, -12, "end"],
    "Delfin FLNG": [9, 6, "start"], // crosses the inset leader line, so it is drawn above it
  },
  inset: {
    "Sabine Pass LNG": [-14, 25, "middle"],
    "Golden Pass LNG": [-7, 8, "end"],
    "Port Arthur LNG": [6, -14, "middle"],
    "CP2 LNG": [8, -8, "start"],
    "Commonwealth LNG": [-2, 25, "middle"],
    "Woodside Louisiana LNG": [-9, 6, "end"],
    "Magnolia LNG": [4, -14, "middle"],
  },
};
// Terminals drawn only in the inset. The main map gets one box for the cluster.
const INSET_ONLY = new Set(Object.keys(LABEL_POS.inset));

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
  const { svg, mapX, mapW, mapTop, mapBottom } = fig;

  // The same layers are drawn twice: once for the main map and once for the inset.
  function drawLayers(g, proj, { inset }) {
    const path = d3.geoPath(proj);
    GEM.layers.basemap(g, path, { world, usStates });
    if (!inset) GEM.layers.labels(g, proj, REGION_LABELS);
    GEM.layers.context(g, path, operating.features, CONTEXT.color);
    GEM.layers.lines(g, path, lines.features, LINE_STYLE, { tip: lineTip });
    GEM.layers.points(g, proj, terminals.filter((t) => INSET_ONLY.has(t.label) === inset), {
      styles: TERMINAL_STYLE,
      labelPos: inset ? LABEL_POS.inset : LABEL_POS.main,
      groupClass: inset ? "terminals-inset" : "terminals-main",
      tip: pointTip,
    });
  }

  // ---- main map ----
  const proj = fig.fit(projection(), WINDOW);
  const g = fig.frame();
  drawLayers(g, proj, { inset: false });

  // Saguaro annotation: the Saguaro Connector meets the Sierra Madre pipeline at the Rio Grande, and Sierra Madre runs off the frame's west edge toward Sonora.
  if (terminals.some((t) => t.label.startsWith("Saguaro"))) {
    const exit = proj([-106.6, 30.61]); // where Sierra Madre leaves the frame
    const x0 = mapX + 12, y0 = exit[1] + 16;
    const ann = g.append("g").attr("class", "annotation");
    ann.append("path").attr("d", `M${x0 + 44},${y0} L${x0 + 2},${y0}`).attr("marker-end", "url(#arrow)");
    ann.append("text").attr("x", x0).attr("y", y0 + 24).attr("text-anchor", "start")
      .selectAll("tspan").data(["Continues about 750 km to", "Saguaro Energía LNG in Sonora,", "Mexico (in development)"]).join("tspan")
      .attr("x", x0).attr("dy", (d, i) => (i ? 18 : 0)).text((d) => d);
  }
  svg.append("defs").append("marker").attr("id", "arrow").attr("viewBox", "0 0 10 10")
    .attr("refX", 8).attr("refY", 5).attr("markerWidth", 7).attr("markerHeight", 7)
    .attr("orient", "auto-start-reverse")
    .append("path").attr("d", "M1,1 L9,5 L1,9").attr("fill", "none").attr("stroke", C.text).attr("stroke-width", 2);

  // ---- inset ----
  const ix = mapX + mapW - INSET.w - MARGIN;
  const iy = mapBottom - MARGIN - INSET.h;
  const iproj = GEM.fit(projection(), [[ix, iy + INSET.titleH], [ix + INSET.w, iy + INSET.h]], INSET.window);

  // box on the main map showing the inset area, and a leader from it to the inset
  const b0 = proj([INSET.window.lon0, INSET.window.lat1]), b1 = proj([INSET.window.lon1, INSET.window.lat0]);
  svg.append("rect").attr("class", "inset-marker")
    .attr("x", b0[0]).attr("y", b0[1]).attr("width", b1[0] - b0[0]).attr("height", b1[1] - b0[1]);
  svg.append("line").attr("class", "inset-leader")
    .attr("x1", (b0[0] + b1[0]) / 2).attr("y1", b1[1]).attr("x2", ix + INSET.w / 2).attr("y2", iy);
  // main-map terminals and labels sit above the cluster box and leader line
  svg.node().appendChild(svg.select(".terminals-main").node());

  svg.append("rect").attr("class", "inset-bg").attr("x", ix).attr("y", iy).attr("width", INSET.w).attr("height", INSET.h);
  const ig = fig.clipBox(ix, iy + INSET.titleH, INSET.w, INSET.h - INSET.titleH, "inset-clip");
  drawLayers(ig, iproj, { inset: true });
  svg.append("rect").attr("class", "inset-frame").attr("x", ix).attr("y", iy).attr("width", INSET.w).attr("height", INSET.h);
  svg.append("text").attr("class", "inset-title").attr("x", ix + 10).attr("y", iy + 18).text(INSET.title);

  fig.legend(
    [
      ...LINE_STYLE.map((s) => ({ kind: "line", cls: `pipe--${s.key}`, ...s })),
      { kind: "line", cls: "context", ...CONTEXT },
      ...Object.values(TERMINAL_STYLE).map((s) => ({ kind: "point", ...s })),
    ],
    { corner: "bottom-left", margin: MARGIN },
  );

  fig.finish();
});
