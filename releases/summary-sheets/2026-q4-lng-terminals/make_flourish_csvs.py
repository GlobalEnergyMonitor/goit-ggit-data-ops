"""
CSV files for the Flourish charts on the GGIT LNG terminals dashboard, one file per chart.

Each file has exactly the columns the chart binds, in the order it binds them, so it can
replace the chart's data sheet as is. The chart list is the "Flourish figure locations" tab
of the dashboard text doc (17ZfslHDIvQRvmz7jeNxci2s5zCeIQTY2cL_QjMlyYvc).

The numbers come from GGIT-LNG-summary-sheets-2026Q4.ipynb itself: this script runs that
notebook's code cells up to its "Write the workbook" section and builds every file from the
frames it leaves behind. So the dashboard uses the same pull, the same terminal-capacity
fallback and the same capex method as the summary tables, and cannot drift from them.

    python make_flourish_csvs.py              # write flourish-csvs/*.csv
    python make_flourish_csvs.py --upload     # also push them to the Drive folder

--upload writes to the work shared drive through gws-gem-write. For each chart it updates the
CSV file of the same name, then writes the same values into the Google Sheet of the same name
(without ".csv"). Flourish reads the Sheet, not the CSV: each Sheet is published to the web as
CSV, and Flourish's "Import from URL" takes that published link. Drive serves a CSV file as a
generic download, which Flourish rejects. Writing into the existing Sheet keeps its ID and its
published link, and the publish setting republishes on every change, so a refresh needs nothing
in Flourish. A chart with no Sheet yet gets one: converted from the CSV, set to Calibri 10pt,
and published. The published link is printed for pasting into Flourish once.
Ask before running it: Drive writes need explicit approval each time.
"""

import argparse
import contextlib
import csv
import io
import json
import os
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "GGIT-LNG-summary-sheets-2026Q4.ipynb"
STOP_AT_HEADING = "## Write the workbook"
OUT_DIR = HERE / "flourish-csvs"

# "LNG dashboard (current)" on the GEM shared drive
DRIVE_FOLDER_ID = "15TUDuy5zEwYnOI0V1-dEA6qRi94qsnWG"
GWS_WRITE_CONFIG_DIR = "~/.config/gws-gem-write"

# Highlight numbers: "became operational in CURRENT_YEAR", "cancelled or shelved since ..."
CURRENT_YEAR = 2026
CANCELLED_SINCE = 2022

TOP_N = 10

# The capex table lists every subregion, with or without LNG capex, in this order.
CAPEX_SUBREGIONS = [
    ("Africa", "Northern Africa"),
    ("Africa", "Sub-Saharan Africa"),
    ("Americas", "Latin America and the Caribbean"),
    ("Americas", "Northern America"),
    ("Asia", "Central Asia"),
    ("Asia", "Eastern Asia"),
    ("Asia", "South-eastern Asia"),
    ("Asia", "Southern Asia"),
    ("Asia", "Western Asia"),
    ("Europe", "Eastern Europe"),
    ("Europe", "Northern Europe"),
    ("Europe", "Southern Europe"),
    ("Europe", "Western Europe"),
    ("Oceania", "Australia and New Zealand"),
    ("Oceania", "Melanesia"),
    ("Oceania", "Micronesia"),
    ("Oceania", "Polynesia"),
]


def run_notebook():
    """Execute the summary notebook's code cells up to the workbook write; return its namespace."""
    nb = json.loads(NOTEBOOK.read_text())
    ns = {}
    cwd = os.getcwd()
    os.chdir(HERE)                      # the notebook's paths are relative to its folder
    log = io.StringIO()
    try:
        with contextlib.redirect_stdout(log):
            for cell in nb["cells"]:
                src = "".join(cell["source"])
                if cell["cell_type"] == "markdown" and src.startswith(STOP_AT_HEADING):
                    break
                if cell["cell_type"] != "code":
                    continue
                # drop IPython magics (%pip install ...)
                code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("%"))
                exec(compile(code, str(NOTEBOOK), "exec"), ns)
    finally:
        os.chdir(cwd)
    # the fallback cell's report is worth seeing every run
    for line in log.getvalue().splitlines():
        if line.strip().startswith(("added:", "NOT ADDED:")) or "terminal(s) added" in line:
            print("notebook fallback:", line.strip())
    return ns


