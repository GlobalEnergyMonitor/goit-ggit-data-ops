/* US gas pipelines linked to LNG export terminals — GGIT November 2026.
 *
 * Built from the Hormuz alternatives figure (2026-06-goit-release). The WHOLE
 * figure is one SVG (title, subtitle, map, inset, legend, notes, source, GEM
 * logo) laid out to the GEM chart-anatomy spec, so each export is complete.
 *
 * Data comes from data/ (made by prep_data.py; run a local server, see
 * export.py, because file:// blocks fetch). d3, topojson and the basemaps load
 * from CDN, so viewing or exporting needs internet.
 *
 * What lives where:
 *   - Line colors / dashes / legend text  -> CATEGORY_STYLE below
 *   - Terminal marker colors               -> TERMINAL_STYLE below
 *   - Line widths (map + legend)           -> --pipe-w-* vars in style.css
 *   - Map window                           -> LON0/LON1/LAT0/LAT1 below
 *   - Inset window + position              -> INSET below
 *   - Terminal label placement             -> LABEL_POS below
 *   - Title / subtitle / notes / source    -> TEXT below
 */

// ---- Text ----
const TEXT = {
  title: "The US is building gas pipelines to feed LNG exports",
  subtitle:
    "Gas pipelines in construction or proposed that GEM links to LNG export terminals, the terminals they serve, and the operating gas pipeline network",
  note:
    "Note: Includes four lines in construction (Blackcomb, Blackfin, Eiger Express and Pelican) that deliver gas to hubs that LNG plants draw from, as well as to other buyers. Eleven linked lines have no mapped route yet, including the Commonwealth LNG pipeline. Alaska LNG is not shown.",
  source:
    "Source: Global Energy Monitor, Global Gas Infrastructure Tracker, November 2026; LNG terminals, October 2026",
};

// ---- Style config ----
// `cat` MUST match the `category` value in data/lng-pipelines.geojson.
// `key` maps to the .pipe--<key> CSS class that sets the line width.
const CATEGORY_STYLE = [
  {
    cat: "construction",
    label: "LNG-linked pipeline, in construction",
    key: "construction",
    color: "#FE4F2D", // GEM orange
    dash: null,
  },
  {
    cat: "proposed",
    label: "LNG-linked pipeline, proposed",
    key: "proposed",
    color: "#FE4F2D",
    dash: "7,6",
  },
];
const CONTEXT_STYLE = { label: "Operating gas pipeline", color: "#becccf" };
// Teal (GEM core categorical) for terminals: filled = operating, open = in development.
const TERMINAL_STYLE = {
  operating: { label: "LNG export terminal, operating", fill: "#016B83", stroke: "#ffffff" },
  "in development": { label: "LNG export terminal, in development", fill: "#ffffff", stroke: "#016B83" },
};

// Region labels, hand-placed. [name, lon, lat, class]
const REGION_LABELS = [
  ["TEXAS", -99.0, 32.75, "state-label"],
  ["LOUISIANA", -92.35, 31.25, "state-label"],
  ["NEW MEXICO", -105.0, 32.85, "state-label"],
  ["MISSISSIPPI", -89.7, 32.3, "state-label"],
  ["MEXICO", -103.6, 29.0, "country-label"],
];

// ---- Figure layout (GEM chart anatomy) ----
const Wfig = 1000,
  PAD = 28;
const mapX = PAD,
  mapW = Wfig - 2 * PAD; // 944
const mapH = 600;
// Geographic window. The projection is a conic fitted to this box, so the box
// is "contained" in the map rectangle; any spare room shows real geography.
const LON0 = -106.6,
  LON1 = -88.4,
  LAT0 = 23.7,
  LAT1 = 33.4;

// Inset: zoom on the Sabine Pass / Lake Charles cluster.
const INSET = {
  lon0: -94.3,
  lon1: -92.9,
  lat0: 29.56,
  lat1: 30.24,
  w: 370,
  h: 240,
  left: 520, // px in from the map's left edge (sits over the Gulf, below Freeport)
  bottom: 16, // px up from the map's bottom edge
  title: "Sabine Pass and Lake Charles area",
};

