/* GEM figure kit: the parts every GEM map figure shares.
 *
 * A figure is ONE svg holding the title, subtitle, map, legend, source, note and GEM logo, laid out to GEM's data visualization style guide, so each exported file is complete on its own. This file draws the frame around the map and gives helpers for the usual map layers. Each figure's own map.js keeps what is specific to it: the text, the projection, the map window, label positions and which layers to draw.
 *
 * Load order in a figure's index.html: d3, topojson-client, this file, then map.js. Everything here hangs off one global, GEM.
 *
 *   GEM.ready({ world, usStates })   load style tokens, fonts, logo and basemaps; resolves to { tokens, world, usStates }
 *   GEM.figure({ text, mapH, outName })   draw the header and footer; returns the figure object:
 *       fig.svg, fig.mapX, fig.mapW, fig.mapH, fig.mapTop, fig.mapBottom, fig.W, fig.H
 *       fig.frame()                  water + clip for the map area; returns the group to draw into
 *       fig.clipBox(x, y, w, h, id)  the same for any box (an inset)
 *       fig.fit(projection, window)  fit a d3 projection to the map area
 *       fig.legend(items, opts)      legend panel in a corner of the map
 *       fig.finish()                 map outline, logo, export buttons; call last
 *   GEM.fit(projection, extent, window)   fit a projection to any pixel box
 *   GEM.layers.*                     basemap, labels, context, lines, points, places
 *   GEM.tip.show(event, html) / GEM.tip.hide()
 *   GEM.colors                       shortcut to the palette in tokens.json, set once ready() resolves
 *
 * Style values come from ../tokens.json. Don't hard-code a GEM color or size here or in a map.js; add it to tokens.json and read it.
 */
