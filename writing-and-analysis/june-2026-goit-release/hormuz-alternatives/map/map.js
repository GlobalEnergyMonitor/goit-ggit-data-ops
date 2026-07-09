/* Strait of Hormuz crude-oil alternatives — GOIT June 2026.
 *
 * The WHOLE figure is one SVG (title, subtitle, map, legend, source line, GEM
 * logo) laid out to the GEM chart-anatomy spec, so the exported PNG and SVG are
 * each a complete, self-contained image that drops into the report next to the
 * existing Flourish figures.
 *
 * Data is fetched from data/ at load time (run a local server — see README /
 * export.py — because file:// blocks fetch). d3 + topojson + the country
 * basemap come from CDN, so viewing/exporting needs internet.
 *
 * What lives where:
 *   - Route colours / dashes           -> CATEGORY_STYLE below
 *   - Line widths (map + legend)       -> --pipe-w-* vars in style.css
 *   - Faint grey context-layer style   -> CONTEXT_STYLE below + style.css
 *   - Figure size                      -> Wfig / Hfig + layout block below
 *   - Map window (lon/lat)             -> FRAME below
 *   - Title / subtitle / source text   -> the .text("...") calls below
 *   - Marker positions / labels        -> data/flourish-hormuz-points.csv
 *   - Fonts / palette                  -> style.css
 */

// ---- Style config (viz decisions — edit here, not in the data) ----
// Fossil sequential 4-tone (darker = more active / further along) for the live
// oil lines, GEM grey for the retired line. Per the GEM style guide.
// `cat` MUST match the category value in the data (flourish-hormuz-lines.geojson);
// `label` is the free-text legend display — rename it freely without breaking colors.
// `key` maps to the `.pipe--<key>` CSS class that sets the LINE WIDTH (same class
// on the map line and its legend swatch, so they always match). To change a
// width, edit the matching --pipe-w-* var in style.css, not here.
const CATEGORY_STYLE = [
  {
    cat: "Operating bypass routes",
    label: "Operating bypass routes",
    key: "operating",
    color: "#5d0e1e",
    dash: null,
  },
  {
    cat: "Kirkuk–Ceyhan pipeline (reopened 2026)",
    label: "Kirkuk–Ceyhan pipeline (reopened 2026)",
    key: "kirkuk",
    color: "#a93841",
    dash: null,
  },
  {
    cat: "Mothballed lines",
    label: "Mothballed lines",
    key: "mothballed",
    color: "#df8182",
    dash: "9,9",
  },
  {
    cat: "Retired routes",
    label: "Retired routes",
    key: "retired",
    color: "#6e8c91",
    dash: "9,9",
  },
];
// The faint grey context network (all operating oil/NGL pipelines in the frame).
// Width comes from the `.context` CSS rule (--pipe-w-context).
const CONTEXT_STYLE = {
  label: "Operating oil pipelines",
  color: "#becccf",
};

// Country labels — placed by hand in open areas so they don't collide with the
// cities or pipelines. [name, lon, lat]; edit/add/move here.
const COUNTRY_LABELS = [
  ["SAUDI ARABIA", 45.0, 22.5],
  ["IRAQ", 42.0, 32.5],
  ["IRAN", 53.5, 31.5],
  ["TÜRKIYE", 37, 39],
  ["SYRIA", 38.7, 35.5],
  ["U.A.E.", 54.25, 23.3],
];

// Cities whose label reads better to the LEFT of the dot (right-aligned) —
// e.g. near a frame edge or a busy cluster. Everything else labels to the right.
const LABEL_LEFT = new Set(["Abu Dhabi", "Habshan", "Yanbu", "Sidon"]);

// ---- Figure layout (GEM chart anatomy) ----
// Width is fixed; the header (title + subtitle) wraps to the figure width, so
// its height — and therefore the map's top edge and the total figure height —
// are computed at render time in layoutHeader(). export.py reads the final
// height back out of the exported SVG, so it stays in sync automatically.
const Wfig = 1000,
  PAD = 28;
const mapX = PAD,
  mapW = Wfig - 2 * PAD; // 944
// Geographic frame extent (lon/lat). The map aspect — and therefore the total
// figure height — follows latSpan:lonSpan. The latitude span is set so the
// figure aspect (~1000:931) matches the companion Flourish bar chart it sits
// beside (1588:1478).
const LON0 = 34,
  LON1 = 60,
  LAT0 = 19.65,
  LAT1 = 40.35;
const mapH = Math.round((mapW * (LAT1 - LAT0)) / (LON1 - LON0)); // 752

