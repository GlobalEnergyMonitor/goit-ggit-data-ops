#!/usr/bin/env python3
"""Italy (2026-07-28): Background-citation repairs across the 14 Italian terminals.

Three kinds of repair, in the order the project prefers them:

  * relocation -- the same document is still published, just at a new address
    (La Sicilia renumbered its article IDs; Montel-style path changes). Cite the
    live publisher copy, not an archive: it is the same document and it keeps
    working for a reader.
  * archive -- the document is genuinely gone from the live web but a snapshot
    replays it. `{{Cite web}}`/`{{Cite news}}` templates MERGE (the original URL
    stays in `url=`, the snapshot goes in `archive-url`/`archive-date`, and
    `url-status` flips to `dead`); a bare `[url text]` link has nowhere to put a
    snapshot, so its URL is replaced outright.
  * re-sourcing -- no live copy and no usable snapshot, so the claim needs a
    different source that states it. Only used when the first two fail, because
    it silently changes which document backs the sentence.

Separately, every `A Barrel Full` citation is removed: abarrelfull is a banned
source project-wide, so it cannot stay even where it merely corroborates. Where
it was the sentence's ONLY support it is replaced with a real source rather than
just deleted (Brindisi's 50-50 BG/Enel structure, Porto Empedocle's Enel
takeover of Nuove Energie); where the sentence keeps other citations it is
simply dropped. Several of these bans hide behind bit.ly shortlinks -- the
shortener still resolves, so only the link text gives them away.

Two dead refs turned out to be citing the wrong story altogether (Priolo's
"Shell withdraws" ref pointed at a Reuters piece about EU bank deposits); those
are re-sourced to articles that actually report the claim.
"""
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

A = "https://web.archive.org/web/"

# ---------------------------------------------------------------- replacements

# Enel's own 2003 joint press release with BG, and BG Group's 2005 Annual Report
# and Accounts (filed with the SEC as a 20-F exhibit) -- between them the 50-50
# structure and Enel's exit, from both partners' primary filings.
ENEL_BG_2003 = ("https://www.enel.com/content/dam/enel-com/pressrelease/"
                "porting_pressrelease/1595303-1_PDF-1.pdf")
BG_20F_2005 = ("https://www.sec.gov/Archives/edgar/data/805260/"
               "000102123106000163/b822635ex15-2.htm")
BRINDISI_JV = (
    "<ref>[" + ENEL_BG_2003 + " Enel to become BG Group's partner in Brindisi "
    "LNG], BG Group / Enel joint press release, 14 Feb. 2003.</ref>"
    "<ref>[" + BG_20F_2005 + " BG Group Annual Report and Accounts 2005] "
    "(\"On 21 June 2005, the Group acquired the remaining 50% of the voting "
    "shares of Brindisi LNG SpA that it did not already own\"), filed with the "
    "US SEC as an exhibit to BG Group's Form 20-F. Accessed July 28, 2026.</ref>")

# The Enel press release announcing completion of the Nuove Energie purchase --
# primary, and it also dates the 2005 agreements the secondary coverage confuses
# with the acquisition itself.
ENEL_NUOVE_ENERGIE = ("https://www.enel.com/content/dam/enel-com/pressrelease/"
                      "porting_pressrelease/1594997-1_PDF-1.pdf")
PE_NUOVE_ENERGIE = (
    "<ref name=Barrel>[" + ENEL_NUOVE_ENERGIE + " Enel acquires control of "
    "Porto Empedocle regasification terminal], Enel press release, 6 July 2007 "
    "(\"Enel Trade has completed the acquisition of 90% of Nuove Energie "
    "Srl\").</ref>")

# The Reuters URL on this ref is a story about EU bank deposits, not Shell's
# withdrawal -- a wrong citation rather than a dead one, so it is re-sourced.
PRIOLO_SHELL = (
    "<ref>[https://www.milanofinanza.it/news/priolo-anche-shell-abbandona-il-"
    "rigassificatore-1797119 Priolo, anche Shell abbandona il rigassificatore], "
    "''Milano Finanza'', 6 Nov. 2012.</ref>"
    "<ref>[https://livesicilia.it/erg-si-defila-in-pole-ecco-la-shell/ Erg si "
    "defila, in pole ecco la Shell], ''LiveSicilia'', 2012.</ref>")