def blank_zero(frame, cols):
    """The country and capex charts show an empty cell, not 0, where there is nothing."""
    frame = frame.copy()
    for c in cols:
        frame[c] = frame[c].where(frame[c] != 0, "")
    return frame


def highlights(ns):
    """28357206 highlights table. Its four numbers are typed into Flourish number charts."""
    lng, IN_DEV = ns["lng"], ns["IN_DEV"]
    ec = ns["capacity"]["LNG export capacity by country/area"].loc["Total"]
    ic = ns["capacity"]["LNG import capacity by country/area"].loc["Total"]
    new_op = lng[(lng["Status"] == "operating")
                 & (lng["ActualStartYear"] == CURRENT_YEAR)]["CapacityinMtpa"].sum()
    gone = lng[lng["Status"].isin(["shelved", "cancelled"])].copy()
    gone_year = pd.to_numeric(gone["CancelledYear"], errors="coerce").where(
        gone["Status"] == "cancelled", pd.to_numeric(gone["ShelvedYear"], errors="coerce"))
    gone_mtpa = gone[gone_year >= CANCELLED_SINCE]["CapacityinMtpa"].sum()
    rows = [
        ("operating import and export capacity globally", ec["Operating"] + ic["Operating"]),
        (f"became operational in {CURRENT_YEAR}", new_op),
        ("currently in development globally", ec[IN_DEV] + ic[IN_DEV]),
        (f"cancelled or shelved since {CANCELLED_SINCE}", gone_mtpa),
    ]
    return pd.DataFrame([(round(v), "mtpa", t) for t, v in rows],
                        columns=["Value", "Unit", "Text"])


def capacity_over_time(ns, facility_type):
    """28357211 / 28357234. Capacity by the year each unit entered its current status:
    operating by start year, construction by construction year, proposed by proposal year."""
    lng, floor = ns["lng"], ns["START_YEAR_FLOOR"]
    d = lng[lng["FacilityType"] == facility_type]
    series = {}
    for label, status, year_col in [("Operating", "operating", "ActualStartYear"),
                                    ("Construction", "construction", "ConstructionYear"),
                                    ("Proposed", "proposed", "ProposalYear")]:
        s = d[d["Status"] == status].copy()
        s[year_col] = pd.to_numeric(s[year_col], errors="coerce")
        s = s[s[year_col] >= floor]
        series[label] = s.groupby(s[year_col].astype(int))["CapacityinMtpa"].sum()
    out = pd.DataFrame(series).fillna(0.0)
    out = out.reindex(range(floor, int(out.index.max()) + 1)).fillna(0.0).round(2)
    out.index.name = "Start year"
    return out.reset_index()


def top_operating(ns, facility_type):
    """28357221 / 28357238. Top ten countries by operating capacity."""
    t = ns["capacity"][f"LNG {facility_type} capacity by country/area"].drop(index="Total")
    out = t["Operating"].sort_values(ascending=False).head(TOP_N).round(1)
    out.index.name = "Country/Area"
    return out.reset_index()


def top_in_development(ns, facility_type):
    """28357226 / 28357243. Top ten countries by capacity in development."""
    t = ns["capacity"][f"LNG {facility_type} capacity by country/area"].drop(index="Total")
    t = t.sort_values(ns["IN_DEV"], ascending=False).head(TOP_N)
    out = pd.DataFrame({"Construction": t["Construction"].round(1),
                        "Proposed": t["Proposed"].round(1),
                        "Total": t[ns["IN_DEV"]].round(1)})
    out.index.name = "Country/Area"
    return blank_zero(out.reset_index(), ["Construction", "Proposed"])


