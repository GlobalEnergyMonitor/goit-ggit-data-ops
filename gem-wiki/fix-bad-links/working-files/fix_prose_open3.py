#!/usr/bin/env python3
"""The last three open HUMAN-REVIEW items from the Italy/Spain/Germany sweep.

All three were parked as "no source at all" -- a figure, a clause and a
quotation whose citations turned out not to carry them. Each is closed here by
finding a source rather than by deleting the claim, except the Brunsbuettel
quotation, which is downgraded to reported speech because the wording that can
be verified is German and putting a back-translation inside quotation marks
would be inventing a quote.

Priolo Augusta. "$500 million" rests on an ICIS ref that serves only a
212-byte Incapsula bot-challenge stub and has no Wayback snapshot, so the
figure is unverifiable where it is cited. Informare, reporting the same
announcement one day earlier (23 Feb. 2005), gives "un investimento di circa
400 milioni di euro" alongside the 8 bcm/y capacity that matches GEM's record.
Later reporting drifts (MilanoFinanza: EUR 500m in 2009, 450m in Sept. 2012,
800m in Nov. 2012), so the sentence is pinned to the announcement-time figure.
The ICIS ref is kept -- bot-walled is not dead, and it still supports the 2005
announcement it sits behind.

El Musel. The opposition clause survived a re-sourcing that only covered the
approval half (Bunker Index). Europa Press's wire original names the group
(Xixon Si Puede) and the argument -- the port "puso en bandeja" the legalisation
of a plant "declarada ilegal por el Tribunal Supremo" -- and El Comercio's
next-day write-up adds Izquierda Unida and the "primer paso" framing. Both are
fetchable in full; the eleconomista copy is Akamai-walled and unarchived, and
is not needed. The clause gains the two names, since the sources have them.

Brunsbuettel. The quotation's Montel citation pointed at an unrelated RWE
lignite story that was never archived. A search on the quotation's own wording
returns exactly one page on the indexed web: gem.wiki itself. What does exist
is the Dow Jones Newswires report of the Q3 2020 earnings call it came from
(12 Nov. 2020), which carries the substance in German -- Krebber as
"RWE-Finanzvorstand", the Covid-19 slip, "sehr optimistisch", "genug
Liefervertraege", "ueber die Ziellinie" -- and Global LNG Info's English note
of the same week. Note both call him CFO: Krebber did not become CEO until May
2021, so "RWE's CEO" was wrong independently of the sourcing. The German source
gives only supply contracts, never offtake contracts, so that half of the old
quotation goes with it.
"""
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

INFORMARE = "https://www.informare.it/news/gennews/2005/20050354.asp"
EUROPAPRESS = (
    "https://www.europapress.es/asturias/noticia-xsp-lamenta-autorizacion-"
    "bunkering-musel-pone-bandeja-legalizacion-regasificadora-"
    "20170307132752.html")
COMERCIO = ("https://www.elcomercio.es/gijon/201703/08/"
            "xixon-puede-creen-paso-20170308000450-v.html")
DOWJONES = ("https://www.finanznachrichten.de/nachrichten-2020-11/"
            "51226518-rwe-will-ueber-lng-terminal-brunsbuettel-nun-erst-"
            "2021-entscheiden-015.htm")
GLNGI = ("https://www.globallnginfo.com/ShowNews.aspx?"
         "NewsID=ANTA0ODQ5NTc0ODQ4NDg0ODQ4NTE1MQ==")

PRIOLO_OLD = (
    "It would cost around $500 million.<ref name=cap>")
PRIOLO_NEW = (
    "It would cost around €400 million.<ref name=cap>")
PRIOLO_REF = (
    "<ref>[" + INFORMARE + " Progetto di Shell ed ERG per lo sviluppo di un "
    "terminal per la rigassificazione di gas naturale liquefatto in Sicilia], "
    "''Informare'', 23 Feb. 2005.</ref>")
PRIOLO_ANCHOR = "ICIS, 24 Feb. 2005.</ref>"

MUSEL_OLD = (
    "this decision was met with opposition from local political groups who "
    "maintain this use would go against previous court decisions.")
