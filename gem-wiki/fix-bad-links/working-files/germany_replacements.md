# Germany dead-link replacement research

Research-only findings. No wiki pages or other files were modified. Hard rules followed: no archive.org/web.archive.org, no gem.wiki/globalenergymonitor.org, no abarrelfull.*, verbatim-fetch verification only, ≥2 independent sources preferred (1 primary/regulatory acceptable alone), honest NOT-FOUND where unverifiable.

---

### 1. Brunsbüttel LNG Terminal [12] — "four hurdles" claim
STATUS: CONFIRMED
CLAIM: As of January 2020, the terminal still faced four major hurdles prior to achieving FID: securing financial backing, guaranteeing sufficient commercial deals for long-term use, acquiring the relevant nautical and land-use permits, and ensuring regulatory approval.
SOURCE 1: https://www.montelnews.com/en/news/1082222/german-lng-terminal-still-faces-4-hurdles--developer
  publisher / date: Montel News, Jan 27, 2020 (same article as the dead ref, live at a different URL path — `/en/news/` instead of the dead `/en/story/.../1082222`)
  http status you observed: 200 (curl, Chrome UA)
  VERBATIM: "the proposed 8bcm/year site still needed to tick four boxes, said Tijhuis. These included securing financial backing, guaranteeing sufficient commercial deals for long-term use, acquiring the relevant nautical and land-use permits as well as ensuring regulatory approval for the company's plans, Tijhuis said."
SOURCE 2: none (this is the same underlying Montel article at its live URL, not a second independent source — but it is a direct fetch of the actual content, not a mirror/paywall stub)
NOTES: The original dead URL `https://www.montelnews.com/en/story/german-lng-terminal-still-faces-4-hurdles--developer/1082222` returns 404. The article is live and fully readable (not paywalled) at the `/en/news/1082222/...` path. Recommend swapping the ref URL to this live path.

---

### 2. Brunsbüttel LNG Terminal [16] — RWE/Uniper Wilhelmshaven withdrawal claim
STATUS: PARTIAL
CLAIM: "The comments [RWE CEO optimism on Brunsbüttel FID] came a week after Uniper revealed it would not be proceeding with rival plans to import LNG at its proposed Wilhelmshaven LNG Terminal due to a lack of interest in long-term contracts."
SOURCE 1: https://www.nsenergybusiness.com/news/uniper-reviews-wilhelmshaven-lng-project/
  publisher / date: NS Energy Business, Nov 9, 2020
  http status you observed: 200 (WebFetch)
  VERBATIM: "Uniper said that it will re-evaluate plans for the proposed liquefied natural gas (LNG) terminal in Wilhelmshaven, Germany after failing to get the required response for its import capacities from market players." / "Although, several players participated in it and expressed general interest, the number of those who made their booking intentions binding was not enough." / project manager: "many companies don't want to make long-term commitments at the moment."
SOURCE 2: none found — S&P Global's own Nov 6, 2020 piece ("Uniper to re-evaluate plans for Wilhelmshaven LNG terminal after tepid interest") and Uniper's own press release (`uniper.energy/news/ltew-is-considering-new-focus-of-the-plans-for-an-import-terminal-in-wilhelmshaven`) both returned HTTP 403 to both WebFetch and curl (Akamai-style bot wall) — treated as live-not-dead per project convention but not independently verifiable.
NOTES: Two issues worth flagging to the human reviewer: (1) **Attribution mismatch** — the task described this as an "RWE/Uniper" withdrawal claim, but the actual wiki sentence attributes the Wilhelmshaven withdrawal to **Uniper**, not RWE (RWE is the subject of the surrounding paragraph about Brunsbüttel, not the withdrawing party). (2) **Citation appears mismatched regardless of live/dead status** — the existing `[ref]` for this sentence points to `montelnews.com/es/story/rwe-expects-lignite-closure-deal-by-year-end/`, whose own headline ("RWE expects lignite closure deal by year end") is about RWE's coal/lignite phase-out, not Uniper's Wilhelmshaven LNG withdrawal. That URL is also dead (404, confirmed via curl). The nsenergybusiness.com source above supports the underlying fact but is a different outlet than what should probably replace this ref.

---