def terminal_map(ns):
    """28357249 points sheet: every proposed and construction unit. The chart's lines,
    regions and regions_geometry sheets are its basemap and are not replaced."""
    lng = ns["lng"]
    d = lng[~lng["FromTerminalTotal"] & lng["Status"].isin(["proposed", "construction"])]
    year = pd.to_numeric(d["LatestPlannedStartYear"], errors="coerce").astype("Int64")
    return pd.DataFrame({
        "TerminalName": d["TerminalName"],
        "UnitName": d["UnitName"].fillna(""),
        "Type": d["FacilityType"].str.capitalize(),
        "Status": d["Status"].str.capitalize(),
        "Start year": year,
        "Capacity (mtpa)": d["CapacityinMtpa"],
        "Latitude": d["Latitude"],
        "Longitude": d["Longitude"],
    })


def capex_by_subregion(ns):
    """28357256. In-development capex by subregion, US$ billion."""
    ex = ns["capex"]["LNG export terminal capex by region"]
    im = ns["capex"]["LNG import terminal capex by region"]
    cols = ["Proposed (export)", "Construction (export)",
            "Proposed (import)", "Construction (import)"]

    def values(key):
        get = lambda t, c: t.loc[key, c] if key in t.index else 0.0
        return [get(ex, "Proposed"), get(ex, "Construction"),
                get(im, "Proposed"), get(im, "Construction")]

    known = {s for _, s in CAPEX_SUBREGIONS}
    stray = (set(ex.index) | set(im.index)) - known - {"Total"}
    assert not stray, f"capex subregions missing from CAPEX_SUBREGIONS: {stray}"
    rows = [[f"{r} - {s}"] + values(s) for r, s in CAPEX_SUBREGIONS]
    rows.append(["Total"] + values("Total"))
    out = pd.DataFrame(rows, columns=["Subregion"] + cols)
    out[cols] = out[cols].round(1)
    return blank_zero(out, cols)


# file name -> (Flourish viz ID, builder). Names carry no date so a refresh overwrites the
# same Drive file and the URL bound in Flourish never changes.
FILES = {
    "lng-dashboard-28357206-highlights.csv": (28357206, highlights),
    "lng-dashboard-28357211-export-capacity-over-time.csv":
        (28357211, lambda ns: capacity_over_time(ns, "export")),
    "lng-dashboard-28357221-top-10-exporters-operating.csv":
        (28357221, lambda ns: top_operating(ns, "export")),
    "lng-dashboard-28357226-top-10-export-in-development.csv":
        (28357226, lambda ns: top_in_development(ns, "export")),
    "lng-dashboard-28357234-import-capacity-over-time.csv":
        (28357234, lambda ns: capacity_over_time(ns, "import")),
    "lng-dashboard-28357238-top-10-importers-operating.csv":
        (28357238, lambda ns: top_operating(ns, "import")),
    "lng-dashboard-28357243-top-10-import-in-development.csv":
        (28357243, lambda ns: top_in_development(ns, "import")),
    "lng-dashboard-28357249-map-points.csv": (28357249, terminal_map),
    "lng-dashboard-28357256-capex-by-subregion.csv": (28357256, capex_by_subregion),
}