# MHI's own release on the Brindisi EPC award is gone and was never archived.
# Two independent Italian outlets carry the same consortium line-up -- and
# informare.it also states the 50:50 BG/Enel ownership this ref is cited for.
# Note both date the award to December 2004, not the MHI slug's April 2005.
BRINDISI_EPC = (
    "<ref>[https://www.informare.it/news/gennews/2004/20042313.asp Brindisi LNG "
    "ha assegnato il contratto EPC per il terminal di rigassificazione di "
    "Brindisi], ''Informare'', Dec. 2004.</ref>"
    "<ref>[https://www.lagazzettadelmezzogiorno.it/news/home/26350/brindisi-la-"
    "tecnimont-fara-il-rigassificatore.html Brindisi, la Tecnimont fara il "
    "rigassificatore], ''La Gazzetta del Mezzogiorno'', 19 Dec. 2004.</ref>")

# Api Nova Energia's own site is gone and unarchived. LNG Industry covers the
# offshore siting, the 16 km distance and the developer; the Italian ministry's
# project page is the primary record. Neither states $250m -- LNG Industry puts
# the project at EUR 200 million, so the cost figure goes to HUMAN-REVIEW.
FALCONARA_PROJECT = (
    "<ref>[https://www.lngindustry.com/liquid-natural-gas/20072011/api_nova_"
    "receives_approval_for_italian_fsru/ Api Nova receives approval for Italian "
    "FSRU], ''LNG Industry'', 20 July 2011.</ref>"
    "<ref>[https://www.mase.gov.it/energia/gas-naturale-e-petrolio/gas-naturale/"
    "rigassificatori/terminale-off-shore-di-rigassificazione-gnl-di-falconara-"
    "marittima Terminale off-shore di rigassificazione GNL di Falconara "
    "Marittima], Italian Ministry of the Environment and Energy Security.</ref>")

# Energie und Management's free archive dropped the 2004 Endesa story and it was
# never archived; Staffetta Quotidiana ran the same news two days earlier.
MONFALCONE_ENDESA = (
    "<ref>[https://www.staffettaonline.com/articolo.aspx?id=28631 Endesa riprova "
    "con il GNL a Monfalcone], ''Staffetta Quotidiana'', 22 May 2004.</ref>")

# The English press release at gasnaturalfenosa.com has no snapshot, but a CDX
# prefix search turned up the Spanish original of the same 16 July 2009 release
# as an archived PDF on the company's own file server.
ZAULE_APPROVAL = (
    "<ref>[" + A + "20120703060526/http://www.gasnaturalfenosa.com/servlet/"
    "ficheros/1297093018383/20090716_NotaTrieste,22.pdf Gas Natural obtiene el "
    "decreto de aprobacion medioambiental para su proyecto de terminal "
    "regasificadora en Trieste, Italia], Gas Natural press release, 16 July 2009 "
    "(Spanish original of the since-removed English release).</ref>")

# ---------------------------------------------------------------------- fixes

BAN = "banned source (a barrel full) removed"
BAN_SUB = "banned source (a barrel full) replaced with a primary source"