const GEM = (() => {
  const SHARED = new URL(".", document.currentScript.src).href; // the folder this file is in
  const TOKENS_URL = new URL("../tokens.json", SHARED).href;
  const WORLD_URL = SHARED + "vendor/world-atlas-2.0.2-countries-50m.json";
  const US_STATES_URL = SHARED + "vendor/us-atlas-3.0.1-states-10m.json";
  const LOGO_URL = SHARED + "assets/gem-logo.svg";
  const NS = "http://www.w3.org/2000/svg";
  const EXPORT_PARAM = new URLSearchParams(location.search).get("export");

  // Header and footer baselines and line heights, in px. They follow the token sizes: 34 is 28 px at 1.2, 26 is 18 px at 1.45, 17 is 14 px at 1.2.
  const TITLE_TOP = 46,
    TITLE_LH = 34,
    SUB_LH = 26,
    NOTE_LH = 17,
    NOTE_GAP = 23,
    FOOT_BASELINE = 11; // first footer baseline sits this far below the section gap

  let TOKENS = null,
    PAGE_CSS = "",
    LOGO = { paths: [], w: 1080, h: 488.11 },
    CURRENT = null;
  const api = { colors: null, tokens: null };

  // ---- tokens -> CSS variables ----
  function tokenCss(t) {
    const font = (name) => `"${name}", sans-serif`;
    const vars = {
      "--gem-text": t.text.color,
      "--gem-font-header": font(t.fonts.header),
      "--gem-font-body": font(t.fonts.body),
      "--gem-size-title": t.text.title.size + "px",
      "--gem-size-subtitle": t.text.subtitle.size + "px",
      "--gem-size-body": t.text.body.size + "px",
      "--gem-size-footer": t.text.footer.size + "px",
      "--gem-water": t.map.water,
      "--gem-land": t.map.land,
      "--gem-border": t.map.border,
      "--gem-border-opacity": t.map.countryBorderOpacity,
      "--gem-subnational-opacity": t.map.subnationalBorderOpacity,
      "--gem-max-width": t.layout.maxWidth + "px",
    };
    return ":root {\n" + Object.entries(vars).map(([k, v]) => `  ${k}: ${v};`).join("\n") + "\n}\n";
  }

  function fontsLoaded(t) {
    if (!document.fonts || !document.fonts.load) return Promise.resolve();
    const h = `'${t.fonts.header}'`, b = `'${t.fonts.body}'`;
    const specs = [`400 18px ${h}`, `600 16px ${h}`, `700 28px ${h}`, `400 16px ${b}`, `500 20px ${b}`, `600 16px ${b}`];
    const loads = Promise.all(specs.map((s) => document.fonts.load(s))).then(() => document.fonts.ready);
    const timeout = new Promise((res) => setTimeout(res, 8000));
    return Promise.race([loads, timeout]);
  }

  function parseLogo(svgText) {
    if (!svgText) return;
    const vb = svgText.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
    if (vb) { LOGO.w = +vb[1]; LOGO.h = +vb[2]; }
    LOGO.paths = [...svgText.matchAll(/<path\b[^>]*?\sd="([^"]+)"/g)].map((m) => m[1]);
  }

  // Loads everything a figure needs before drawing. Basemaps are optional so a figure only pays for what it uses.
  async function ready({ world = true, usStates = false } = {}) {
    TOKENS = await d3.json(TOKENS_URL);
    api.tokens = TOKENS;
    api.colors = { ...TOKENS.brand, ...TOKENS.categorical, ...TOKENS.categoricalExtended, background: TOKENS.map.background, text: TOKENS.text.color };
    const tokenStyle = tokenCss(TOKENS);
    const el = document.createElement("style");
    el.textContent = tokenStyle;
    document.head.appendChild(el);

    const sheets = [...document.querySelectorAll('link[rel="stylesheet"]')].map((l) => d3.text(l.href).catch(() => ""));
    const [css, logoSvg, worldTopo, statesTopo] = await Promise.all([
      Promise.all(sheets),
      d3.text(LOGO_URL).catch(() => ""),
      world ? d3.json(WORLD_URL) : null,
      usStates ? d3.json(US_STATES_URL) : null,
    ]);
    PAGE_CSS = tokenStyle + css.join("\n"); // written into the exported SVG so it stands alone
    parseLogo(logoSvg);
    await fontsLoaded(TOKENS);
    return { tokens: TOKENS, world: worldTopo, usStates: statesTopo };
  }

  // ---- text and geometry helpers ----
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

  // Sampled edges of a lon/lat box, so fitting a conic projection sees the curved parallels.
  function boxOutline({ lon0, lon1, lat0, lat1 }, n = 20) {
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

  // Fits `projection` so the lon/lat `window` is contained in the pixel box `extent` ([[x0, y0], [x1, y1]]). Spare room shows real geography. Paths are then cut off `clipPad` px outside the box, which keeps the rest of the world out of the exported SVG.
  function fit(projection, extent, window, clipPad = 20) {
    projection.fitExtent(extent, boxOutline(window));
    if (clipPad != null) {
      projection.clipExtent([
        [extent[0][0] - clipPad, extent[0][1] - clipPad],
        [extent[1][0] + clipPad, extent[1][1] + clipPad],
      ]);
    }
    return projection;
  }

  // ---- the figure frame ----
  function figure({ text, mapH, outName, width, pad, container = "#map" }) {
    const L = TOKENS.layout;
    const W = width ?? L.maxWidth,
      PAD = pad ?? L.pad;
    const mapX = PAD,
      mapW = W - 2 * PAD;
    const LOGO_H = L.logoHeight,
      LOGO_W = (LOGO.w * LOGO_H) / LOGO.h;

    const svg = d3.select(container).append("svg").attr("preserveAspectRatio", "xMidYMid meet");
    const bg = svg.append("rect").attr("x", 0).attr("y", 0).attr("width", W).attr("fill", "#ffffff");

    // header: title, then the subtitle 8 px below it, then one section gap to the map
    const title = svg.append("text").attr("class", "fig-title").attr("x", mapX).attr("y", TITLE_TOP);
    const titleLines = wrapText(title, text.title, mapW, TITLE_LH);
    let mapTop = TITLE_TOP + (titleLines - 1) * TITLE_LH;
    if (text.subtitle) {
      const subTop = mapTop + SUB_LH + L.titleToSubtitle;
      const subtitle = svg.append("text").attr("class", "fig-subtitle").attr("x", mapX).attr("y", subTop);
      mapTop = subTop + (wrapText(subtitle, text.subtitle, mapW, SUB_LH) - 1) * SUB_LH;
    }
    mapTop += L.sectionGap;
    const mapBottom = mapTop + mapH;

    // footer: source first, note below it; the text stops short of the logo
    const textW = mapW - LOGO_W - 30;
    let y = mapBottom + L.sectionGap + FOOT_BASELINE;
    let textBottom = mapBottom;
    [["fig-source", text.source], ["fig-note", text.note]].forEach(([cls, str]) => {
      if (!str) return;
      const t = svg.append("text").attr("class", cls).attr("x", mapX).attr("y", y);
      const n = wrapText(t, str, textW, NOTE_LH);
      textBottom = y + (n - 1) * NOTE_LH + 4;
      y += (n - 1) * NOTE_LH + NOTE_GAP;
    });
    // The logo's bottom lines up with the last line of footer text.
    const logoTop = Math.max(mapBottom + L.sectionGap, textBottom - LOGO_H);
    const H = logoTop + LOGO_H + L.logoMargin;
    svg.attr("viewBox", `0 0 ${W} ${H}`);
    bg.attr("height", H);

    const fig = { svg, W, H, PAD, mapX, mapW, mapH, mapTop, mapBottom, outName };

    fig.clipBox = (x, y, w, h, id) => {
      svg.append("rect").attr("class", "water").attr("x", x).attr("y", y).attr("width", w).attr("height", h);
      svg.append("clipPath").attr("id", id).append("rect").attr("x", x).attr("y", y).attr("width", w).attr("height", h);
      return svg.append("g").attr("clip-path", `url(#${id})`);
    };
    fig.frame = () => fig.clipBox(mapX, mapTop, mapW, mapH, "frame-clip");
    fig.fit = (projection, window, clipPad) =>
      fit(projection, [[mapX, mapTop], [mapX + mapW, mapBottom]], window, clipPad);

    // Legend panel in a corner of the map. Items are { kind: "line", label, color, dash, cls } or { kind: "point", label, fill, stroke }; `cls` is the CSS class that sets a line's width.
    fig.legend = (items, { corner = "bottom-left", margin = 10 } = {}) => {
      const ROW = 24, PAD_X = 14, PAD_TOP = 18, PAD_BOTTOM = 14, GAP = 10;
      // A line sample fits exactly three dashes of the dashed pattern, so no partial fourth dash shows.
      const dashed = items.find((i) => i.dash);
      const [DASH, DGAP] = dashed ? dashed.dash.split(",").map(Number) : [7, 6];
      const SWATCH_W = 3 * DASH + 2 * DGAP, TEXT_X = SWATCH_W + GAP;
      const lg = svg.append("g").attr("class", "legend");
      const labels = [];
      items.forEach((c, i) => {
        const yy = i * ROW;
        if (c.kind === "point") {
          lg.append("circle").attr("class", "terminal").attr("cx", SWATCH_W / 2).attr("cy", yy).attr("r", 6)
            .attr("fill", c.fill).attr("stroke", c.stroke);
        } else {
          lg.append("line").attr("class", c.cls)
            .attr("x1", 0).attr("x2", SWATCH_W).attr("y1", yy).attr("y2", yy)
            .attr("stroke", c.color).attr("stroke-dasharray", c.dash || null).attr("stroke-linecap", "round");
        }
        labels.push(lg.append("text").attr("x", TEXT_X).attr("y", yy + 5).text(c.label));
      });
      const blockW = TEXT_X + Math.max(...labels.map((t) => t.node().getComputedTextLength()));
      const rows = (items.length - 1) * ROW;
      lg.insert("rect", ":first-child").attr("class", "legend-bg")
        .attr("x", -PAD_X).attr("y", -PAD_TOP).attr("width", blockW + 2 * PAD_X)
        .attr("height", rows + PAD_TOP + PAD_BOTTOM).attr("rx", 6);
      const left = corner.endsWith("left") ? mapX + margin + PAD_X : mapX + mapW - margin - PAD_X - blockW;
      const top = corner.startsWith("top") ? mapTop + margin + PAD_TOP : mapBottom - margin - PAD_BOTTOM - rows;
      lg.attr("transform", `translate(${left}, ${top})`);
      return lg;
    };

    fig.finish = () => {
      svg.append("rect").attr("class", "map-outline")
        .attr("x", mapX).attr("y", mapTop).attr("width", mapW).attr("height", mapH);
      svg.append("g")
        .attr("transform", `translate(${W - PAD - LOGO_W},${logoTop}) scale(${LOGO_H / LOGO.h})`)
        .html(LOGO.paths.map((d) => `<path fill="${L.logoColor}" d="${d}"></path>`).join(""));
      finishRender();
    };

    CURRENT = fig;
    return fig;
  }

  // Runs `draw` with the projection's cut-off (see fit) switched off, so shapes come out whole. Dashed lines need this: cutting one moves where its dashes start, so the pattern would shift whenever the map window changed.
  function whole(path, draw) {
    const projection = path.projection();
    const cut = projection.clipExtent ? projection.clipExtent() : null;
    if (cut) projection.clipExtent(null);
    const out = draw();
    if (cut) projection.clipExtent(cut);
    return out;
  }

  // ---- map layers ----
  const layers = {
    // Land, then sub-national borders, then country borders. `usStates` is optional.
    basemap(g, path, { world, usStates } = {}) {
      if (world) {
        g.append("g").selectAll("path").data(topojson.feature(world, world.objects.countries).features).join("path")
          .attr("class", "country").attr("d", path);
      }
      if (usStates) {
        const mesh = topojson.mesh(usStates, usStates.objects.states, (a, b) => a !== b);
        g.append("path").attr("class", "state-border").attr("d", whole(path, () => path(mesh)));
      }
      if (world) {
        g.append("path").datum(topojson.mesh(world, world.objects.countries)).attr("class", "border").attr("d", path);
      }
    },

    // Hand-placed region names. rows: [name, lon, lat, cssClass], class "country-label" or "state-label".
    labels(g, proj, rows) {
      g.append("g").selectAll("text").data(rows).join("text")
        .attr("class", (d) => d[3])
        .attr("transform", (d) => `translate(${proj([d[1], d[2]])})`)
        .text((d) => d[0]);
    },

    // Background network in one color, no hover.
    context(g, path, features, color) {
      g.append("g").selectAll("path").data(features).join("path")
        .attr("class", "context").attr("d", path).attr("stroke", color ?? TOKENS.map.background);
    },

    // Highlighted lines. `styles` is a list of { cat, key, color, dash }; `cat` must match a feature's properties.category and `key` picks the .pipe--<key> width class. The first style in the list is drawn on top.
    lines(g, path, features, styles, { tip } = {}) {
      const rank = new Map(styles.map((s, i) => [s.cat, -i]));
      const byCat = new Map(styles.map((s) => [s.cat, s]));
      const layer = g.append("g");
      whole(path, () => features.slice()
        .sort((a, b) => (rank.get(a.properties.category) ?? 0) - (rank.get(b.properties.category) ?? 0))
        .forEach((f) => {
          const s = byCat.get(f.properties.category);
          if (!s) return;
          const grp = layer.append("g");
          grp.append("path").attr("class", "pipe-hit").attr("d", path(f));
          grp.append("path").attr("class", `pipe pipe--${s.key}`).attr("d", path(f))
            .attr("stroke", s.color).attr("stroke-dasharray", s.dash);
          if (tip) grp.on("mousemove", (e) => api.tip.show(e, tip(f.properties))).on("mouseleave", api.tip.hide);
        }));
      return layer;
    },

    // Labeled dots. rows need lon, lat, label and status. `styles` maps a status to { fill, stroke }; the first status listed is drawn on top. `labelPos` maps a label to [dx, dy, text-anchor]; the default is right of the dot.
    points(g, proj, rows, { styles, labelPos = {}, groupClass = null, r = 6, tip } = {}) {
      const rank = new Map(Object.keys(styles).map((k, i) => [k, -i]));
      const sorted = rows.slice().sort((a, b) => (rank.get(a.status) ?? 0) - (rank.get(b.status) ?? 0));
      const tg = g.append("g").attr("class", groupClass)
        .selectAll("g").data(sorted).join("g")
        .attr("transform", (d) => `translate(${proj([d.lon, d.lat])})`);
      if (tip) tg.on("mousemove", (e, d) => api.tip.show(e, tip(d))).on("mouseleave", api.tip.hide);
      tg.append("circle").attr("class", "terminal").attr("r", r)
        .attr("fill", (d) => styles[d.status].fill)
        .attr("stroke", (d) => styles[d.status].stroke);
      const pos = (d) => labelPos[d.label] || [9, 0, "start"];
      tg.append("text").attr("class", "terminal-label")
        .attr("x", (d) => pos(d)[0]).attr("y", (d) => pos(d)[1]).attr("text-anchor", (d) => pos(d)[2])
        .text((d) => d.label);
      return tg;
    },

    // Small place names. rows: [name, lon, lat, dx, dy, text-anchor, showDot].
    places(g, proj, rows) {
      const pg = g.append("g").selectAll("g").data(rows).join("g")
        .attr("transform", (d) => `translate(${proj([d[1], d[2]])})`);
      pg.filter((d) => d[6]).append("circle").attr("class", "place-dot").attr("r", 2.5);
      pg.append("text").attr("class", "place-label").attr("x", (d) => d[3]).attr("y", (d) => d[4])
        .attr("text-anchor", (d) => d[5]).text((d) => d[0]);
    },
  };

  // ---- tooltip (screen only) ----
  api.tip = {
    show(e, html) {
      d3.select(".tooltip").style("display", "block").html(html)
        .style("left", e.pageX + 14 + "px").style("top", e.pageY + 12 + "px");
    },
    hide() {
      d3.select(".tooltip").style("display", "none");
    },
  };

  // ---- export (SVG + PNG) ----
  function serializeSVG() {
    const clone = CURRENT.svg.node().cloneNode(true);
    clone.setAttribute("xmlns", NS);
    clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
    clone.setAttribute("width", CURRENT.W);
    clone.setAttribute("height", CURRENT.H);
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
    triggerDownload(new Blob([serializeSVG()], { type: "image/svg+xml;charset=utf-8" }), CURRENT.outName + ".svg");
  }

  function downloadPNG(scale) {
    const url = URL.createObjectURL(new Blob([serializeSVG()], { type: "image/svg+xml;charset=utf-8" }));
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(CURRENT.W * scale);
      canvas.height = Math.round(CURRENT.H * scale);
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      canvas.toBlob((b) => triggerDownload(b, CURRENT.outName + ".png"));
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      alert("PNG export failed to rasterize the SVG.");
    };
    img.src = url;
  }

  // Wires the Download buttons. With ?export=svg or ?export=png in the URL (what ../export.py opens) it also strips the page down to the bare figure and marks it rendered.
  function finishRender() {
    const svgBtn = document.getElementById("dl-svg"),
      pngBtn = document.getElementById("dl-png");
    if (svgBtn) svgBtn.onclick = downloadSVG;
    if (pngBtn) pngBtn.onclick = () => downloadPNG(+document.getElementById("png-scale").value);

    if (EXPORT_PARAM) {
      const tb = document.querySelector(".toolbar");
      if (tb) tb.style.display = "none";
      const wrap = document.getElementById("wrap");
      if (wrap) {
        wrap.style.padding = "0";
        wrap.style.maxWidth = "none";
      }
      const s = CURRENT.svg.node();
      s.style.width = CURRENT.W + "px";
      s.style.height = CURRENT.H + "px";
    }
    if (EXPORT_PARAM === "svg") {
      const pre = document.createElement("pre");
      pre.id = "export-out";
      pre.setAttribute("data-name", CURRENT.outName);
      pre.textContent = serializeSVG();
      document.body.appendChild(pre);
    }
    document.body.setAttribute("data-rendered", "1");
  }

  return Object.assign(api, { ready, figure, fit, boxOutline, wrapText, layers });
})();