### 3. Brunsbüttel FSRU [13] — offshore-energy.biz re-confirmation
STATUS: CONFIRMED
CLAIM: The FSRU terminal will have LNG tank capacity of 165,000 cubic metres, construction to begin around the turn of the year 2022/2023 timeframe context (article headlined "kicking off in September").
SOURCE 1: https://www.offshore-energy.biz/construction-of-brunsbu%CC%88ttel-lng-terminal-kicking-off-in-september/
  publisher / date: Offshore Energy (Sanja Pekic), Jul 20, 2022
  http status you observed: 200 (curl, Chrome UA)
  VERBATIM: "The terminal will have two LNG tanks with a capacity of 165,000 cubic metres (cbm) each and an LNG regasification plant." / "As early as the turn of the year 2022/2023, the terminal is to be built at the Elbe port of Brunsbüttel."
SOURCE 2: none re-fetched independently for this specific figure (this ref was already live and matched the claim; no replacement was needed)
NOTES: This URL is alive and already contains the exact claimed figures — no replacement needed, just re-confirmation.

---

### 4. Lubmin FSRU [8] — Neptune arrival date discrepancy
STATUS: MISMATCH — human resolution required (per instruction, not resolved by me)
CLAIM: "In November 2022, TotalEnergies' Neptune FSRU arrived at the terminal site [Lubmin]." (cited to a dead abcnews.go.com wire story, 404 confirmed via curl)
SOURCE 1: https://maritime-executive.com/article/fsru-arrives-in-germany-port-of-lubmin-to-start-lng-imports
  publisher / date: The Maritime Executive, Dec 16, 2022
  http status you observed: 200 (curl + WebFetch)
  VERBATIM: "Germany's second FSRU unit was moved into position in the Port of Lubmin today." / "The industrial port at Lubmin is restricted in its size and depth for vessels so the intricate plan called for the vessel to be prepared in the nearby port of Mukran, where it has been since late November."
SOURCE 2: https://www.offshore-energy.biz/lubmin-lng-terminal-receives-fsru-as-operator-expects-start-up-by-the-end-of-month/
  publisher / date: Offshore Energy, Dec 19, 2022
  http status you observed: 200 (curl + WebFetch)
  VERBATIM: "the FSRU Neptune reached the port on 16 December to take its place at the specially prepared berth." / "On 23 November, the FSRU arrived at Mukran Port where it was prepared for the final transfer to Lubmin."
NOTES: Two independent, verbatim-confirmed sources agree: Neptune arrived at **Mukran** on **Nov 23, 2022** (for draft-reduction prep), then reached **Lubmin** itself only on **Dec 16, 2022**. This contradicts the wiki's current claim that Neptune "arrived at the terminal site [Lubmin]" in November 2022. As instructed, I am presenting this evidence for the human to resolve rather than editing the claim myself — the wiki text likely needs to change "arrived at the terminal site in November" to reflect the Mukran-then-Lubmin two-step, with November referring to Mukran and December to Lubmin itself.

---

### 5. Lubmin FSRU [11] — Rügen relocation / noise complaints
STATUS: PARTIAL
CLAIM: Noise complaints from Lubmin-area residents were part of the impetus for Deutsche ReGas/the German government's May 2023 decision to relocate the Neptune FSRU to Mukran (Rügen).
SOURCE 1: https://www.duh.de/presse/pressemitteilungen/pressemitteilung/deutsche-umwelthilfe-klagt-gegen-lng-terminalschiff-neptune-in-lubmin-an-der-ostsee/
  publisher / date: Deutsche Umwelthilfe (DUH), Aug 7, 2023
  http status you observed: 200 (curl + WebFetch)
  VERBATIM: "Lärmbelastung von Anwohnenden grundlegend unterschätzt, maßgebliche Lärmrichtwerte tatsächlich erheblich überschritten" (noise pollution of residents fundamentally underestimated, relevant noise limit values in fact significantly exceeded)
SOURCE 2: none confirmed verbatim for the specific noise→relocation causal link. The original ref `bnnbloomberg.ca/germany-to-move-disputed-lng-vessel-to-baltic-island-ruegen-1.1918746` returns HTTP 200 but is a **soft-404**: the fetched page is a generic BNN Bloomberg homepage shell with no article text (confirmed via curl — no occurrence of "Ruegen", "Lubmin", "Neptune", or "Habeck" anywhere in ~272KB of page text). Reuters' coverage of the same May 2023 decision (`reuters.com/business/energy/germany-scales-down-lng-terminal-plans-supply-crisis-eases-2023-05-15/`) is entirely blocked to my tools (401/bot-challenge via curl; WebFetch reports it cannot fetch reuters.com at all).
NOTES: I can confirm noise problems at Lubmin were real and documented (DUH, Aug 2023 — post-dates the May 2023 relocation announcement but describes the same ongoing complaints) and, separately (via search summaries only, not verbatim-fetched, so not citable per the rules), that the May 2023 relocation decision was noise-related. I could not verbatim-verify a single fresh, live source that ties the two together explicitly. Recommend either accepting DUH alone (noise fact only, not the causal "why relocated" link) or flagging this claim for further research — do not treat this as fully resolved.