// Terminal label placement: [dx, dy, text-anchor]; default is right of the dot.
const LABEL_POS = {
  main: {
    "Rio Grande LNG": [-8, -9, "end"],
    "Texas LNG": [-8, 9, "end"],
    "Freeport LNG": [8, 10, "start"],
    "Plaquemines LNG": [-9, -12, "end"],
    "Delfin FLNG": [9, 6, "start"],
  },
  inset: {
    "Sabine Pass LNG": [10, 4, "start"],
    "Golden Pass LNG": [-6, 24, "middle"],
    "Port Arthur LNG": [6, -14, "middle"],
    "CP2 LNG": [10, -8, "start"],
    "Commonwealth LNG": [4, 24, "middle"],
    "Woodside Louisiana LNG": [-9, 6, "end"],
    "Magnolia LNG": [9, -6, "start"],
  },
};
// Terminals drawn only in the inset (the main map gets one box for the cluster).
const INSET_ONLY = new Set(Object.keys(LABEL_POS.inset));

// Header typography (baselines + line heights, px).
const TITLE_TOP = 46,
  TITLE_LH = 34,
  TITLE_TO_SUB = 30,
  SUB_LH = 23,
  SUB_TO_MAP = 18;
const NOTE_LH = 19;

let mapTop, mapBottom, footerTop, Hfig;

function boxOutline(lon0, lon1, lat0, lat1, n = 20) {
  // sampled box edges, so a conic fit sees the curved parallels
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const lon = lon0 + ((lon1 - lon0) * i) / n;
    pts.push([lon, lat0], [lon, lat1]);
  }
  for (let i = 0; i <= n; i++) {
    const lat = lat0 + ((lat1 - lat0) * i) / n;
    pts.push([lon0, lat], [lon1, lat]);
  }
  return { type: "MultiPoint", coordinates: pts };
}

const styleByCat = new Map(CATEGORY_STYLE.map((c) => [c.cat, c]));

function wrapText(textSel, text, maxWidth, lineHeight) {
  const x = textSel.attr("x");
  const words = text.split(/\s+/);
  let line = [];
  let lines = 0;
  let tspan = textSel.append("tspan").attr("x", x).attr("dy", 0);
  words.forEach((w) => {
    line.push(w);
    tspan.text(line.join(" "));
    if (tspan.node().getComputedTextLength() > maxWidth && line.length > 1) {
      line.pop();
      tspan.text(line.join(" "));
      line = [w];
      tspan = textSel.append("tspan").attr("x", x).attr("dy", lineHeight).text(w);
      lines += 1;
    }
  });
  return lines + 1;
}

// ---- Load data, then draw ----
const EXPORT_PARAM = new URLSearchParams(location.search).get("export");
const tooltip = d3.select(".tooltip");
const WORLD = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json";
const STATES = "https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/states-10m.json";

let LINES, TERMINALS, OPERATING, WORLD_TOPO, STATES_TOPO, LOGO_PATHS = "";

Promise.all([
  d3.json("data/lng-pipelines.geojson"),
  d3.csv("data/terminals.csv", (r) => ({
    name: r.name,
    label: r.label,
    status: r.status,
    units: r.unit_statuses,
    lat: +r.latitude,
    lon: +r.longitude,
  })),
  d3.json("data/operating-context.geojson"),
  d3.json(WORLD).catch(() => null),
  d3.json(STATES).catch(() => null),
  d3.text("assets/gem-logo-midnight.svg").catch(() => ""),
]).then(([lines, terminals, operating, world, states, logoSvg]) => {
  LINES = lines;
  TERMINALS = terminals;
  OPERATING = operating;
  WORLD_TOPO = world;
  STATES_TOPO = states;
  LOGO_PATHS = extractLogoPaths(logoSvg);
  whenFontsLoaded().then(draw);
});

