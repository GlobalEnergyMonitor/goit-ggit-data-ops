# Italy dead-link replacements — research findings

### 1. Adriatic LNG Terminal [14]
STATUS: FOUND
CLAIM: ExxonMobil announced it had selected BlackRock as the potential buyer of its majority stake in the Adriatic LNG terminal; no final agreement yet reached (2023).
SOURCE 1: https://www.offshore-technology.com/news/exxon-lng-terminal-stake-sale/
  publisher / date: Offshore Technology (GlobalData), Oct 2023
  http status you observed: curl got 403 (bot-block); WebFetch loaded the page content successfully (treat as live per bot-block≠dead convention)
  VERBATIM: "Exxon Mobil has selected investment major BlackRock as the likely buyer for its stake in the Adriatic liquefied natural gas (LNG) import terminal in Italy." / "Exxon stated that because a definitive agreement had not been reached, it was still working on the acquisition."
SOURCE 2: https://www.marinelink.com/news/exxon-mobil-finds-buyer-adriatic-lng-508514
  publisher / date: MarineLink, Oct 2023
  http status you observed: 200
  VERBATIM: "Exxon Mobil Corp chose BlackRock as the potential buyer for its majority stake in Italy's main liquefied natural gas (LNG) import terminal, the U.S. oil producer said in a statement." / "Exxon said it continued to work on the transaction as a final agreement had not been reached."
NOTES: Clean replacement, both facts (selection + no final agreement) confirmed verbatim on both pages.

### 2. Brindisi LNG Terminal [3]
STATUS: FOUND
CLAIM: Brindisi LNG of Italy awarded the EPC contract for the LNG terminal to an international consortium including Tecnimont, GLF (Grandi Lavori Fincosit), VICNI (Vinci Construction), and MHI (Mitsubishi Heavy Industries).
SOURCE 1: https://www.sec.gov/Archives/edgar/data/0000805260/000119163805000107/bg200501246k.txt
  publisher / date: BG Group plc, SEC Form 6-K, 24 January 2005 (regulatory filing)
  http status you observed: 200 (fetched with `curl -A "GEM research baird.langenbrunner@globalenergymonitor.org"`)
  VERBATIM: "On 20 December 2004, Brindisi LNG SpA, a joint venture between BG Group and Enel, announced that the Engineering, Procurement and Construction (EPC) contract for the LNG importation terminal had been awarded to a consortium led by Tecnimont SpA and including Mitsubishi Heavy Industries Ltd, Grandi Lavori Fincosit SpA, Consorzio Cooperativa Costruttori, Sofregaz S.A and Vinci Construction Grands Projets SAS."
SOURCE 2: https://www.lagazzettadelmezzogiorno.it/news/home/26350/brindisi-la-tecnimont-fara-il-rigassificatore.html
  publisher / date: La Gazzetta del Mezzogiorno (Italian regional daily), Dec 2004
  http status you observed: 200
  VERBATIM: "L'associazione temporanea di imprese che ha vinto la gara, guidata da Tecnimont, è formata da Grandi Lavori Fincosit SpA, Consorzio Cooperativa Costruttori, Sofregaz, Vinci Construction Grands Projets Sas e Mitsubishi Heavy Industries Ltd."
NOTES: Primary regulatory filing (SEC 6-K) plus independent Italian press, both naming all four consortium members abbreviated in the wiki (Tecnimont, GLF, VICNI, MHI). The original MHI press release date (21 Apr 2005) vs. these sources' date (Dec 2004/Jan 2005) — the EPC award was first announced 20 Dec 2004; MHI's own release in Apr 2005 was presumably a later corporate PR restating the same award. Same underlying event/consortium either way.

### 3. Falconara Marittima LNG Terminal [1]
STATUS: PARTIAL
CLAIM: (a) MASE page names "API Nòva Energia" as the project sponsor; (b) "The project would cost about $250 million."
SOURCE 1 (for part a — re-confirmed): https://www.mase.gov.it/energia/gas-naturale-e-petrolio/gas-naturale/rigassificatori/terminale-off-shore-di-rigassificazione-gnl-di-falconara-marittima
  publisher / date: Ministero dell'Ambiente e della Sicurezza Energetica (MASE), Italian government
  http status you observed: 200
  VERBATIM: page text contains "API Nòva Energia" (confirmed present via grep on fetched HTML)