---

### 6. Mukran FSRU [6] — RWE exit
STATUS: CONFIRMED
CLAIM: RWE (the original sponsor) is no longer involved in the Mukran LNG project.
SOURCE 1: https://lngprime.com/lng-terminals/germanys-rwe-says-it-is-not-involved-in-mukran-lng-plans/82172/
  publisher / date: LNG Prime, May 23, 2023
  http status you observed: 200 (curl + WebFetch)
  VERBATIM: "RWE is not involved in the German government's plan for a possible FSRU terminal in Mukran" (direct quote from an RWE spokesperson)
SOURCE 2: none independently verbatim-confirmed. `de.marketscreener.com`'s German-language coverage ("RWE will auf Dauer kein LNG-Terminal-Betreiber sein") exists but returned HTTP 403 (Akamai "Access Denied") to both curl and WebFetch.
NOTES: The original dead ref `bnnbloomberg.ca/rwe-draws-up-plans-to-exit-controversial-german-lng-project-1.1918163` returns HTTP 200 but, like item 5's bnnbloomberg.ca URL, is a soft-404 (generic homepage shell, no occurrence of "RWE", "Ruegen", or "Mukran" in the fetched text). LNG Prime's direct quote from an RWE spokesperson functions as a primary/company-statement source, acceptable alone per the sourcing rules.

---