function whenFontsLoaded() {
  if (!document.fonts || !document.fonts.load) return Promise.resolve();
  const specs = [
    "400 18px 'Plus Jakarta Sans'",
    "600 16px 'Plus Jakarta Sans'",
    "700 28px 'Plus Jakarta Sans'",
    "400 16px 'Barlow Semi Condensed'",
    "500 20px 'Barlow Semi Condensed'",
    "600 16px 'Barlow Semi Condensed'",
  ];
  const loads = Promise.all(specs.map((s) => document.fonts.load(s))).then(
    () => document.fonts.ready,
  );
  const timeout = new Promise((res) => setTimeout(res, 8000));
  return Promise.race([loads, timeout]);
}

function extractLogoPaths(svgText) {
  if (!svgText) return "";
  const ds = [...svgText.matchAll(/<path\b[^>]*?\sd="([^"]+)"/g)].map((m) => m[1]);
  return ds.map((d) => `<path fill="#002430" d="${d}"></path>`).join("");
}

let svg;

function layoutHeader() {
  const title = svg.append("text").attr("class", "fig-title").attr("x", mapX).attr("y", TITLE_TOP);
  const titleLines = wrapText(title, TEXT.title, mapW, TITLE_LH);
  const subTop = TITLE_TOP + (titleLines - 1) * TITLE_LH + TITLE_TO_SUB;
  const subtitle = svg.append("text").attr("class", "fig-subtitle").attr("x", mapX).attr("y", subTop);
  const subLines = wrapText(subtitle, TEXT.subtitle, mapW, SUB_LH);
  mapTop = subTop + (subLines - 1) * SUB_LH + SUB_TO_MAP;
  mapBottom = mapTop + mapH;
}

function layoutFooter() {
  const note = svg.append("text").attr("class", "fig-note").attr("x", mapX).attr("y", mapBottom + 26);
  const noteLines = wrapText(note, TEXT.note, mapW, NOTE_LH);
  footerTop = mapBottom + 26 + (noteLines - 1) * NOTE_LH + 14;
  Hfig = footerTop + 50;
}

// Draws basemap + all data layers into group `g`, using projection `proj`.
function drawLayers(g, proj, opts) {
  const path = d3.geoPath(proj);
  if (WORLD_TOPO) {
    const countries = topojson.feature(WORLD_TOPO, WORLD_TOPO.objects.countries);
    g.append("g").selectAll("path").data(countries.features).join("path")
      .attr("class", "country").attr("d", path);
  }
  if (STATES_TOPO) {
    g.append("path")
      .datum(topojson.mesh(STATES_TOPO, STATES_TOPO.objects.states, (a, b) => a !== b))
      .attr("class", "state-border").attr("d", path);
  }
  if (WORLD_TOPO) {
    g.append("path").datum(topojson.mesh(WORLD_TOPO, WORLD_TOPO.objects.countries))
      .attr("class", "border").attr("d", path);
  }

  if (opts.labels) {
    g.append("g").selectAll("text").data(REGION_LABELS).join("text")
      .attr("class", (d) => d[3])
      .attr("transform", (d) => `translate(${proj([d[1], d[2]])})`)
      .text((d) => d[0]);
  }

  // grey operating network
  g.append("g").selectAll("path").data(OPERATING.features).join("path")
    .attr("class", "context").attr("d", path).attr("stroke", CONTEXT_STYLE.color);

  // highlighted lines: proposed under construction
  const order = { proposed: 0, construction: 1 };
  const feats = LINES.features.slice()
    .sort((a, b) => (order[a.properties.category] ?? 0) - (order[b.properties.category] ?? 0));
  const layer = g.append("g");
  feats.forEach((f) => {
    const s = styleByCat.get(f.properties.category);
    if (!s) return;
    const grp = layer.append("g");
    grp.append("path").attr("class", "pipe-hit").attr("d", path(f));
    grp.append("path").attr("class", `pipe pipe--${s.key}`).attr("d", path(f))
      .attr("stroke", s.color).attr("stroke-dasharray", s.dash);
    grp.on("mousemove", (e) => showLineTip(e, f.properties)).on("mouseleave", hideTip);
  });

  // terminals
  const pos = opts.inset ? LABEL_POS.inset : LABEL_POS.main;
  const terms = TERMINALS.filter((t) => (opts.inset ? INSET_ONLY.has(t.label) : !INSET_ONLY.has(t.label)));
  // operating drawn last so filled dots sit on top
  terms.sort((a, b) => (a.status === "operating") - (b.status === "operating"));
  const tg = g.append("g").selectAll("g").data(terms).join("g")
    .attr("transform", (d) => `translate(${proj([d.lon, d.lat])})`)
    .on("mousemove", (e, d) => showPointTip(e, d)).on("mouseleave", hideTip);
  tg.append("circle").attr("class", "terminal").attr("r", opts.inset ? 6 : 6)
    .attr("fill", (d) => TERMINAL_STYLE[d.status].fill)
    .attr("stroke", (d) => TERMINAL_STYLE[d.status].stroke);
  tg.append("text").attr("class", "terminal-label")
    .attr("x", (d) => (pos[d.label] || [9, 0])[0])
    .attr("y", (d) => (pos[d.label] || [9, 0])[1])
    .attr("text-anchor", (d) => (pos[d.label] || [9, 0, "start"])[2])
    .text((d) => d.label);
}