// Header typography (baselines + line heights, px). The title/subtitle text
// itself lives in the .text() calls in layoutHeader().
const TITLE_TOP = 46, // first title baseline
  TITLE_LH = 34, // title line height
  TITLE_TO_SUB = 30, // last title baseline -> first subtitle baseline
  SUB_LH = 23, // subtitle line height
  SUB_TO_MAP = 16; // last subtitle baseline -> map top edge

// Assigned by layoutHeader() once the header is measured.
let mapTop, mapBottom, footerTop, Hfig;

// Fixed map frame: lon ~34–60E, lat ~19.65–40.35N (see LON0/LON1/LAT0/LAT1).
// Use MultiPoint of the corners (not a Polygon) so fitExtent reads an
// unambiguous bbox — a Polygon ring's winding can make d3 fit the whole globe.
const FRAME = {
  type: "MultiPoint",
  coordinates: [
    [LON0, LAT0],
    [LON1, LAT1],
  ],
};

const styleByCat = new Map(CATEGORY_STYLE.map((c) => [c.cat, c]));
function catStyle(cat) {
  return (
    styleByCat.get(cat) || {
      color: cat && cat.startsWith("Operating") ? "#5d0e1e" : "#6e8c91",
      dash: null,
      key: null, // no `pipe--<key>` class -> falls back to --pipe-w-default
    }
  );
}
// pick dark vs white label text for legibility on a given marker fill
function textOn(bg) {
  return d3.lab(bg).l > 65 ? "#2a2a2a" : "#ffffff";
}

// Greedy word-wrap for an SVG <text>: lays words into <tspan> lines, breaking
// whenever the measured line exceeds maxWidth. The first line sits on the
// element's own y; each later line is offset by lineHeight via dy. Returns the
// number of lines so the caller can lay out whatever follows. (Measuring needs
// the text attached to a rendered SVG with fonts loaded — see fonts.ready gate.)
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
      tspan = textSel
        .append("tspan")
        .attr("x", x)
        .attr("dy", lineHeight)
        .text(w);
      lines += 1;
    }
  });
  return lines + 1;
}

// ---- Load data, then draw ----
const EXPORT_PARAM = new URLSearchParams(location.search).get("export");
const tooltip = d3.select(".tooltip");
const BASEMAP = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json";

let LINES,
  POINTS,
  OPERATING,
  LOGO_PATHS = "";

Promise.all([
  d3.json("data/flourish-hormuz-lines.geojson"),
  d3.csv("data/flourish-hormuz-points.csv", (r) =>
    !r.latitude || !r.longitude
      ? null
      : {
          label: r.label,
          name: r.name,
          type: r.type,
          category: r.category || "",
          color: r.color || "#333333",
          lat: +r.latitude,
          lon: +r.longitude,
        },
  ),
  d3.json("data/operating-context-2026-06.geojson"),
  d3.text("assets/gem-logo-midnight.svg").catch(() => ""),
]).then(([lines, points, operating, logoSvg]) => {
  LINES = lines;
  POINTS = points;
  OPERATING = operating;
  LOGO_PATHS = extractLogoPaths(logoSvg);
  whenFontsLoaded().then(draw);
});

// Wait for the web fonts before drawing — the header wrap and legend width are
// measured with getComputedTextLength, which mis-counts against a fallback font.
// document.fonts.ready is NOT enough: web fonts load lazily (only once text that
// uses them exists), so before draw() there is nothing pending and .ready
// resolves immediately with the faces still unloaded — fine in a warm browser
// where they're cached, but headless Chrome (cold cache) then measures and
// renders with fallback metrics, shifting the wrap, height and glyphs. So force
// each weight/family we actually use to download, and await those explicitly.
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
  // never hang if a face fails to fetch (e.g. offline) — fall back after 8s
  const timeout = new Promise((res) => setTimeout(res, 8000));
  return Promise.race([loads, timeout]);
}

// pull <path d="..."> data out of the logo SVG so it inlines into the figure
// (survives both in-browser canvas PNG and headless-Chrome SVG/PNG export)
function extractLogoPaths(svgText) {
  if (!svgText) return "";
  const ds = [...svgText.matchAll(/<path\b[^>]*?\sd="([^"]+)"/g)].map(
    (m) => m[1],
  );
  return ds.map((d) => `<path fill="#002430" d="${d}"></path>`).join("");
}

let svg, path, g;

