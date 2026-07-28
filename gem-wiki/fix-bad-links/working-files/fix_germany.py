#!/usr/bin/env python3
"""Germany (2026-07-28): Background-citation repairs across the German terminals.

Same order of preference as the Italy pass -- relocation first, then a
content-verified archive snapshot, and only then a different source:

  * relocation -- several publishers here simply renumbered their URLs and kept
    the article. Montel moved `/en/story/<slug>/<id>` to `/en/news/<id>/<slug>`;
    Bayern Innovativ moved its news items under `/en/emagazine/detail/`; and
    Offshore Energy's Brunsbuettel piece only 404s because the wiki copy carries
    a raw `u`-umlaut plus a mailing-list tracking query, where the live URL is
    percent-encoded and bare. All three are the same document, so they are cited
    live rather than through an archive.
  * archive -- `{{Cite web}}`/`{{Cite news}}` MERGE (original stays in `url=`,
    snapshot goes to `archive-url`/`archive-date`, `url-status` flips to `dead`);
    a bare `[url text]` link has nowhere to put a snapshot, so its URL is
    replaced. Two bare links are promoted to templates instead of being replaced
    outright, because their snapshots are the only surviving copy and a template
    keeps the dead original visible to a reader.
  * dropped as redundant -- Mukran's dead BNN Bloomberg copy of the RWE exit sat
    immediately beside a live LNG Prime citation of the same fact. Nothing is
    lost by removing it, and nothing is gained by archiving a second copy of a
    fact the page already sources.
  * re-sourcing -- the last resort, used only where the first three fail. Four
    of the five here are upgrades rather than sideways moves: two Nasdaq copies
    of Reuters wire stories are replaced by the primary documents the wire was
    reporting on (Deutsche Umwelthilfe's own press release, which carries the
    Greifswalder Bodden sentence the wiki quotes; and the Bundesverwaltungs-
    gericht's own release on the Ostsee-Anbindungs-Leitung ruling), and BNN
    Bloomberg's dead copy of the Rügen relocation story is replaced by a live
    copy of the same Bloomberg wire at Rigzone.

Two things are deliberately left as open questions rather than papered over:

  * Lubmin's ABC News ref is restored by pointing at the Irish Examiner's live
    copy of the same AP wire story -- but that story says the Neptune arrived
    off MUKRAN on 23 November 2022 and was only "due to begin operation in
    nearby Lubmin" later, and two independent reports (Maritime Executive,
    Offshore Energy) put its arrival at Lubmin on 16 December 2022. The wiki
    sentence says it "arrived at the terminal site" in November. That is a
    factual correction to the prose, not a citation repair, so it is logged for
    human review instead of being rewritten here.
  * Brunsbüttel's Montel ref covered two claims at once: a Krebber quote about
    supply and offtake contracts, and Uniper's withdrawal from Wilhelmshaven.
    Only the second could be re-sourced (NS Energy). The Montel URL slug is
    about an unrelated RWE lignite-closure story and has no snapshot at all, so
    this looks like a citation that was mismatched when it was laid down rather
    than one that rotted. The Krebber quote is left flagged as unsourced.

The `A Barrel Full` citation on Wilhelmshaven FSRU goes for the usual reason:
abarrelfull is banned project-wide. Its sentence keeps an Energy Intelligence
citation, so no substitute is needed -- but note that abarrelfull was the only
support for that sentence's "8 mtpa" figure, and the Energy Intelligence article
that remains says 10 bcm/y (~7.25 mtpa). That discrepancy is a factual question
about the number, not about the citation, so it is logged for human review
rather than silently rewritten here.

Not touched, deliberately: the many `CHECK 401/403` refs (Reuters, S&P Global,
Bloomberg, eleconomista, globeecho). A bot wall is not a dead link -- those
pages load for a reader, and swapping a live citation for an archive would be a
downgrade. Stade's dw.com ref scanned as a soft-404 but now serves the full
article, so it is left alone as well.
"""
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