SOURCE 2 (cost, PARTIAL match only): https://www.lngindustry.com/liquid-natural-gas/20072011/api_nova_receives_approval_for_italian_fsru/
  publisher / date: LNG Industry, 20 July 2011
  http status you observed: 200
  VERBATIM: "The new project is worth approximately €200 million and is estimated to commence in 2015."
NOTES: MASE page re-confirmed live and correct (part a done). For the cost figure: I could NOT find any independent live source stating "$250 million" specifically — the only place that figure appears is the dead Api Nova Energia site and the banned abarrelfull mirror. The one live cost figure I found (LNG Industry, 2011) states approximately €200 million, which is a related but DIFFERENT number, not a corroboration of $250M. Recommend treating "$250 million" as effectively NOT-FOUND/unsourced; flag the €200M figure to the reviewer as a possible replacement value if they want to update the number rather than just re-cite it.

### 4. Gioia Tauro LNG Terminal [6]
STATUS: PARTIAL
CLAIM: In October 2020, Medgas Italia's 29.22% stake in the Gioia Tauro LNG project was scheduled to be auctioned off in bankruptcy court for approximately €6.8 million.
SOURCE 1: https://www.staffettaonline.com/articolo.aspx?id=345982
  publisher / date: Staffetta Quotidiana, 1 July 2020
  http status you observed: 200
  VERBATIM: "E' all'asta una quota del 29,22% del progetto di terminale di rigassificazione onshore da 12 mld mc/anno di Lng Medgas Terminal Srl a Gioia Tauro (RC). La vendita, con base d'asta di poco meno di 6,9 milioni di euro e rialzi di almeno 100.000 euro, avverrà il prossimo 7 ottobre e viene effettuata nell'ambito della procedura di fallimento 262/2018..."
SOURCE 2: none found
NOTES: This IS the article already cited alongside the dead giustizia.it ref (i.e. it's not a NEW independent source — it's the surviving twin citation for the same sentence), so this does not give you a second independent source for the dead giustizia.it auction-notice URL specifically. I could not find any other live page describing the giustizia.it court auction notice itself. Also note a minor figure discrepancy: Staffetta says base auction price "poco meno di 6,9 milioni" (~€6.9M), while GEM's wiki text says "€6.8 million" — close but not identical; worth a reviewer check. Net effect: the underlying fact is well corroborated by the still-live staffettaonline ref, but I found no replacement for the dead giustizia.it URL itself — recommend either dropping the dead ref (keeping staffettaonline as sole citation) or leaving it unsourced-for-that-URL.

### 5. Porto Empedocle LNG Terminal [4]
STATUS: FOUND
CLAIM: Enel had recently renewed permits for the Porto Empedocle project for another 52 months and remained interested in selling the project to another buyer (article: La Sicilia, 17 July 2016).
SOURCE 1: https://www.lasicilia.it/news/agrigento/1100801/l-enel-ha-deciso-e-rinuncia-al-rigassificatore-di-porto-empedocle.html
  publisher / date: La Sicilia, 2016
  http status you observed: 200
  VERBATIM (Italian): "Per la società di gestione dell'energia il mettere in vendita le autorizzazioni, fresche di rinnovo per 52 mesi, è ovviamente solo una questione economica. Chiusasi la parentesi del gas, l'eliminazione di progetti come quello di Porto Empedocle porterà infatti un risparmio di circa 850milioni di euro e, spera Enel, un introito importante qualora riesca a piazzare sul mercato quello che oggi è solamente un castello di carte."
  (Translation: "For the energy utility, putting the permits — freshly renewed for 52 months — up for sale is obviously purely a financial matter. With the gas chapter closed, eliminating projects like Porto Empedocle will bring savings of about €850 million and, Enel hopes, significant revenue if it manages to place on the market what today is only a house of cards.")
SOURCE 2: none independent found
NOTES: This is the SAME article/publisher (La Sicilia) as the dead URL, just resurfaced at a different live URL path — I tried two other URL variants for the same headline (both 404) before finding this live one. I searched extensively (multiple query variants) but could not find any OTHER (independent) outlet reporting this specific 2016 Enel announcement (52-month permit renewal + sale interest) — this appears to be a La Sicilia exclusive/local story that wasn't picked up elsewhere online. Single-source is the honest outcome here; recommend keeping it since it's a direct live copy of the exact original reporting.