// Draw the wrapped title + subtitle and derive the layout that depends on how
// many lines they took: map top edge, footer position, total figure height.
function layoutHeader() {
  const title = svg
    .append("text")
    .attr("class", "fig-title")
    .attr("x", mapX)
    .attr("y", TITLE_TOP);
  const titleLines = wrapText(
    title,
    "What alternatives are there to the Strait of Hormuz?",
    mapW,
    TITLE_LH,
  );

  const subTop = TITLE_TOP + (titleLines - 1) * TITLE_LH + TITLE_TO_SUB;
  const subtitle = svg
    .append("text")
    .attr("class", "fig-subtitle")
    .attr("x", mapX)
    .attr("y", subTop);
  const subLines = wrapText(
    subtitle,
    "Crude oil pipelines in the Middle East, highlighting operating routes that bypass the Strait of Hormuz, as well as unused routes that could be reactivated to do so",
    mapW,
    SUB_LH,
  );

  mapTop = subTop + (subLines - 1) * SUB_LH + SUB_TO_MAP;
  mapBottom = mapTop + mapH;
  footerTop = mapBottom + 18;
  Hfig = footerTop + 46;
}

function draw() {
  svg = d3
    .select("#map")
    .append("svg")
    .attr("preserveAspectRatio", "xMidYMid meet");

  // white background (so the standalone PNG/SVG isn't transparent). Height is
  // set after layoutHeader() knows the final figure height.
  const bg = svg
    .append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", Wfig)
    .attr("fill", "#ffffff");

  // Title + subtitle (baked into the figure). These wrap to the figure width
  // and push the map down by however many lines they take.
  layoutHeader();

  // Now that mapTop / Hfig are known, size the canvas + background.
  svg.attr("viewBox", `0 0 ${Wfig} ${Hfig}`);
  bg.attr("height", Hfig);

  const proj = d3.geoEquirectangular().fitExtent(
    [
      [mapX, mapTop],
      [mapX + mapW, mapTop + mapH],
    ],
    FRAME,
  );
  path = d3.geoPath(proj);

  // Water background (frame rectangle) + clip
  const fx = proj([LON0, LAT1]),
    fx2 = proj([LON1, LAT0]);
  svg
    .append("rect")
    .attr("class", "water")
    .attr("x", fx[0])
    .attr("y", fx[1])
    .attr("width", fx2[0] - fx[0])
    .attr("height", fx2[1] - fx[1]);
  svg
    .append("clipPath")
    .attr("id", "frame-clip")
    .append("rect")
    .attr("x", fx[0])
    .attr("y", fx[1])
    .attr("width", fx2[0] - fx[0])
    .attr("height", fx2[1] - fx[1]);
  // thin frame outline
  svg
    .append("rect")
    .attr("x", fx[0])
    .attr("y", fx[1])
    .attr("width", fx2[0] - fx[0])
    .attr("height", fx2[1] - fx[1])
    .attr("fill", "none")
    .attr("stroke", "#cdd6d9")
    .attr("stroke-width", 1);

  g = svg.append("g").attr("clip-path", "url(#frame-clip)");

  d3.json(BASEMAP)
    .then((world) => {
      const countries = topojson.feature(world, world.objects.countries);
      // full mesh (no a!==b filter) so coastlines are drawn too, not just the
      // interior borders shared between two countries.
      const borders = topojson.mesh(world, world.objects.countries);

      g.append("g")
        .selectAll("path")
        .data(countries.features)
        .join("path")
        .attr("class", "country")
        .attr("d", path);
      g.append("path").datum(borders).attr("class", "border").attr("d", path);
      g.append("path")
        .datum(d3.geoGraticule().step([5, 5]))
        .attr("class", "graticule")
        .attr("d", path);

      drawContext();
      drawPipes();
      drawPoints();
      drawChrome(proj);
      finishRender();
    })
    .catch(() => {
      drawContext();
      drawPipes();
      drawPoints();
      drawChrome(proj);
      finishRender();
    }); // basemap best-effort
}

// faint grey network of all operating oil/NGL pipelines, under the highlights
function drawContext() {
  g.append("g")
    .selectAll("path")
    .data(OPERATING.features)
    .join("path")
    .attr("class", "context")
    .attr("d", path)
    .attr("stroke", CONTEXT_STYLE.color);
}