MUSEL_NEW = (
    "this decision was met with opposition from the local political groups "
    "Xixón Sí Puede and Izquierda Unida, who called it a first step toward "
    "legalizing a regasification plant that the Supreme Court had declared "
    "illegal.")
MUSEL_REFS = (
    "<ref>[" + EUROPAPRESS + " XSP lamenta que la autorización del "
    "'bunkering' en El Musel pone en bandeja la legalización de la "
    "regasificadora], ''Europa Press'', 7 Mar. 2017.</ref>"
    "<ref>M. Menéndez, [" + COMERCIO + " Xixón Sí Puede e IU creen que es el "
    "paso para legalizar la regasificadora], ''El Comercio'', "
    "8 Mar. 2017.</ref>")
MUSEL_ANCHOR = "''Bunker Index'', 8 Mar. 2017.</ref>"

BRUNS_OLD = (
    "With FID being aimed for in the first half of 2021, RWE's CEO Markus "
    "Krebber also said, \"We are very optimistic that we will get enough "
    "supply contracts, and also offtake contracts, to get the project over "
    "the finishing line.\" The comments came a week after Uniper")
BRUNS_NEW = (
    "On RWE's third-quarter earnings call on November 12, 2020, the company's "
    "CFO, Markus Krebber, said COVID-19 had slightly delayed the investment "
    "decision, which was now expected in the first half of 2021; he added "
    "that RWE was very optimistic it would secure enough supply contracts to "
    "carry the project over the finishing line, and that all of the partners "
    "still expected Germany's first LNG import terminal to be built."
    "<ref>[" + DOWJONES + " RWE will über LNG-Terminal Brunsbüttel nun erst "
    "2021 entscheiden], Dow Jones Newswires, 12 Nov. 2020.</ref>"
    "<ref>[" + GLNGI + " German LNG completes EPC contractor pre-qualification "
    "process] (update of 18 Nov. 2020), ''Global LNG Info''.</ref> "
    "The comments came a week after Uniper")

fixes = {
    "Priolo Augusta LNG Terminal": (
        "background: the 2005 announcement put the cost at €400 million, per "
        "informare; the icis ref serves only a bot-challenge stub and cannot "
        "support the $500m figure", [
            ("$500 million -> €400 million", PRIOLO_OLD, PRIOLO_NEW),
        ]),
    "El Musel LNG Terminal": (
        "background: source the 2017 bunkering opposition (europa press + el "
        "comercio) and name the two groups", [
            ("name the groups and their argument", MUSEL_OLD, MUSEL_NEW),
        ]),
    "Brunsbüttel LNG Terminal": (
        "background: re-source the november 2020 krebber comments to the dow "
        "jones report of the q3 call; he was cfo, not ceo, until may 2021", [
            ("unsourced quote -> sourced reported speech; ceo -> cfo",
             BRUNS_OLD, BRUNS_NEW),
        ]),
}

# Refs are appended after an existing ref rather than folded into the prose
# swap above, so the two kinds of change stay independently reviewable.
APPENDS = [
    ("Priolo Augusta LNG Terminal", "add the informare ref for €400m",
     PRIOLO_ANCHOR, PRIOLO_REF),
    ("El Musel LNG Terminal", "add the two opposition refs",
     MUSEL_ANCHOR, MUSEL_REFS),
]


def append_after(new, anchor, addition, label):
    if new.count(anchor) != 1:
        raise SystemExit(f"anchor not unique ({new.count(anchor)}): {label}")
    out = new.replace(anchor, anchor + addition, 1)
    print(f"--- {label}\n  AFTER: ...{anchor}\n  ADD: {addition}\n")
    return out


if __name__ == "__main__":
    s = gw.session()
    diffs = {t: fixlib.build_prose(s, t, fx) for t, (summ, fx) in fixes.items()}
    for title, label, anchor, addition in APPENDS:
        old, new = diffs[title]
        diffs[title] = (old, append_after(new, anchor, addition, label))
    import pickle
    pickle.dump(diffs, open("diffs_prose_open3.pkl", "wb"))
    print("\n\nALL DIFFS BUILT OK ->", len(diffs), "pages")