def gws(*args, upload=None):
    env = dict(os.environ,
               GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(GWS_WRITE_CONFIG_DIR),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    cmd = ["gws", *args]
    if upload:
        cmd += ["--upload", str(upload), "--upload-content-type", "text/csv"]
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gws {' '.join(args[:2])} failed:\n{res.stderr}{res.stdout}")
    out = res.stdout[res.stdout.find("{"):]
    return json.loads(out) if out.strip() else {}


SHEET_MIME = "application/vnd.google-apps.spreadsheet"
PUBLISH = {"published": True, "publishAuto": True, "publishedOutsideDomain": True}


def publish_sheet(sheet_id):
    """Publish the latest revision to the web, republishing on change; return the CSV link."""
    revisions = gws("drive", "revisions", "list", "--params",
                    json.dumps({"fileId": sheet_id, "fields": "revisions(id)"}))["revisions"]
    link = gws("drive", "revisions", "update", "--params",
               json.dumps({"fileId": sheet_id, "revisionId": revisions[-1]["id"],
                           "fields": "publishedLink"}),
               "--json", json.dumps(PUBLISH))["publishedLink"]
    return link.replace("/pubhtml", "/pub?output=csv")


def create_sheet(csv_id, name):
    """Convert the CSV file into a new Sheet in the folder, Calibri 10pt, published."""
    sheet_id = gws("drive", "files", "copy", "--params",
                   json.dumps({"fileId": csv_id, "supportsAllDrives": True, "fields": "id"}),
                   "--json", json.dumps({"name": name, "mimeType": SHEET_MIME,
                                         "parents": [DRIVE_FOLDER_ID]}))["id"]
    tab = gws("sheets", "spreadsheets", "get", "--params",
              json.dumps({"spreadsheetId": sheet_id, "fields": "sheets.properties.sheetId"}))
    gws("sheets", "spreadsheets", "batchUpdate", "--params",
        json.dumps({"spreadsheetId": sheet_id}),
        "--json", json.dumps({"requests": [{"repeatCell": {
            "range": {"sheetId": tab["sheets"][0]["properties"]["sheetId"]},
            "cell": {"userEnteredFormat": {"textFormat": {"fontFamily": "Calibri",
                                                          "fontSize": 10}}},
            "fields": "userEnteredFormat.textFormat.fontFamily,"
                      "userEnteredFormat.textFormat.fontSize"}}]}))
    return sheet_id


def write_sheet(sheet_id, path):
    """Replace the first tab's values with the CSV, as typed text so nothing is reformatted."""
    tab = gws("sheets", "spreadsheets", "get", "--params",
              json.dumps({"spreadsheetId": sheet_id, "fields": "sheets.properties.title"}))
    title = tab["sheets"][0]["properties"]["title"].replace("'", "''")
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    gws("sheets", "spreadsheets", "values", "clear", "--params",
        json.dumps({"spreadsheetId": sheet_id, "range": f"'{title}'"}))
    gws("sheets", "spreadsheets", "values", "update", "--params",
        json.dumps({"spreadsheetId": sheet_id, "range": f"'{title}'!A1",
                    "valueInputOption": "RAW"}),
        "--json", json.dumps({"values": rows}))


def upload(paths):
    """Update each CSV file in the Drive folder, then the published Sheet Flourish reads."""
    listing = gws("drive", "files", "list", "--params", json.dumps({
        "q": f'"{DRIVE_FOLDER_ID}" in parents and trashed=false',
        "supportsAllDrives": True, "includeItemsFromAllDrives": True,
        "fields": "files(id,name,mimeType)", "pageSize": 200}))
    csvs = {f["name"]: f["id"] for f in listing.get("files", []) if f["mimeType"] != SHEET_MIME}
    sheets = {f["name"]: f["id"] for f in listing.get("files", []) if f["mimeType"] == SHEET_MIME}
    for path in paths:
        if path.name in csvs:
            csv_id = csvs[path.name]
            gws("drive", "files", "update", "--params",
                json.dumps({"fileId": csv_id, "supportsAllDrives": True}), upload=path)
        else:
            csv_id = gws("drive", "files", "create", "--params",
                         json.dumps({"supportsAllDrives": True}),
                         "--json", json.dumps({"name": path.name, "parents": [DRIVE_FOLDER_ID],
                                               "mimeType": "text/csv"}), upload=path)["id"]
        name = path.stem
        if name in sheets:
            sheet_id = sheets[name]
            action = "updated"
        else:
            sheet_id = create_sheet(csv_id, name)
            action = "created"
        write_sheet(sheet_id, path)
        print(f"  {action} {name}\n    {publish_sheet(sheet_id)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--upload", action="store_true",
                    help="also create/update the files in the Drive folder (asks nothing; "
                         "get approval first)")
    args = ap.parse_args()

    ns = run_notebook()
    OUT_DIR.mkdir(exist_ok=True)
    written = []
    for name, (viz_id, build) in FILES.items():
        frame = build(ns)
        path = OUT_DIR / name
        frame.to_csv(path, index=False)
        written.append(path)
        print(f"{viz_id}  {len(frame):>4} rows  {name}")

    if args.upload:
        print(f"\nuploading to Drive folder {DRIVE_FOLDER_ID} (Flourish links below):")
        upload(written)


if __name__ == "__main__":
    main()