function drawPipes() {
  const layer = g.append("g");
  // sort so mothballed lines draw on top, then operating, over faint historic.
  // Keys MUST match the data's category values (flourish-hormuz-lines.geojson).
  const order = {
    "Retired routes": 0,
    "Operating bypass routes": 1,
    "Kirkuk–Ceyhan pipeline (reopened 2026)": 2,
    "Mothballed lines": 3,
  };
  const feats = LINES.features
    .slice()
    .sort(
      (a, b) =>
        (order[a.properties.category] || 0) -
        (order[b.properties.category] || 0),
    );

  feats.forEach((f) => {
    const s = catStyle(f.properties.category);
    const grp = layer.append("g");
    grp.append("path").attr("class", "pipe-hit").attr("d", path(f));
    grp
      .append("path")
      .attr("class", s.key ? `pipe pipe--${s.key}` : "pipe")
      .attr("d", path(f))
      .attr("stroke", s.color)
      .attr("stroke-dasharray", s.dash);
    grp
      .on("mousemove", (e) => showLineTip(e, f.properties))
      .on("mouseleave", hideTip);
  });
}

function drawPoints() {
  const layer = g.append("g");
  const terminals = POINTS.filter((p) => p.type === "terminal/city");
  const choke = POINTS.filter((p) => p.type === "chokepoint");

  // country labels first, so cities/markers draw over them
  layer
    .append("g")
    .selectAll("text")
    .data(COUNTRY_LABELS)
    .join("text")
    .attr("class", "country-label")
    .attr("transform", (d) => `translate(${path.projection()([d[1], d[2]])})`)
    .text((d) => d[0]);

  const t = layer
    .append("g")
    .selectAll("g")
    .data(terminals)
    .join("g")
    .attr(
      "transform",
      (d) => `translate(${path.projection()([d.lon, d.lat])})`,
    );
  t.append("circle").attr("class", "terminal").attr("r", 2.6);
  t.append("text")
    .attr("class", "terminal-label")
    .attr("x", (d) => (LABEL_LEFT.has(d.name) ? -5 : 5))
    .attr("y", 0)
    .attr("text-anchor", (d) => (LABEL_LEFT.has(d.name) ? "end" : "start"))
    .text((d) => d.name.toUpperCase());

  const c = layer
    .append("g")
    .selectAll("g")
    .data(choke)
    .join("g")
    .attr(
      "transform",
      (d) => `translate(${path.projection()([d.lon, d.lat])})`,
    );
  c.append("circle").attr("class", "hormuz-dot").attr("r", 9);
  c.append("text")
    .attr("class", "hormuz-label")
    .attr("x", -13)
    .attr("y", 4)
    .attr("text-anchor", "end")
    .text((d) => d.name.toUpperCase());
}

// Legend + source line + GEM logo (everything baked into the SVG)
function drawChrome(proj) {
  // ---- Legend (overlaid top-right of the map, no background) ----
  const legItems = CATEGORY_STYLE.concat([
    {
      label: CONTEXT_STYLE.label,
      color: CONTEXT_STYLE.color,
      dash: null,
      context: true,
    },
  ]);
  // Anchored to the map's top-right corner with a 20px margin on the top and
  // right. The block is right-pinned: we measure the widest label and shift the
  // whole legend left by its total width, so the right edge always sits 20px in
  // from the map edge no matter how long the labels are (long labels grow the
  // block leftward rather than spilling off the right).
  const MARGIN_RIGHT = 30,
    MARGIN_TOP = 35;
  const SWATCH_W = 48, // swatch line length (long enough for 3 dashes of the 9,9 pattern)
    TEXT_X = 58, // label start (swatch + 10px gap)
    ROW = 26; // row pitch
  const right = mapX + mapW - MARGIN_RIGHT;
  const top = mapTop + MARGIN_TOP;
  const lg = svg.append("g").attr("class", "legend");
  const labels = [];
  legItems.forEach((c, i) => {
    const y = i * ROW;
    // same width class as the map line for this category, so swatch == map
    lg.append("line")
      .attr("class", c.context ? "context" : c.key ? `pipe--${c.key}` : "pipe")
      .attr("x1", 0)
      .attr("x2", SWATCH_W)
      .attr("y1", y)
      .attr("y2", y)
      .attr("stroke", c.color)
      .attr("stroke-dasharray", c.dash)
      .attr("stroke-linecap", "round");
    labels.push(
      lg
        .append("text")
        .attr("x", TEXT_X)
        .attr("y", y + 5)
        .text(c.label),
    );
  });
  const maxLabel = Math.max(
    ...labels.map((t) => t.node().getComputedTextLength()),
  );
  const blockW = TEXT_X + maxLabel;

  // Faint background panel behind the swatches/labels (improves legibility over
  // the map). Inserted first so it sits under the lines + text; its look is set
  // by `.legend-bg` in style.css. Padding is symmetric L/R; rows run y=0..(n-1)*ROW.
  const PAD_X = 14,
    PAD_TOP = 18,
    PAD_BOTTOM = 14;
  lg.insert("rect", ":first-child")
    .attr("class", "legend-bg")
    .attr("x", -PAD_X)
    .attr("y", -PAD_TOP)
    .attr("width", blockW + PAD_X * 2)
    .attr("height", (legItems.length - 1) * ROW + PAD_TOP + PAD_BOTTOM)
    .attr("rx", 6);

  lg.attr("transform", `translate(${right - blockW}, ${top})`);

  // ---- Source line ----
  svg
    .append("text")
    .attr("class", "fig-source")
    .attr("x", mapX)
    .attr("y", footerTop + 27)
    .text(
      "Source: Global Energy Monitor, Global Oil Infrastructure Tracker, June 2026",
    );

  // ---- GEM logo (bottom-right, 40px tall) ----
  const LOGO_VB_W = 1080,
    LOGO_VB_H = 488.11,
    logoH = 40;
  const logoScale = logoH / LOGO_VB_H,
    logoW = LOGO_VB_W * logoScale;
  const logoX = Wfig - PAD - logoW,
    logoY = footerTop + 2;
  svg
    .append("g")
    .attr("transform", `translate(${logoX},${logoY}) scale(${logoScale})`)
    .html(LOGO_PATHS);
}