### 6. Toscana FSRU [8]
STATUS: FOUND
CLAIM: FSRU Toscana began commercial operations in January 2014, described as the first floating LNG regasification platform of its kind.
SOURCE 1: https://www.lngindustry.com/liquid-natural-gas/13012014/fsru_toscana_begins_operations_31/
  publisher / date: LNG Industry, 13 January 2014
  http status you observed: 200
  VERBATIM: "The world's first ever floating liquefied natural gas (LNG) platform, the FSRU Toscana, has begun commercial operations off the coast of Italy." (headline: "World's first FSRU begins operations")
SOURCE 2: none found with the exact same claim
NOTES: I tried several other candidates (World Ports Organization — 403/blocked; Maritime Professional's "RINA classes first offshore FSRU" piece — describes 2010 projections, not the Jan 2014 commercial-ops milestone, so not a real match). The LNG Industry piece is a strong, exact, contemporaneous trade-press match (same publication date as the original dead Port Technology piece's topic) but I couldn't corroborate with a second independent outlet within reasonable search effort — treat as single-source FOUND.

### 7. Toscana FSRU [21]
STATUS: FOUND
CLAIM: Snam's acquisition from Iren Group of a 49.07% stake in OLT (Offshore LNG Toscana), completed February 2020, part of a ~€400 million valued deal, resulting ownership structure Snam 49.07% / First State Investments 48.24% / Golar LNG 2.69%.
SOURCE 1: https://www.ilsole24ore.com/art/rigassificatore-olt-iren-cede-snam-49percento-dell-impianto-ACrbSol
  publisher / date: Il Sole 24 Ore, 21 September 2019
  http status you observed: 200
  VERBATIM: "Snam mette le mani su Olt Offshore Lng Toscana" acquiring "il 49,07% della società alla quale fa capo l'infrastruttura galleggiante"; valuation "approximately 400 million euros as of December 31, 2017, with a net amount at closing of 345 million euros"
SOURCE 2: https://energiaoltre.it/snam-e-iren-conclusa-compravendita-del-4907-del-rigassificatore-olt/
  publisher / date: Energia Oltre, 26 February 2020 (deal-closing report)
  http status you observed: curl got 403 (bot-block); WebFetch loaded the page content successfully (treat as live)
  VERBATIM: "Snam ha acquisito una partecipazione pari al 49,07% del capitale sociale di OLT" from Iren; "Il corrispettivo versato da Snam al Gruppo Iren...è complessivamente pari a circa 332 milioni di euro"; post-deal stakes: Snam 49.07%, "First State Investments International Ltd...ne detiene il 48,24%", "Golar Offshore Toscana Ltd. possiede la quota rimanente, pari al 2,69%"
NOTES: IMPORTANT — the dead URL's slug ("snam-in-olt-avanza-procedura-bunker-gnl" = "Snam/OLT advances LNG bunkering procedure") suggested a bunkering-related topic, but reading the actual gem.wiki Background text shows ref [21] (name ":0") is actually cited for the Snam/Iren STAKE ACQUISITION sentences (not bunkering) — I researched and sourced that actual claim. If the original conferenzagnl.com article genuinely covered both topics under one URL, only the ownership-transaction content is relevant to what this ref supports in the wiki text. The exact net-closing price varies slightly across sources (€332M vs €345M — both are "net of certain adjustments" figures, consistent with the wiki's "€400 million" gross valuation figure); worth a reviewer glance but not a contradiction.