function draw() {
  svg = d3.select("#map").append("svg").attr("preserveAspectRatio", "xMidYMid meet");
  const bg = svg.append("rect").attr("x", 0).attr("y", 0).attr("width", Wfig).attr("fill", "#ffffff");

  layoutHeader();
  layoutFooter();
  svg.attr("viewBox", `0 0 ${Wfig} ${Hfig}`);
  bg.attr("height", Hfig);

  // ---- main map ----
  const proj = d3.geoConicConformal().parallels([27, 32]).rotate([97.5, 0])
    .fitExtent([[mapX, mapTop], [mapX + mapW, mapBottom]], boxOutline(LON0, LON1, LAT0, LAT1));

  svg.append("rect").attr("class", "water")
    .attr("x", mapX).attr("y", mapTop).attr("width", mapW).attr("height", mapH);
  svg.append("clipPath").attr("id", "frame-clip").append("rect")
    .attr("x", mapX).attr("y", mapTop).attr("width", mapW).attr("height", mapH);
  const g = svg.append("g").attr("clip-path", "url(#frame-clip)");
  drawLayers(g, proj, { labels: true, inset: false });

  // Saguaro annotation: the main line heads for the border, the terminal is in Sonora.
  const sag = TERMINALS.find((t) => t.label.startsWith("Saguaro"));
  if (sag) {
    const a = proj([-105.45, 31.2]);
    const ann = g.append("g").attr("class", "annotation");
    ann.append("path")
      .attr("d", `M${a[0] - 8},${a[1] + 11} L${a[0] - 46},${a[1] + 11}`)
      .attr("marker-end", "url(#arrow)");
    ann.append("text").attr("x", a[0] - 46).attr("y", a[1] + 36).attr("text-anchor", "start")
      .selectAll("tspan").data(["To Saguaro Energía LNG", "in Sonora, Mexico (in development)"]).join("tspan")
      .attr("x", a[0] - 46).attr("dy", (d, i) => (i ? 18 : 0)).text((d) => d);
  }
  svg.append("defs").append("marker").attr("id", "arrow").attr("viewBox", "0 0 10 10")
    .attr("refX", 8).attr("refY", 5).attr("markerWidth", 7).attr("markerHeight", 7)
    .attr("orient", "auto-start-reverse")
    .append("path").attr("d", "M1,1 L9,5 L1,9").attr("fill", "none").attr("stroke", "#3a4a50").attr("stroke-width", 1.5);

  // ---- inset ----
  const ix = mapX + INSET.left;
  const iy = mapBottom - INSET.bottom - INSET.h;
  const ITOP = 26; // room for the inset title
  const iproj = d3.geoConicConformal().parallels([27, 32]).rotate([97.5, 0])
    .fitExtent([[ix, iy + ITOP], [ix + INSET.w, iy + INSET.h]],
      boxOutline(INSET.lon0, INSET.lon1, INSET.lat0, INSET.lat1));

  // box on the main map showing the inset area
  const b0 = proj([INSET.lon0, INSET.lat1]), b1 = proj([INSET.lon1, INSET.lat0]);
  svg.append("rect").attr("class", "inset-marker")
    .attr("x", b0[0]).attr("y", b0[1]).attr("width", b1[0] - b0[0]).attr("height", b1[1] - b0[1]);
  // leader from the box to the inset
  svg.append("line").attr("class", "inset-leader")
    .attr("x1", (b0[0] + b1[0]) / 2).attr("y1", b1[1])
    .attr("x2", ix + INSET.w / 2).attr("y2", iy);

  svg.append("rect").attr("class", "inset-bg")
    .attr("x", ix).attr("y", iy).attr("width", INSET.w).attr("height", INSET.h);
  svg.append("rect").attr("class", "water")
    .attr("x", ix).attr("y", iy + ITOP).attr("width", INSET.w).attr("height", INSET.h - ITOP);
  svg.append("clipPath").attr("id", "inset-clip").append("rect")
    .attr("x", ix).attr("y", iy + ITOP).attr("width", INSET.w).attr("height", INSET.h - ITOP);
  const ig = svg.append("g").attr("clip-path", "url(#inset-clip)");
  drawLayers(ig, iproj, { labels: false, inset: true });
  svg.append("rect").attr("class", "inset-frame")
    .attr("x", ix).attr("y", iy).attr("width", INSET.w).attr("height", INSET.h);
  svg.append("text").attr("class", "inset-title").attr("x", ix + 10).attr("y", iy + 18).text(INSET.title);

  // map frame outline
  svg.append("rect").attr("x", mapX).attr("y", mapTop).attr("width", mapW).attr("height", mapH)
    .attr("fill", "none").attr("stroke", "#cdd6d9").attr("stroke-width", 1);

  drawChrome();
  finishRender();
}

