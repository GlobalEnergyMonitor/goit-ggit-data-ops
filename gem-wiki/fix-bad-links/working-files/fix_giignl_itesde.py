#!/usr/bin/env python3
"""Italy / Spain / Germany (2026-07-28): GIIGNL annual-report citation repairs.

Every legacy `giignl.org` annual-report URL on these pages is dead -- the
association moved the whole publication set behind a Webflow CDN. The document
is unchanged, so this is a relocation, not a re-sourcing: each dead URL is
swapped for the CDN copy of the SAME edition (never a newer one, which would
silently re-date the claim). Edition->URL table lives in fixlib.

Two shapes need more than a URL swap:
  * `<ref>https://giignl.org/...pdf</ref>` -- a naked URL is not a citation, so
    these are rebuilt as a real one via fixlib.giignl().
  * `<ref>[[/giignl.org/...pdf|GIIGNL 2021 Annual Report,]] ...</ref>` -- an
    external URL pasted into wikilink brackets, which renders as a redlink to a
    nonexistent local page rather than a link to the report. Also rebuilt.
"""
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

OLD2020 = ("https://giignl.org/sites/default/files/PUBLIC_AREA/Publications/"
           "giignl_-_2020_annual_report_-_04082020.pdf")
OLD2022 = "https://giignl.org/wp-content/uploads/2022/05/GIIGNL2022_Annual_Report_May24.pdf"
OLD2023 = "https://giignl.org/wp-content/uploads/2023/07/GIIGNL-2023-Annual-Report-July20.pdf"
OLD2024 = "https://giignl.org/wp-content/uploads/2024/06/GIIGNL-2024-Annual-Report-1.pdf"
OLD2025 = "https://giignl.org/wp-content/uploads/2025/06/GIIGNL-Annual-Report-2025.pdf"

ACC = "July 28, 2026"
SUMM = "giignl annual report: dead giignl.org pdf -> live cdn copy, same edition"
SUMM_BARE = ("giignl annual report: dead giignl.org pdf -> live cdn copy, "
             "same edition; bare url given a proper citation")

# A naked-URL ref, rebuilt as a citation pointing at the relocated PDF.
bare2025 = ("bare 2025 url -> cited cdn copy", OLD2025,
            ("full", fixlib.giignl(fixlib.G2025, 2025, accessed=ACC)))
# An external URL pasted into wikilink brackets: renders as a redlink, not a link.
wl2021 = ("malformed wikilink -> cited cdn copy", "giignl 2021 annual report apr27",
          ("full", fixlib.giignl(fixlib.G2021, 2021, accessed=ACC)))

fixes = {
    # ---- Italy ----
    "Adriatic LNG Terminal": (SUMM, [
        ("giignl 2022 -> cdn", OLD2022, ("swap", OLD2022, fixlib.G2022)),
        ("giignl 2020 -> cdn", OLD2020, ("swap", OLD2020, fixlib.G2020)),
    ]),
    "Panigaglia LNG Terminal": (SUMM_BARE, [
        ("giignl 2024 -> cdn", OLD2024, ("swap", OLD2024, fixlib.G2024)),
        bare2025,
    ]),
    "Porto Empedocle LNG Terminal": (SUMM, [
        ("giignl 2020 -> cdn", OLD2020, ("swap", OLD2020, fixlib.G2020)),
    ]),
    "Porto Torres FSRU": (SUMM_BARE, [bare2025]),
    "Ravenna FSRU": (SUMM, [
        ("giignl 2024 -> cdn", OLD2024, ("swap", OLD2024, fixlib.G2024)),
    ]),
    "Toscana FSRU": (SUMM, [
        ("giignl 2020 -> cdn", OLD2020, ("swap", OLD2020, fixlib.G2020)),
    ]),
    # ---- Spain ----
    "Barcelona LNG Terminal": (SUMM_BARE, [wl2021, bare2025]),
    "El Musel LNG Terminal": (SUMM_BARE, [
        ("giignl 2022 -> cdn", OLD2022, ("swap", OLD2022, fixlib.G2022)),
        bare2025,
    ]),
    "Huelva LNG Terminal": (SUMM_BARE, [wl2021]),
    # ---- Germany ----
    "Brunsbüttel FSRU": (SUMM, [
        ("giignl 2023 -> cdn", OLD2023, ("swap", OLD2023, fixlib.G2023)),
    ]),
    "Brunsbüttel LNG Terminal": (SUMM, [
        ("giignl 2024 -> cdn", OLD2024, ("swap", OLD2024, fixlib.G2024)),
    ]),
    "Lubmin FSRU": (SUMM, [
        ("giignl 2023 -> cdn", OLD2023, ("swap", OLD2023, fixlib.G2023)),
    ]),
    "Lubmin RWE FSRU": (SUMM, [
        ("giignl 2023 -> cdn", OLD2023, ("swap", OLD2023, fixlib.G2023)),
    ]),
    "Mukran FSRU": (SUMM, [
        ("giignl 2024 -> cdn", OLD2024, ("swap", OLD2024, fixlib.G2024)),
    ]),
    "Stade LNG Terminal": (SUMM, [
        ("giignl 2023 -> cdn", OLD2023, ("swap", OLD2023, fixlib.G2023)),
    ]),
    "Wilhelmshaven TES FSRU": (SUMM, [
        ("giignl 2024 -> cdn", OLD2024, ("swap", OLD2024, fixlib.G2024)),
    ]),
}

if __name__ == "__main__":
    s = gw.session()
    diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}
    import pickle
    pickle.dump(diffs, open("diffs_giignl_itesde.pkl", "wb"))
    print("\n\nALL DIFFS BUILT OK ->", len(diffs), "pages")