### 8. Trieste Monfalcone LNG Terminal [2]
STATUS: FOUND
CLAIM: The project was originally announced by Endesa in 2004.
SOURCE 1: https://www.staffettaonline.com/articolo.aspx/$/$/articolo.aspx?id=28631
  publisher / date: Staffetta Quotidiana, 22 May 2004 (dated 2 days before the dead German-language article's 24 May 2004 date — same news cycle)
  http status you observed: 200
  VERBATIM (Italian, free teaser text — article title "ENDESA RIPROVA CON IL GNL A MONFALCONE"): "Endesa riprova nell'impresa di realizzare un terminale di Gnl a Monfalcone (GO). Impresa a suo tempo fallita dall'Eni, all'indomani di un referendum locale..."
  (Translation: "Endesa is trying again in the endeavor to build an LNG terminal at Monfalcone (Gorizia province) — an endeavor that had previously failed under Eni, following a local referendum.")
SOURCE 2: none independent found
NOTES: Only the free teaser paragraph is accessible (rest is paywalled), but that teaser alone directly states the 2004 Endesa LNG-terminal announcement at Monfalcone, dated within days of the original dead citation. Searched extensively for a second outlet covering this specific 2004 announcement; found only retrospective mentions (which trace back to the same original story) or unrelated Endesa-Monfalcone power-plant coverage. Single-source FOUND.

### 9. Zaule LNG Terminal [2]
STATUS: FOUND
CLAIM: The EIA (environmental impact assessment) for Gas Natural's Trieste-Zaule regasification terminal project was completed in July 2009 ("Gas Natural obtains environmental approval...").
SOURCE 1: https://www.euro-petrole.com/gas-natural-obtains-environmental-approval-for-its-regasification-terminal-project-in-trieste-italy-n-i-3458
  publisher / date: Euro-Petrole (Enerpresse network), 27 July 2009 — appears to be the same press release also mirrored at euro-energie.com; counted as ONE source
  http status you observed: 200
  VERBATIM: "The Italian Ministry of the Environment has approved the Environmental Impact Assessment (VIA) for the liquid natural gas regasification plant planned by the company in the port of Trieste-Zaule, in the Friuli Venezia Giulia region, in the north east of the country." (article dated 27/07/2009)
SOURCE 2: https://www.movimentotriestelibera.net/wp/2019/01/22/the-lng-terminal-italy-wanted-to-force-in-trieste/
  publisher / date: Free Trieste Movement, 22 Jan 2019 (retrospective piece)
  http status you observed: curl timed out (no response within 40s); WebFetch fetched and returned content successfully
  VERBATIM: "In 2009, after the Italian Ministry for the Environment's shocking favorable opinion to Gas Natural's project, it was again those two organizations to denounce the scandal to public opinion."
NOTES: Source 1 exactly matches the claim (title, publisher, and July 2009 date all line up with the original dead Gas Natural Fenosa press release). Source 2 independently corroborates the 2009 Ministry approval but doesn't specify "July" — it's directionally consistent, not an exact-date match, so treat it as supporting rather than fully independent-and-precise corroboration.

### 10. Priolo Augusta LNG Terminal [4]
STATUS: FOUND (existing citation confirmed MISMATCHED — replaced with two correct sources)
CLAIM: In December 2012 (per wiki body text — actual event Nov 2012 per press), Shell announced it was also pulling out of the Priolo Augusta LNG project, leaving it with no developer; the regional government had apparently opposed the proposal.
EXISTING CITATION IS WRONG: `http://uk.reuters.com/article/uk-eu-banks-deposits-idUKKBN1AD1SO` is about EU bank deposits, not this LNG project — confirmed mismatched, do not attempt to rescue it.
SOURCE 1 (Shell withdrawal): https://www.milanofinanza.it/news/priolo-anche-shell-abbandona-il-rigassificatore-1797119
  publisher / date: MilanoFinanza, "MF Sicilia" edition, 6 November 2012
  http status you observed: 200
  VERBATIM: reports Shell's "dietrofront" (reversal/pullout) from the Priolo project, following ERG's earlier July 2012 exit from their Ionio Gas joint venture; local industrialist Aldo Garozzo quoted expressing disappointment over the lost investment
SOURCE 2 (regional government opposition): https://livesicilia.it/erg-si-defila-in-pole-ecco-la-shell/
  publisher / date: LiveSicilia
  http status you observed: 200
  VERBATIM: "Il consiglio di amministrazione di Erg ha deliberato di uscire dal progetto per la realizzazione di un rigassificatore nel comune di Melilli" after years of delay from the Sicilian regional government; describes Sicilian regional president Lombardo's decision to advance a competing terminal at Porto Empedocle instead, which "ha impedito la costruzione di quello di Priolo e Melilli" ("prevented the construction of the one at Priolo and Melilli") and caused a "durissimo scontro" (severe clash) with Confindustria
NOTES: The claim has two parts (Shell's Nov/Dec 2012 withdrawal; regional-government opposition) and I found one solid live source per part rather than a single source covering both — MilanoFinanza nails the Shell pullout date/fact, LiveSicilia establishes that the Sicilian regional government's choice to favor Porto Empedocle effectively blocked/opposed Priolo-Melilli. Note the wiki body text says "December 2012" but the press (MilanoFinanza, dated 6 Nov 2012, and the original dead Reuters citation's own "2 Nov. 2012" date) points to early November 2012 — flag this month discrepancy to the reviewer; it predates my scope (I was asked to find a correct citation, not correct the body text), but it's worth a look.
