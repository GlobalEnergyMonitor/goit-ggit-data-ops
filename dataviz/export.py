"""
Export a GEM figure to PNG and SVG with headless Chrome, or serve it for live editing.

A figure is a folder holding index.html and map.js that uses the shared kit in dataviz/shared/. The page fetches its data, which a browser blocks over file://, so this script serves the repo on a throwaway localhost port and points headless Chrome at the figure. Only the figure folder and dataviz/ are served.

Usage, from anywhere in the repo:
  python dataviz/export.py path/to/figure            # writes <name>.svg and <name>.png into the figure folder
  python dataviz/export.py path/to/figure --scale 3  # PNG at 3x instead of the default 2x
  python dataviz/export.py path/to/figure --serve    # dev server only; open the printed URL, Ctrl-C to stop

<name> is the outName set in the figure's map.js. No Chrome? Use --serve and the Download buttons on the page.
"""

import argparse
import functools
import html as htmllib
import http.server
import os
import pathlib
import re
import subprocess
import threading

DATAVIZ = pathlib.Path(__file__).resolve().parent
REPO = DATAVIZ.parent

# Fallback size only. The real size is read from the exported SVG, because the height depends on how the title and footer wrap.
FIG_W, FIG_H = 800, 800


def find_chrome():
    env = os.environ.get("CHROME")
    candidates = [env] if env else []
    candidates += [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if c and pathlib.Path(c).exists():
            return c
    return None


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves the repo, but only the figure folder and dataviz/, and never lets the browser cache."""

    allowed = ()

    def translate_path(self, path):
        local = pathlib.Path(super().translate_path(path)).resolve()
        if any(local == a or a in local.parents for a in self.allowed):
            return str(local)
        return str(REPO / "__not_served__")

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


def serve(figure, port=0):
    """Start the server in a background thread. Returns (httpd, url of the figure page)."""
    handler = functools.partial(Handler, directory=str(REPO))
    Handler.allowed = (figure, DATAVIZ)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    rel = figure.relative_to(REPO).as_posix()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}/{rel}/index.html"


def export_assets(figure, scale=2):
    chrome = find_chrome()
    if not chrome:
        raise SystemExit("No Chrome, Chromium or Edge found. Set CHROME=/path/to/browser, or run with --serve and use the Download buttons on the page.")

    httpd, url = serve(figure)
    common = [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--virtual-time-budget=12000"]
    try:
        # SVG first. The page writes the finished SVG into <pre id="export-out" data-name="...">. Reading it back also gives the output name and the real figure size for the screenshot.
        dom = subprocess.run(common + ["--dump-dom", url + "?export=svg"], check=True, capture_output=True, text=True).stdout
        m = re.search(r'<pre id="export-out" data-name="([^"]+)">(.*?)</pre>', dom, re.S)
        if not m:
            raise SystemExit("The page did not finish drawing, so nothing was exported. Run with --serve, open the URL and check the browser console for errors.")
        name, svg_str = htmllib.unescape(m.group(1)), htmllib.unescape(m.group(2))
        svg_path = figure / f"{name}.svg"
        svg_path.write_text(svg_str, encoding="utf-8")
        print(f"wrote {svg_path} ({svg_path.stat().st_size / 1e6:.1f} MB)")

        fig_w, fig_h = FIG_W, FIG_H
        dim = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_str)
        if dim:
            fig_w, fig_h = round(float(dim.group(1))), round(float(dim.group(2)))

        # PNG: a screenshot sized exactly to the figure. ?export=png hides the toolbar and page padding.
        png_path = figure / f"{name}.png"
        subprocess.run(
            common + [f"--force-device-scale-factor={scale}", f"--window-size={fig_w},{fig_h}", f"--screenshot={png_path}", url + "?export=png"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        print(f"wrote {png_path} ({fig_w * scale} x {fig_h * scale} px)")
    finally:
        httpd.shutdown()


def main():
    ap = argparse.ArgumentParser(description="Export a GEM figure folder to PNG and SVG.")
    ap.add_argument("figure", help="path to the figure folder (the one holding index.html)")
    ap.add_argument("--scale", type=int, default=2, help="PNG pixels per figure pixel (default 2, so an 800 px figure is 1600 px wide)")
    ap.add_argument("--serve", action="store_true", help="run the dev server and wait, for viewing and editing live")
    args = ap.parse_args()

    figure = pathlib.Path(args.figure).resolve()
    if not (figure / "index.html").exists():
        raise SystemExit(f"No index.html in {figure}")
    if REPO not in figure.parents:
        raise SystemExit(f"{figure} is outside this repo, so the page could not reach dataviz/shared/.")

    if args.serve:
        httpd, url = serve(figure)
        print(f"serving {figure}\n  {url}\nCtrl-C to stop.")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            httpd.shutdown()
        return

    export_assets(figure, scale=args.scale)


if __name__ == "__main__":
    main()