### 7. Mukran FSRU [23] — NABU marine-protection quote / DW original
STATUS: CONFIRMED
CLAIM: NABU (Germany's Nature and Biodiversity Conservation Union) stated that the planned Rügen LNG terminal would be built in a marine protection area, destroying seabed and endangering the Greifswalder Bodden, its habitats, and native species.
SOURCE 1: https://www.nabu.de/natur-und-landschaft/meere/lebensraum-meer/gefahren/33131.html
  publisher / date: NABU (primary source — the organization itself), undated on page but content matches the 2023 campaign period
  http status you observed: 200 (curl + WebFetch)
  VERBATIM: "Für das geplante Flüssiggas-Terminal vor Rügen soll eine Pipeline durch Meeresschutzgebiete gebaut werden. Das würde Teile des Meeresbodens zerstören und den bereits belasteten Greifswalder Bodden, seine Lebensräume und dort heimische Arten gefährden." (translation matches the wiki's English paraphrase almost exactly.)
SOURCE 2: none — NABU's own statement is a primary source, acceptable alone.
NOTES: The original dead ref (`globeecho.com/.../why-the-planned-lng-terminal-off-rugen-is-so-controversial/`) is confirmed dead (403, blocked, via curl). The task suggested chasing the original DW (Deutsche Welle) republication of this quote, but **dw.com is entirely inaccessible to my tools** — both WebFetch ("Claude Code is unable to fetch from www.dw.com") and WebSearch's domain filter reject it. I pivoted to NABU's own site, which is the primary source of the quote anyway (better than the DW republication would have been) and is fully live and verbatim-matching.

---

### 8. Stade LNG Terminal [3] — zim.de PDF confirmation
STATUS: CONFIRMED
CLAIM: "The [Stade LNG Terminal] facility is intended to be [a] longer-term replacement for the interim onshore Stade FSRU."
SOURCE 1: https://www.zim.de/Redaktion/DE/Downloads/F/faqs-lng-terminal-mukran.pdf?__blob=publicationFile&v=4
  publisher / date: Bundesministerium für Wirtschaft und Klimaschutz (Germany's Federal Ministry for Economic Affairs and Climate Action), "Informationen zum FSRU-Standort Mukran," Jul 12, 2023
  http status you observed: 200 (curl); downloaded PDF (5 pages), parsed with pypdf, real text layer confirmed
  VERBATIM: "Drei landbasierte Terminals sollen 2027 außerdem in Wilhelmshaven, Brunsbüttel und Stade in Betrieb gehen und lösen dabei jeweils eine FSRU ab." (Three land-based terminals are additionally due to come into operation in 2027 in Wilhelmshaven, Brunsbüttel, and Stade, each thereby replacing an FSRU.)
SOURCE 2: https://www.osw.waw.pl/en/publikacje/osw-commentary/2023-04-28/all-costs-germany-shifts-to-lng
  publisher / date: OSW Centre for Eastern Studies, Apr 28, 2023
  http status you observed: 200 (curl)
  VERBATIM: "Other projects which private investors will implement involve the facilities in Wilhelmshaven ... and those in Stade. All three terminals are expected to replace the FSRUs which have previously been operating in these locations."
NOTES: Both sources are alive and directly confirm the claim; a government FAQ PDF plus an independent think-tank commentary — strong (green-level) corroboration. No action needed beyond re-confirming these URLs are still live (they are).

---

### 9. Stade LNG Terminal [13] — Bloomberg Jan 2022 corroboration
STATUS: NOT-FOUND (for independent verbatim corroboration)
CLAIM: "In January 2022, citing gas market turbulence and volatility, HEH announced that it was delaying the binding phase of its capacity booking process until summer 2022 ... As a result, a final investment decision for the project, set for the first quarter of 2023, may also be delayed." (Bloomberg, Jan 12, 2022, cited alongside an S&P Global piece on the same delay in the same paragraph)
SOURCE 1: none fully verbatim-confirmed. S&P Global's own companion piece (`spglobal.com/.../011322-germanys-heh-delays-binding-open-season-for-stade-lng-import-terminal`) returned HTTP 403 "Security Controls Triggered" on every attempt (curl with Chrome UA, and WebFetch) — consistent with every other spglobal.com URL attempted in this project.
SOURCE 2: none
NOTES: I found two aggregator republications confirming the story is real and dated correctly — `tankterminals.com` and `tanknewsinternational.com`, both carrying the identical headline "Germany's HEH Delays Binding Open Season for Stade LNG Import Terminal" with `datePublished: 2022-01-17` in their page metadata (HTTP 200, confirmed via curl) — but **neither page renders the actual article body text** (both are stub/teaser pages showing only headline, byline, and date, with the `.article-content` div empty), so I could not verbatim-verify the specific "FID set for Q1 2023 may be delayed" sentence from any independently fetchable source. A 2023-01-12-dated Montel News article ("Decision on German LNG terminal Stade due in summer") covers a **different, later** delay decision and is paywalled (`isAccessibleForFree: false`) — not usable either. Per the task's guidance, reporting NOT-FOUND rather than guessing; the claim rests only on the already-cited (bot-walled but presumably live) Bloomberg and S&P Global originals.

---

### 10. Wilhelmshaven FSRU — 8 mtpa (2005 E.ON proposal) figure
STATUS: MISMATCH
CLAIM: "In October 2005, E.ON proposed the Wilhelmshaven FSRU Terminal in Lower Saxony, with capacity of 8 mtpa." (currently cited to a banned abarrelfull.wikidot.com link, plus a live energyintel.com link)
SOURCE 1: https://www.energyintel.com/0000017b-a7a9-de4c-a17b-e7eb89700000
  publisher / date: Energy Intelligence, "E.On Hatches Plan for Germany's First LNG Import Terminal," published Wed, Oct 26, 2005
  http status you observed: 200 (curl + WebFetch)
  VERBATIM: "German energy giant E.On announced Thursday that it plans to build the country's first ever LNG import terminal at Wilhelmshaven on the North Sea coast. As a first step, E.On said a feasibility study would begin to examine the technical and economic conditions for a 10 billion cubic meters per year (7.25 million ton per year) capacity terminal, which it estimates would cost €500 million ($600 million)."
SOURCE 2: none — did not find any live source stating "8 mtpa" specifically for the 2005 proposal.
NOTES: **This is not a NOT-FOUND — it is an active mismatch.** The wiki's own already-cited, currently-live source (Energy Intelligence, Oct 26, 2005) states the 2005 E.ON proposal's capacity as **10 bcm/y (7.25 million tonnes per year)**, not 8 mtpa. This is the same 7.25 Mt/10 bcm figure the task instructed me not to accept as a stand-in match for "8 mtpa" — but here it isn't a different outlet's approximation, it's the terminal's own currently-cited primary source directly contradicting the "8 mtpa" value in the wiki text. I found no independent live source anywhere supporting "8 mtpa" for the 2005 proposal (the only other citation is the banned abarrelfull.wikidot.com link, which cannot be used per the rules regardless). Recommend flagging the "8 mtpa" figure for human review — it appears to conflict with its own supporting source and may need correcting to 7.25 mtpa (10 bcm/y), per Energy Intelligence.