// Legend + source line + GEM logo
function drawChrome() {
  const items = CATEGORY_STYLE.map((c) => ({ ...c, kind: "line" }))
    .concat([{ label: CONTEXT_STYLE.label, color: CONTEXT_STYLE.color, kind: "context" }])
    .concat(Object.values(TERMINAL_STYLE).map((t) => ({ ...t, kind: "point" })));

  const SWATCH_W = 40, TEXT_X = 50, ROW = 24;
  const left = mapX + 22, top = mapBottom - 20 - (items.length - 1) * ROW - 16;
  const lg = svg.append("g").attr("class", "legend");
  const labels = [];
  items.forEach((c, i) => {
    const y = i * ROW;
    if (c.kind === "point") {
      lg.append("circle").attr("class", "terminal").attr("cx", SWATCH_W / 2).attr("cy", y).attr("r", 6)
        .attr("fill", c.fill).attr("stroke", c.stroke);
    } else {
      lg.append("line")
        .attr("class", c.kind === "context" ? "context" : `pipe--${c.key}`)
        .attr("x1", 0).attr("x2", SWATCH_W).attr("y1", y).attr("y2", y)
        .attr("stroke", c.color).attr("stroke-dasharray", c.dash || null).attr("stroke-linecap", "round");
    }
    labels.push(lg.append("text").attr("x", TEXT_X).attr("y", y + 5).text(c.label));
  });
  const blockW = TEXT_X + Math.max(...labels.map((t) => t.node().getComputedTextLength()));
  lg.insert("rect", ":first-child").attr("class", "legend-bg")
    .attr("x", -14).attr("y", -18).attr("width", blockW + 28)
    .attr("height", (items.length - 1) * ROW + 32).attr("rx", 6);
  lg.attr("transform", `translate(${left}, ${top})`);

  const LOGO_VB_W = 1080, LOGO_VB_H = 488.11, logoH = 40;
  const logoScale = logoH / LOGO_VB_H, logoW = LOGO_VB_W * logoScale;
  const src = svg.append("text").attr("class", "fig-source").attr("x", mapX).attr("y", footerTop + 20);
  wrapText(src, TEXT.source, mapW - logoW - 30, 20);
  svg.append("g")
    .attr("transform", `translate(${Wfig - PAD - logoW},${footerTop + 4}) scale(${logoScale})`)
    .html(LOGO_PATHS);
}