fixes = {
    "Adriatic LNG Terminal": (
        "background refs: " + BAN + "; argus 404 -> wayback; nasdaq 404 re-sourced", [
            ("abarrelfull -> drop", "abarrelfull.wikidot.com/adriatic", ("full", "")),
            ("argus 404 -> wayback merge", "argusmedia.com/en/news/2114070", ("full",
             "<ref>{{Cite web|url=https://www.argusmedia.com/en/news/2114070-adriatic-"
             "lng-to-receive-first-qflex|title=Adriatic LNG to receive first Q-Flex"
             "|last=|first=|date=2020-06-12|website=Argus Media|language=en"
             "|url-status=dead|archive-url=" + A + "20210712222518/https://www."
             "argusmedia.com/en/news/2114070-adriatic-lng-to-receive-first-qflex"
             "|archive-date=2021-07-12|access-date=}}</ref>")),
            ("nasdaq 404 -> re-sourced", "nasdaq.com/articles/exxon-mobil-to-sell", ("full",
             "<ref>[https://www.marinelink.com/news/exxon-mobil-finds-buyer-adriatic-"
             "lng-508514 ExxonMobil Finds Buyer for Adriatic LNG Stake], "
             "''MarineLink'', 2024.</ref><ref>[https://www.offshore-technology.com/"
             "news/exxon-lng-terminal-stake-sale/ ExxonMobil to sell majority stake "
             "in Italian LNG terminal to BlackRock], ''Offshore Technology'', "
             "2024.</ref>")),
        ]),
    "Brindisi LNG Terminal": (
        "background refs: " + BAN_SUB + "; lngworldnews 404 -> wayback; dead "
        "mhi release -> two italian outlets on the same epc award", [
            ("mhi release dead and unarchived -> informare + gazzetta",
             "mhi.com/news/sec1", ("full", BRINDISI_EPC)),
            ("abarrelfull -> enel/bg primary sources",
             "abarrelfull.wikidot.com/brindisi-lng-terminal Brindisi",
             ("full", BRINDISI_JV)),
            ("lngworldnews 404 -> wayback", "lngworldnews.com/italy-bg-shelves",
             ("swap",
              "http://www.lngworldnews.com/italy-bg-shelves-brindisi-lng-project/",
              A + "20191118092755/https://www.lngworldnews.com/italy-bg-shelves-"
              "brindisi-lng-project/")),
        ]),
    "Falconara Marittima LNG Terminal": (
        "background refs: " + BAN + "; dead developer page -> lng industry + "
        "the ministry's own project page", [
            ("abarrelfull -> drop", "bit.ly/2lYXwlu", ("full", "")),
            ("api nova site dead and unarchived -> lng industry + mase",
             "apinovaenergia.gruppoapi.com", ("full", FALCONARA_PROJECT)),
        ]),
    "Panigaglia LNG Terminal": ("background refs: " + BAN, [
        ("abarrelfull -> drop", "bit.ly/2lZrrtE", ("full", "")),
    ]),
    "Piombino FSRU": ("background refs: euronews dead -> wayback archive", [
        ("euronews 406 -> wayback merge", "euronews.com/next/2022/12/09", ("full",
         "<ref>{{Cite web|url=https://www.euronews.com/next/2022/12/09/italy-energy-"
         "lng|title=Italy's Snam to pick offshore site for new LNG terminal in early "
         "2023 {{!}} Euronews|date=2022-09-12|website=www.euronews.com|url-status="
         "dead|archive-url=" + A + "20250725083308/https://www.euronews.com/next/"
         "2022/12/09/italy-energy-lng|archive-date=2025-07-25|access-date="
         "2026-07-14}}</ref>")),
    ]),
    "Porto Empedocle LNG Terminal": (
        "background refs: " + BAN_SUB + "; la sicilia relocated; greenitalia dead -> wayback", [
            ("abarrelfull -> enel 2007 press release", "name=Barrel",
             ("full", PE_NUOVE_ENERGIE)),
            ("la sicilia 404 -> relocated live copy",
             "lasicilia.it/news/agrigento/155/", ("swap",
              "http://www.lasicilia.it/news/agrigento/155/l-enel-ha-deciso-e-rinuncia-"
              "al-rigassificatore-di-porto-empedocle.html",
              "https://www.lasicilia.it/news/agrigento/1100801/l-enel-ha-deciso-e-"
              "rinuncia-al-rigassificatore-di-porto-empedocle.html")),
            ("greenitalia dead -> wayback merge", "greenitalia.org", ("full",
             "<ref>{{Cite web|url=https://greenitalia.org/green-italia-contro-il-"
             "rigassificatore-di-porto-empedocle-e-a-agrigento-2/|title=Green Italia "
             "contro il rigassificatore di Porto Empedocle e a Agrigento|last=|first="
             "|date=|website=Green Italia|language=|url-status=dead|archive-url="
             + A + "20250328164644/https://greenitalia.org/green-italia-contro-il-"
             "rigassificatore-di-porto-empedocle-e-a-agrigento-2/|archive-date="
             "2025-03-28|access-date=2021-01-14}}</ref>")),
        ]),
    "Priolo Augusta LNG Terminal": (
        "background refs: " + BAN + "; shell-withdrawal ref pointed at an unrelated "
        "reuters story -> re-sourced", [
            ("abarrelfull -> drop", "bit.ly/2lZqi5i", ("full", "")),
            ("wrong reuters story -> milanofinanza + livesicilia",
             "uk-eu-banks-deposits", ("full", PRIOLO_SHELL)),
        ]),
    "Toscana FSRU": (
        "background refs: " + BAN + "; lngworldnews, porttechnology and "
        "conferenzagnl dead -> wayback", [
            ("abarrelfull -> drop", "bit.ly/2lZnEMJ", ("full", "")),
            ("porttechnology 404 -> wayback", "porttechnology.org/news/first_"
             "floating_lng_platform", ("swap",
             "https://www.porttechnology.org/news/first_floating_lng_platform_"
             "begins_commercial_operations",
             A + "20250427125259/https://www.porttechnology.org/news/first_"
             "floating_lng_platform_begins_commercial_operations")),
            ("lngworldnews 404 -> wayback", "lngworldnews.com/fsru-toscana-arrives",
             ("swap", "http://www.lngworldnews.com/fsru-toscana-arrives-in-italy/",
              A + "20170601014557/http://www.lngworldnews.com/fsru-toscana-arrives-"
              "in-italy/")),
            ("conferenzagnl soft-404 -> wayback merge", "conferenzagnl.com", ("full",
             "<ref name=\":0\">{{Cite web|url=http://www.conferenzagnl.com/2019/09/"
             "snam-in-olt-avanza-procedura-bunker-gnl/?lang=en|title=Snam in the share "
             "capital of OLT (Offshore LNG Toscana) • News|last=|first=|date="
             "September 26, 2019|website=ConferenzaGNL|language=en-US|url-status=dead"
             "|archive-url=" + A + "20211020062946/http://www.conferenzagnl.com/2019/"
             "09/snam-in-olt-avanza-procedura-bunker-gnl/?lang=en|archive-date="
             "2021-10-20|access-date=}}</ref>")),
        ]),
    "Trieste Monfalcone LNG Terminal": (
        "background refs: " + BAN + "; dead energie und management story -> "
        "staffetta on the same 2004 endesa announcement", [
            ("abarrelfull -> drop", "bit.ly/2lZsry0", ("full", "")),
            ("e&m free archive dropped the story, no snapshot -> staffetta",
             "energie-und-management.de", ("full", MONFALCONE_ENDESA)),
        ]),
    "Zaule LNG Terminal": (
        "background refs: lngworldnews 404 -> wayback archive; unarchived "
        "english press release -> archived spanish original", [
        ("gas natural fenosa release unarchived -> archived spanish original",
         "gasnaturalfenosa.com/en/home", ("full", ZAULE_APPROVAL)),
        ("lngworldnews 404 -> wayback", "lngworldnews.com/gas-natural-fenosa-bins",
         ("swap",
          "https://www.lngworldnews.com/gas-natural-fenosa-bins-zaule-lng-project-in-italy/",
          A + "20190515045459/https://www.lngworldnews.com/gas-natural-fenosa-bins-"
          "zaule-lng-project-in-italy/")),
    ]),
}

if __name__ == "__main__":
    s = gw.session()
    diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}
    import pickle
    pickle.dump(diffs, open("diffs_italy.pkl", "wb"))
    print("\n\nALL DIFFS BUILT OK ->", len(diffs), "pages")