A = "https://web.archive.org/web/"

# ---------------------------------------------------------------- replacements

# NABU's own page carries the Greifswalder Bodden passage the wiki quotes in
# translation. Globe Echo (the existing citation) is an aggregator and only
# bot-walled rather than dead, so it stays; NABU is added beside it as the
# primary the quote actually comes from.
MUKRAN_NABU = (
    "<ref>{{Cite news|url=https://globeecho.com/news/europe/germany/why-the-"
    "planned-lng-terminal-off-rugen-is-so-controversial/?utm_source=substack&"
    "utm_medium=email|title=Why the planned LNG terminal off Rügen is so "
    "controversial|date=2023-04-20|work=Globe Echo|access-date=2023-10-01"
    "|language=en-US}}</ref>"
    "<ref>[https://www.nabu.de/natur-und-landschaft/meere/lebensraum-meer/"
    "gefahren/33131.html LNG-Terminals in Deutschland], NABU (Naturschutzbund "
    "Deutschland), accessed July 28, 2026.</ref>")

# Deutsche Umwelthilfe's own release carries, in German, the exact sentence the
# wiki quotes in translation; taz reported the suit independently the same day.
LUBMIN_DUH = (
    "<ref>[https://www.duh.de/presse/pressemitteilungen/pressemitteilung/"
    "deutsche-umwelthilfe-klagt-gegen-lng-terminalschiff-neptune-in-lubmin-an-"
    "der-ostsee/ Deutsche Umwelthilfe klagt gegen LNG-Terminalschiff \"Neptune\" "
    "in Lubmin an der Ostsee], Deutsche Umwelthilfe press release, 7 Aug. 2023."
    "</ref>"
    "<ref>[https://taz.de/Klage-gegen-LNG-Terminal-in-Lubmin/!5949178/ Klage "
    "gegen LNG-Terminal in Lubmin], ''taz'', 7 Aug. 2023.</ref>")

# ---------------------------------------------------------------------- fixes

BAN = "banned source (a barrel full) removed"