// ---- Tooltips ----
function showLineTip(e, p) {
  tooltip.style("display", "block").html(
    `<b>${p.name}${p.segment ? " (" + p.segment + ")" : ""}</b><br>` +
      `<span class="meta">${p.status}${p.capacity_bcmy ? " · " + p.capacity_bcmy + " bcm/y" : ""}</span><br>` +
      `${p.terminal ? "Linked terminal: " + p.terminal : "No named terminal"}`,
  );
  moveTip(e);
}
function showPointTip(e, d) {
  tooltip.style("display", "block").html(
    `<b>${d.name}</b><br><span class="meta">${d.status} (units: ${d.units})</span>`,
  );
  moveTip(e);
}
function moveTip(e) {
  tooltip.style("left", e.pageX + 14 + "px").style("top", e.pageY + 12 + "px");
}
function hideTip() {
  tooltip.style("display", "none");
}

// ---- Export (SVG + PNG) ----
const NS = "http://www.w3.org/2000/svg";
const OUT_NAME = "GGIT-US-LNG-pipelines-2026-11";
let PAGE_CSS = "";

function serializeSVG() {
  const clone = document.querySelector("#map svg").cloneNode(true);
  clone.setAttribute("xmlns", NS);
  clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
  clone.setAttribute("width", Wfig);
  clone.setAttribute("height", Hfig);
  const style = document.createElementNS(NS, "style");
  style.textContent = PAGE_CSS;
  clone.insertBefore(style, clone.firstChild);
  return '<?xml version="1.0" encoding="UTF-8"?>\n' + new XMLSerializer().serializeToString(clone);
}

function triggerDownload(blob, name) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    URL.revokeObjectURL(a.href);
    a.remove();
  }, 0);
}

function downloadSVG() {
  triggerDownload(new Blob([serializeSVG()], { type: "image/svg+xml;charset=utf-8" }), OUT_NAME + ".svg");
}

function downloadPNG(scale) {
  const url = URL.createObjectURL(new Blob([serializeSVG()], { type: "image/svg+xml;charset=utf-8" }));
  const img = new Image();
  img.onload = () => {
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(Wfig * scale);
    canvas.height = Math.round(Hfig * scale);
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    URL.revokeObjectURL(url);
    canvas.toBlob((b) => triggerDownload(b, OUT_NAME + ".png"));
  };
  img.onerror = () => {
    URL.revokeObjectURL(url);
    alert("PNG export failed to rasterize the SVG.");
  };
  img.src = url;
}

d3.text("style.css").then((css) => { PAGE_CSS = css; }).catch(() => {});
document.getElementById("dl-svg").onclick = downloadSVG;
document.getElementById("dl-png").onclick = () => downloadPNG(+document.getElementById("png-scale").value);

function finishRender() {
  if (EXPORT_PARAM) {
    const tb = document.querySelector(".toolbar");
    if (tb) tb.style.display = "none";
    const wrap = document.getElementById("wrap");
    if (wrap) {
      wrap.style.padding = "0";
      wrap.style.maxWidth = "none";
    }
    const s = document.querySelector("#map svg");
    if (s) {
      s.style.width = Wfig + "px";
      s.style.height = Hfig + "px";
    }
  }
  if (EXPORT_PARAM === "svg") {
    const emit = () => {
      const pre = document.createElement("pre");
      pre.id = "export-out";
      pre.textContent = serializeSVG();
      document.body.appendChild(pre);
      document.body.setAttribute("data-rendered", "1");
    };
    if (PAGE_CSS) emit();
    else d3.text("style.css").then((css) => { PAGE_CSS = css; }).catch(() => {}).then(emit);
    return;
  }
  document.body.setAttribute("data-rendered", "1");
}