// ---- Tooltips ----
function showLineTip(e, p) {
  const len = p.length_km
    ? `${Math.round(p.length_km).toLocaleString()} km`
    : "length n/a";
  const route = [p.from, p.to].filter(Boolean).join(" → ");
  tooltip
    .style("display", "block")
    .html(
      `<b>${p.num ? p.num + ". " : ""}${p.name}</b><br>` +
        `<span class="meta">${p.category}${p.status ? " · " + p.status : ""}</span><br>` +
        `${route ? route + "<br>" : ""}` +
        `<span class="meta">${len}</span>`,
    );
  moveTip(e);
}
function showPointTip(e, d) {
  tooltip
    .style("display", "block")
    .html(
      `<b>${d.label}. ${d.name}</b><br><span class="meta">${d.category || d.type}</span>`,
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
let PAGE_CSS = ""; // filled in once style.css is fetched (for self-contained SVG)

function serializeSVG() {
  const clone = document.querySelector("#map svg").cloneNode(true);
  clone.setAttribute("xmlns", NS);
  clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
  clone.setAttribute("width", Wfig);
  clone.setAttribute("height", Hfig);
  const style = document.createElementNS(NS, "style");
  style.textContent = PAGE_CSS;
  clone.insertBefore(style, clone.firstChild);
  return (
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    new XMLSerializer().serializeToString(clone)
  );
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
  triggerDownload(
    new Blob([serializeSVG()], { type: "image/svg+xml;charset=utf-8" }),
    "GOIT-Hormuz-alternative-routes-d3.svg",
  );
}

function downloadPNG(scale) {
  const url = URL.createObjectURL(
    new Blob([serializeSVG()], { type: "image/svg+xml;charset=utf-8" }),
  );
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
    canvas.toBlob((b) =>
      triggerDownload(b, "GOIT-Hormuz-alternative-routes-d3.png"),
    );
  };
  img.onerror = () => {
    URL.revokeObjectURL(url);
    alert("PNG export failed to rasterize the SVG.");
  };
  img.src = url;
}

// Fetch style.css once so serialized SVGs are self-contained, then wire buttons.
d3.text("style.css")
  .then((css) => {
    PAGE_CSS = css;
  })
  .catch(() => {});
document.getElementById("dl-svg").onclick = downloadSVG;
document.getElementById("dl-png").onclick = () =>
  downloadPNG(+document.getElementById("png-scale").value);

// Headless-export hook: ?export strips the toolbar + page padding so the
// screenshot is the figure alone; ?export=svg also dumps the serialized SVG.
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
    // ensure style.css is inlined before serializing the standalone SVG
    const emit = () => {
      const pre = document.createElement("pre");
      pre.id = "export-out";
      pre.textContent = serializeSVG();
      document.body.appendChild(pre);
      document.body.setAttribute("data-rendered", "1");
    };
    if (PAGE_CSS) emit();
    else
      d3.text("style.css")
        .then((css) => {
          PAGE_CSS = css;
        })
        .catch(() => {})
        .then(emit);
    return;
  }
  document.body.setAttribute("data-rendered", "1"); // export.py waits on this
}
