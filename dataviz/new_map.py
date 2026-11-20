"""
Start a new map figure by copying dataviz/template-map/ to a folder of your choice.

Usage, from anywhere in the repo:
  python dataviz/new_map.py writing-and-analysis/2027-03-some-report/my-map --name GGIT-my-map-2027-03

The new folder can sit anywhere in this repo. The script points its index.html at dataviz/shared/ from wherever it lands, and sets the export file name. --name defaults to the folder name.
"""

import argparse
import os
import pathlib
import shutil

DATAVIZ = pathlib.Path(__file__).resolve().parent
REPO = DATAVIZ.parent
TEMPLATE = DATAVIZ / "template-map"


def main():
    ap = argparse.ArgumentParser(description="Copy the GEM map template into a new figure folder.")
    ap.add_argument("folder", help="path of the new figure folder; it must not exist yet")
    ap.add_argument("--name", help="file name for the exported SVG and PNG, without extension (default: the folder name)")
    args = ap.parse_args()

    dest = pathlib.Path(args.folder).resolve()
    if REPO not in dest.parents:
        raise SystemExit(f"{dest} is outside this repo, so the page could not reach dataviz/shared/.")
    if dest.exists():
        raise SystemExit(f"{dest} already exists. Pick a new folder name.")

    shutil.copytree(TEMPLATE, dest, ignore=shutil.ignore_patterns("*.svg", "*.png", "raw", ".DS_Store", "__pycache__"))

    shared = pathlib.Path(os.path.relpath(DATAVIZ / "shared", dest)).as_posix()
    index = dest / "index.html"
    index.write_text(index.read_text(encoding="utf-8").replace("../shared/", shared + "/"), encoding="utf-8")

    name = args.name or dest.name
    map_js = dest / "map.js"
    map_js.write_text(map_js.read_text(encoding="utf-8").replace('"GEM-template-map"', f'"{name}"'), encoding="utf-8")

    rel = dest.relative_to(REPO).as_posix()
    print(f"created {dest}")
    print("next:")
    print(f"  python dataviz/export.py {rel} --serve   # view it while you edit map.js")
    print(f"  python {rel}/prep_data.py               # after you point it at real data")
    print(f"  python dataviz/export.py {rel}           # write {name}.svg and {name}.png")


if __name__ == "__main__":
    main()
