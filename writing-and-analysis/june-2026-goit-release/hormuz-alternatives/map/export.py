"""
Export the Hormuz figure to publication-quality PNG + SVG via headless Chrome.

The figure (index.html + style.css + map.js) fetches its data from data/, which
the browser blocks over file://. So this serves the folder on a throwaway
localhost server and points headless Chrome at it — no global install, no CORS
flags, works the same as the dev server you'd use to view it.

Usage:
  python export.py                 # PNG (3x) + SVG next to this script
  python export.py --scale 2       # PNG at 2x instead
  python export.py --serve         # just run the dev server (Ctrl-C to stop),
                                    #   then open the printed URL to edit live

In-browser alternative: `python export.py --serve`, open the URL, and use the
figure's own Download SVG / Download PNG buttons. No headless Chrome needed.
"""

import argparse
import functools
import http.server
import os
import pathlib
import re
import socketserver
import subprocess
import threading
import html as htmllib

HERE = pathlib.Path(__file__).resolve().parent
PNG = HERE / "GOIT-Hormuz-alternative-routes-d3.png"
SVG = HERE / "GOIT-Hormuz-alternative-routes-d3.svg"

# Figure width is fixed in map.js; the height is dynamic (the title/subtitle
# wrap to the width, so taller headers make a taller figure). These are only
# fallbacks — the real size is read back out of the exported SVG below.
FIG_W, FIG_H = 1000, 931


def find_chrome():
    env = os.environ.get("CHROME")
    candidates = [env] if env else []
    candidates += [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for c in candidates:
        if c and pathlib.Path(c).exists():
            return c
    return None


def serve(port=0):
    """Start a quiet HTTP server rooted at this folder. Returns (httpd, port)."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    handler.log_message = lambda *a, **k: None  # silence request logging
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def export_assets(scale=3):
    chrome = find_chrome()
    if not chrome:
        print("No Chrome/Chromium/Edge found. Set CHROME=/path/to/browser, or run "
              "`python export.py --serve` and use the in-browser Download buttons.")
        return

    httpd, port = serve()
    base = f"http://127.0.0.1:{port}/index.html"
    common = [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars"]
    try:
        # SVG first: dump the DOM of ?export=svg and pull out the embedded
        # serialized SVG. We also read the figure's real width/height from it so
        # the PNG screenshot below is sized to match the (dynamic-height) figure.
        fig_w, fig_h = FIG_W, FIG_H
        dom = subprocess.run(common + [
            "--virtual-time-budget=12000", "--dump-dom", base + "?export=svg",
        ], check=True, capture_output=True, text=True).stdout
        m = re.search(r'<pre id="export-out">(.*?)</pre>', dom, re.S)
        if m:
            svg_str = htmllib.unescape(m.group(1))
            SVG.write_text(svg_str, encoding="utf-8")
            print("wrote", SVG)
            dim = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_str)
            if dim:
                fig_w, fig_h = round(float(dim.group(1))), round(float(dim.group(2)))
        else:
            print("SVG export: serialized output not found — use the in-browser "
                  "Download SVG button instead.")

        # PNG: high-res screenshot sized exactly to the figure (?export=png strips
        # the toolbar + page padding so the screenshot is the figure and nothing else)
        subprocess.run(common + [
            f"--force-device-scale-factor={scale}", f"--window-size={fig_w},{fig_h}",
            "--virtual-time-budget=12000", f"--screenshot={PNG}", base + "?export=png",
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("wrote", PNG, f"({scale}× ≈ {fig_w*scale}×{fig_h*scale}px)")
    finally:
        httpd.shutdown()


def main():
    ap = argparse.ArgumentParser(description="Export the Hormuz D3 figure to PNG + SVG.")
    ap.add_argument("--scale", type=int, default=3, help="PNG device scale factor (default 3)")
    ap.add_argument("--serve", action="store_true",
                    help="run the dev server and block (open the URL to view/edit live)")
    args = ap.parse_args()

    if args.serve:
        httpd, port = serve()
        print(f"serving {HERE}\n  http://127.0.0.1:{port}/index.html\nCtrl-C to stop.")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            httpd.shutdown()
        return

    export_assets(scale=args.scale)


if __name__ == "__main__":
    main()