fixes = {
    "Lubmin FSRU": (
        "background refs: ap wire relocated to a live host; bnn and nasdaq dead "
        "-> rigzone and the primary sources the wire was reporting on", [
            ("abcnews 404 -> live copy of the same ap wire story", "abcnews.go.com",
             ("full",
              "<ref name=\":1\">{{Cite news|url=https://www.irishexaminer.com/world/"
              "arid-41013341.html|title=First floating LNG terminal arrives at German "
              "port|date=2022-11-23|work=Irish Examiner|agency=Associated Press"
              "|access-date=2026-07-28|language=en}}</ref>")),
            ("bnn 404 -> live copy of the same bloomberg wire story",
             "germany-to-move-disputed-lng-vessel", ("full",
             "<ref>{{Cite news|url=https://www.rigzone.com/news/wire/germany_to_move_"
             "disputed_lng_vessel_to_baltic_island_ruegen-11-may-2023-172760-article/"
             "|title=Germany to Move Disputed LNG Vessel to Baltic Island Ruegen"
             "|date=2023-05-11|work=Rigzone|agency=Bloomberg|access-date=2026-07-28"
             "}}</ref>")),
            ("nasdaq 404 -> duh's own release, which carries the quoted sentence",
             "german-environmental-group-sues-private-lng-terminal",
             ("full", LUBMIN_DUH)),
        ]),
    "Brunsbüttel FSRU": (
        "background refs: offshore-energy + bayern innovativ urls relocated", [
            ("offshore-energy 404 (raw umlaut + tracking params) -> live encoded url",
             "_hsmi=220516973", ("full",
             "<ref>[https://www.offshore-energy.biz/construction-of-brunsbu%CC%88ttel-"
             "lng-terminal-kicking-off-in-september/ Construction of Brunsbüttel LNG "
             "terminal kicking off in September]. Offshore Energy. July 20, 2022."
             "</ref>")),
            ("bayern innovativ 404 -> relocated live copy", "bayern-innovativ",
             ("swap",
              "https://www.bayern-innovativ.de/en/page/start-of-construction-for-"
              "brunsbuettel-lng-terminal",
              "https://www.bayern-innovativ.de/en/emagazine/detail/en/page/start-of-"
              "construction-for-brunsbuettel-lng-terminal")),
        ]),
    "Brunsbüttel LNG Terminal": (
        "background refs: montel url relocated; mismatched montel citation for the "
        "uniper withdrawal re-sourced to ns energy", [
            ("montel 404 -> relocated live copy", "1082222", ("swap",
             "https://www.montelnews.com/en/story/german-lng-terminal-still-faces-4-"
             "hurdles--developer/1082222",
             "https://www.montelnews.com/en/news/1082222/german-lng-terminal-still-"
             "faces-4-hurdles--developer")),
            ("montel lignite url (never matched this sentence, no snapshot) -> "
             "ns energy for the uniper half; krebber quote left unsourced",
             "rwe-expects-lignite-closure-deal", ("full",
             "<ref>[https://www.nsenergybusiness.com/news/uniper-reviews-wilhelmshaven-"
             "lng-project/ Uniper to re-evaluate Wilhelmshaven LNG terminal project "
             "amid market uncertainty], ''NS Energy'', 9 Nov. 2020.</ref>")),
        ]),
    "Mukran FSRU": (
        "background refs: dead bnn duplicate dropped; nasdaq + global energy "
        "infrastructure dead -> wayback and the court's own release; nabu added "
        "for the quote it carries", [
            ("bnn 404 -> drop, same fact already cited to lng prime",
             "rwe-draws-up-plans-to-exit", ("full", "")),
            ("nasdaq 404 -> wayback", "german-parliament-backs-fast-track", ("swap",
             "https://www.nasdaq.com/articles/german-parliament-backs-fast-track-"
             "plans-for-lng-terminals",
             A + "20240418012830/https://www.nasdaq.com/articles/german-parliament-"
             "backs-fast-track-plans-for-lng-terminals")),
            ("nasdaq 404 -> the court's own release on the ruling",
             "german-mukran-lng-import-terminal-seen-ready", ("full",
             "<ref>[https://www.bverwg.de/pm/2023/67 Erster Abschnitt der Ostsee-"
             "Anbindungs-Leitung darf weiter gebaut werden], Bundesverwaltungsgericht "
             "press release No. 67/2023, 14 Sept. 2023.</ref>")),
            ("global energy infrastructure 404 -> wayback merge",
             "globalenergyinfrastructure", ("full",
             "<ref>{{Cite web|url=https://globalenergyinfrastructure.com/news/2023/"
             "01-january/fsru-neptune-arrives-off-lubmin-germany/|title=FSRU Neptune "
             "Arrives off Lubmin, Germany|website=globalenergyinfrastructure.com"
             "|url-status=dead|archive-url=" + A + "20260316145922/https://"
             "globalenergyinfrastructure.com/news/2023/01-january/fsru-neptune-"
             "arrives-off-lubmin-germany/|archive-date=2026-03-16|access-date="
             "2024-11-27}}</ref>")),
            ("nabu primary added beside the aggregator carrying its quote",
             "globeecho.com", ("full", MUKRAN_NABU)),
        ]),
    "Stade LNG Terminal": (
        "background refs: gasworld dead -> wayback archive", [
            ("gasworld 404 -> wayback merge", "low-carbon-supply-chain", ("full",
             "<ref>{{Cite web|url=https://www.gasworld.com/low-carbon-supply-chain-"
             "for-lng-from-canada-to-germany-announced/2021010.article|title=Low-"
             "carbon supply chain for LNG from Canada to Germany announced|last="
             "Wright|first=Anthony|date=2021-06-04|website=gasworld|url-status=dead"
             "|archive-url=" + A + "20221008013915/https://www.gasworld.com/low-"
             "carbon-supply-chain-for-lng-from-canada-to-germany-announced/2021010."
             "article|archive-date=2022-10-08}}</ref>")),
        ]),
    "Wilhelmshaven FSRU": (
        "background refs: " + BAN + "; energy intelligence, gas-magazin and igu "
        "dead -> wayback", [
            ("abarrelfull -> drop", "2mnE1Xe", ("full", "")),
            ("energy intelligence soft-404 -> wayback merge", "energyintel", ("full",
             "<ref>{{Cite news|url=https://www.energyintel.com/0000017b-a7a9-de4c-"
             "a17b-e7eb89700000|title=E.On Hatches Plan for Germany's First LNG "
             "Import Terminal|date=2005-10-27|work=Energy Intelligence|url-status="
             "dead|archive-url=" + A + "20250818150807/https://www.energyintel.com/"
             "0000017b-a7a9-de4c-a17b-e7eb89700000|archive-date=2025-08-18"
             "|access-date=2023-01-23|language=en}}</ref>")),
            ("gas-magazin dead -> wayback", "gas-magazin", ("swap",
             "http://www.gas-magazin.de/gasmarkt/zeitung-lng-terminal-in-"
             "wilhelmshaven-wieder-in-planung_77020.html",
             A + "20170804122053/http://www.gas-magazin.de/gasmarkt/zeitung-lng-"
             "terminal-in-wilhelmshaven-wieder-in-planung_77020.html")),
            ("igu 404 -> wayback", "igu.org/sites", ("swap",
             "https://www.igu.org/sites/default/files/node-document-field_file/"
             "IGU_LNG_2018_0.pdf",
             A + "20200615071424/https://www.igu.org/sites/default/files/node-"
             "document-field_file/IGU_LNG_2018_0.pdf")),
        ]),
    "Wilhelmshaven TES FSRU": (
        "background refs: tes-h2 dead -> wayback archive", [
            ("tes-h2 404 -> wayback merge", "tes-partners-with-e-on-and-engie",
             ("full",
              "<ref>{{Cite web|url=https://tes-h2.com/tes-partners-with-e-on-and-"
              "engie-to-manage-the-5th-floating-storage-regasification-unit-of-"
              "germany/|title=TES partners with E.ON and ENGIE to manage the 5th "
              "floating storage regasification unit of Germany|website=TES H2"
              "|url-status=dead|archive-url=" + A + "20230207172609/https://tes-h2."
              "com/tes-partners-with-e-on-and-engie-to-manage-the-5th-floating-"
              "storage-regasification-unit-of-germany/|archive-date=2023-02-07"
              "}}</ref>")),
        ]),
    "Wilhelmshaven TES LNG Terminal": (
        "background refs: tes-h2 dead -> wayback archive", [
            ("tes-h2 404 -> wayback", "tes-h2-invests-in-german-green-energy-hub",
             ("swap", "https://tes-h2.com/tes-h2-invests-in-german-green-energy-hub/",
              A + "20230602094336/https://tes-h2.com/tes-h2-invests-in-german-green-"
              "energy-hub/")),
            ("tes-h2 404 -> wayback", "tes-wilhemshaven-import-terminal-included",
             ("swap",
              "https://tes-h2.com/tes-wilhemshaven-import-terminal-included-as-a-"
              "priority-project-in-the-german-government-acceleration-law/",
              A + "20221005054141/https://tes-h2.com/tes-wilhemshaven-import-"
              "terminal-included-as-a-priority-project-in-the-german-government-"
              "acceleration-law/")),
        ]),
}

if __name__ == "__main__":
    s = gw.session()
    diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}
    import pickle
    pickle.dump(diffs, open("diffs_germany.pkl", "wb"))
    print("\n\nALL DIFFS BUILT OK ->", len(diffs), "pages")
