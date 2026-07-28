#!/usr/bin/env python3
"""Italy follow-up: the two uncategorized pages the export/category union found.

Taranto LNG Terminal needs nothing -- its three refs between them carry every
figure in the sentence (12 bcm/y, EUR 600m, 3.5 bcm for the ex-Ilva works, the
city-council vote and the offshore-wind conflict).

Oristano FSRU's lone problem is not a dead link. The LNG Prime article is live
but subscriber-walled: only its two-sentence lead is public, and the lead does
not contain the "methanization of Sardinia / storage capacity approximately ten
times" clause the page attributes to it. Snam's own 8 Oct 2025 release states
both that clause and the transmission-network/provinces sentence word for word,
so it is added alongside -- the LNG Prime ref stays, it is alive.

Caveat for the next person verifying that URL: snam.it is an Adobe AEM
single-page app. The static HTML is a shell and a plain substring check will
false-negative; the rendered body is served at the same path with `.model.json`
substituted for `.html` (public, no auth). Checked there:
"Sulcis Iglesiente", "methanization" and "ten times" are all present.

Gioia Tauro's dead `pvp.giustizia.it` auction notice (never archived) turns out
to be a legitimate drop-as-redundant after all. The companion Staffetta
Quotidiana ref is not headline-only as first read: the server sends a teaser
paragraph ahead of the subscriber gate, and that teaser carries the 29.22%
stake, the 7 October 2020 auction date, the EUR 100,000 minimum increments, the
bankruptcy docket (262/2018) and a base price. What it does NOT carry is the
page's "EUR 6.8 million" -- it says "base d'asta di poco meno di 6,9 milioni di
euro". No live source anywhere states 6.8; that discrepancy is prose, which
this tooling cannot touch, so it goes to HUMAN-REVIEW.md with the quote.
"""
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

SNAM = ("https://www.snam.it/en/media/news-and-press-releases/comunicati-stampa/"
        "2025/Snam-exclusivity-agreement-potential-acquisition-Higas-conversion-"
        "Oristano-LNG-storage-FSRU.html")

ORISTANO = (
    "<ref>{{Cite web|url=https://lngprime.com/contracts-and-tenders/snam-plans-"
    "to-buy-italian-small-scale-lng-terminal-and-install-fsru/165933/|title=Snam "
    "plans to buy Italian small-scale LNG terminal and install FSRU"
    "|date=2025-10-08|website=LNG Prime|url-status=live|access-date=2026-07-13"
    "}}</ref>"
    "<ref>[" + SNAM + " Snam signs an exclusivity agreement for the potential "
    "acquisition of Higas and the conversion of the Oristano LNG storage "
    "facility into a regasification terminal], Snam press release, "
    "8 Oct. 2025.</ref>")

fixes = {
    "Gioia Tauro LNG Terminal": (
        "background refs: drop the dead pvp.giustizia auction notice -- the "
        "companion staffetta ref carries the stake, the date and the price", [
            ("drop as redundant: never archived, and staffetta's public teaser "
             "already states 29,22% / 7 ottobre / base d'asta / 262/2018",
             "pvp.giustizia.it/pvp/it/dettaglio_annuncio",
             ("full", "")),
        ]),
    "Oristano FSRU": (
        "background refs: lng prime is subscriber-walled past the lead -> "
        "snam's own release added for the metanization and storage claims", [
            ("add snam's 8 oct 2025 release alongside the paywalled lng prime "
             "piece", "lngprime.com/contracts-and-tenders",
             ("full", ORISTANO)),
        ]),
}

if __name__ == "__main__":
    s = gw.session()
    diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}
    import pickle
    pickle.dump(diffs, open("diffs_italy_extra.pkl", "wb"))
    print("\n\nALL DIFFS BUILT OK ->", len(diffs), "pages")
