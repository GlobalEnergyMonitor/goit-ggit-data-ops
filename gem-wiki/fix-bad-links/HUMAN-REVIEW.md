# Human review queue — refs the automated sweep could not settle

Everything else in [COVERAGE.md](COVERAGE.md) is resolved; these are the leftovers
that need a human. Section 1 items are bot-walled or login-walled URLs — opening
them in a normal browser settles each one in seconds. Section 2 items are
confirmed dead with no usable archive — fixing them means choosing a replacement
source that supports the sentence, which is researcher judgment.

For each item: if the article loads and matches the citation, check it off (no
wiki edit needed). If it's gone, tell Claude and the ref gets repaired like any
other. Compiled 2026-07-23.

## 1. Quick browser checks (bot-walled — a click settles it)

- [ ] **[Hazira LNG Terminal](https://www.gem.wiki/Hazira_LNG_Terminal)** —
  Reuters (401 to bots, no content archive; URL slug matches the claim):
  <https://www.reuters.com/article/shell-hazira-capacity/shell-plans-to-double-hazira-lng-plant-capacity-india-head-idUSL3N1H84HZ>
- [ ] **[Haldia FSRU](https://www.gem.wiki/Haldia_FSRU)** — S&P Global
  (bot-walled, no archive; slug matches):
  <https://www.spglobal.com/commodity-insights/en/news-research/latest-news/crude-oil/091025-appec-invenire-boosts-india-upstream-presence-ventures-into-lng-infrastructure>
- [ ] **[Dabhol LNG Terminal](https://www.gem.wiki/Dabhol_LNG_Terminal)** —
  Offshore Technology (Cloudflare-walled; slug matches):
  <https://www.offshore-technology.com/news/gail-dabhol-lng-terminal-capacity/?cf-view>
- [x] ~~**Dabhol / Hazira / AMNS Suvali** — Argus AMNS-Suvali article~~
  **Resolved 2026-07-23**: dead for humans too — swapped to the Dec 2024
  Wayback snapshot on Dabhol (rev 1198398) and Hazira (rev 1198399); AMNS
  Suvali's own page already cited the snapshot.
- [x] ~~**Dhamra LNG Terminal** — Argus Odisha-lockdown article~~
  **Resolved 2026-07-23** (rev 1198400): dead; replaced with the live Argus
  equivalent the reviewer found ("Indian states extend lockdowns, slashing
  fuel demand").
- [x] ~~**Kutubdia (Reliance) FSRU** — S&P Global Platts~~
  **Resolved 2026-07-23** (rev 1198401): dead for humans; replaced with the
  Natural Gas World copy ("Bangladesh Scraps Reliance FSRU", Oct 18, 2018).
  The same dead URL also sits in two auto-generated `autoref` refs, which are
  out of the project's scope.
- [x] ~~**Jaigarh LNG Terminal** — Hellenic Shipping News copy~~
  **Resolved 2026-07-23** (rev 1198402): replaced with the S&P Global
  original the reviewer located (Feb 21, 2020).
- [x] ~~**Mina Al-Ahmadi LNG Terminal** — Energy Institute doc~~
  **Reviewed 2026-07-23, left as-is**: the page cites it via a
  `webcache.googleusercontent.com` URL (which is why a page search for
  "energyinst" finds nothing); reviewer judged it not worth chasing.
- [ ] **[Dabhol LNG Terminal](https://www.gem.wiki/Dabhol_LNG_Terminal)** —
  ICIS, "India's GAIL puts Dabhol LNG terminal expansion plan on hold" (Feb
  2014). The live URL serves an empty page shell (likely a login wall), it was
  never archived, and no syndicated copy exists — needs an ICIS
  subscription/browser check:
  <https://www.icis.com/resources/news/2014/02/07/9751104/india-s-gail-puts-dabhol-lng-terminal-expansion-plan-on-hold/>

## 2. Dead refs needing a replacement source (researcher judgment)

Update 2026-07-23: replacement candidates researched and staged below as
**Proposed replacement** blocks — every URL was content-verified (key phrases
quoted from the live/archived page), but **nothing has been saved to the
wiki**. Check off an item to approve it; strike or comment to reject.

- [x] ~~**Karwar FSRU** — dead pipelineme.com ref (page's only Background
  citation)~~ **Resolved 2026-07-23** (rev 1198405): the automated search found
  nothing independent (moneycentral.com.ng repeats the wiki verbatim and links
  back to it — circular), but the reviewer located a [LinkedIn syndicated
  copy](https://www.linkedin.com/pulse/hyundai-heavy-industries-awarded-us565m-contract-largest-williams)
  of the same original article (identical US$563m-body/US$565m-headline
  mismatch, same Jan 2017 dating, names Fox Petroleum and Karwar) — swapped in.
  Closing sentence also updated per reviewer: shelved as of 2019, cancelled as
  of 2021 (last update Jan 2017).
- [x] ~~**Kukrahati LNG Terminal** — environmentclearance.nic.in risk-assessment PDF~~
  **Resolved 2026-07-23, no edit needed**: the PDF is reachable again (200,
  789 KB) — the earlier failure was a transient nic.in outage. The existing
  ref is intact and well-formed.
- [ ] **[Haldia FSRU](https://www.gem.wiki/Haldia_FSRU)** — therisk.global
  project page now redirects to an about page:
  <https://therisk.global/energy/haldia-fsru-project/>
  - **Proposed replacement** (high confidence):
    `<ref>[https://indiaseatradenews.com/smp-kolkata-awards-30-year-licence-for-floating-lng-terminal-at-haldia/ SMP Kolkata awards 30-year licence for floating LNG terminal at Haldia], India Seatrade News, September 8, 2025</ref>`
    — article body matches every supported fact (30-yr SMPK concession,
    Invenire Petrodyne + Excelerate consortium, FSRU at Haldia Dock Complex,
    1.5 mtpa expandable to 3, launch H2 2027); corroborated by GIIGNL's news
    page, Blackridge, and S&P.
- [ ] **[Gate LNG Terminal](https://www.gem.wiki/Gate_LNG_Terminal)** — Techint
  case-study PDF, dead and never archived:
  <http://www.techint-ingenieria.com/sites/default/files/upload/publications/files/Project%20Cse%20Study%20Gate.pdf>
  - **Proposed replacement** (high confidence):
    `<ref>[https://www.offshore-technology.com/projects/gate-lng-terminal/ Gate LNG Terminal], Offshore Technology, Dec. 14, 2011</ref>`
    — live page confirms everything the sentence bundles: June 2008
    construction start, Sept 2011 inauguration, Techint/SENER EPC consortium,
    Gasunie+Vopak ownership, €800m (~US$1.1B) cost. (The dead ref shares its
    sentence with 3 other refs, so this is a drop-in.)
- [ ] **[Terneuzen FSRU](https://www.gem.wiki/Terneuzen_FSRU)** — dead Nasdaq
  copy of a Dec 2022 Reuters piece (Gasunie eyeing Terneuzen), no archive or
  other syndication found:
  <https://www.nasdaq.com/articles/dutch-grid-operator-gasunie-looking-at-terneuzen-for-new-lng-capacity>
  - **Proposed replacement** (split into two refs — the dead ref supports two
    unrelated sentences and no single live source covers both):
    - Terneuzen-candidate-site sentence (medium-high):
      `<ref>[https://www.gasunie.nl/en/news/gasunie-investigates-options-for-increasing-lng-imports-in-the-netherlands Gasunie investigates options for increasing LNG imports in the Netherlands], Gasunie, December 12, 2022</ref>`
      — Gasunie's own press release: "For this, the port of Terneuzen is
      currently in the picture."
    - Bergermeer ~€500M sentence (high):
      `<ref>[https://www.euronews.com/next/2022/12/09/netherlands-gas-storage Netherlands to spend up to $548 million to fill gas storage for next winter], Euronews (citing Reuters), December 9, 2022</ref>`
      — "expects to spend up to 520.5 million euros… to fill the gas storage
      at Bergermeer… winter of 2023/2024."
    - Caveat: the same dead Nasdaq URL also lives in auto-generated
      `autoref_0` used across Tables 1–5 — out of this project's Background
      scope, flagged here for awareness.
- [ ] **[Revithoussa LNG Terminal](https://www.gem.wiki/Revithoussa_LNG_Terminal)**
  — dead DESFA page; live DESFA pages don't confirm the 1999/DEPA claims it
  supported: <http://www.desfa.gr/?p=11022&lang=en>
  - **Proposed replacement** (high confidence; split into two refs, one per
    fact — archived captures of the dead `?p=11022` URL all resolve to
    homepage/unrelated pages, so the original is truly unrecoverable):
    - 1999 completion:
      `<ref>[https://web.archive.org/web/20110721080341/http://www.depa.gr/files/downloadables/brochures/AnnualReport2006.pdf DEPA Annual Report 2006 (PDF), p. 16], DEPA S.A., 2007 (Wayback Machine capture)</ref>`
      — PDF text: "Construction of the Revythoussa… Terminal was completed in
      December 1999."
    - DESFA as DEPA subsidiary:
      `<ref>[https://web.archive.org/web/20180416151130/http://www.desfa.gr/en/company/historical-background Historical Background], DESFA S.A., April 16, 2018 (Wayback Machine capture)</ref>`
      — "established DESFA S.A. as a subsidiary company owned in its entirety
      by DEPA S.A."
- [ ] **[Kutubdia LNG Terminal (Petronet)](https://www.gem.wiki/Kutubdia_LNG_Terminal_%28Petronet%29)**
  — Petrobangla 2018 annual report PDF, dead path and never archived (the
  report may have moved elsewhere on petrobangla.org.bd):
  <https://petrobangla.org.bd/admin/attachment/webtable/1263_upload_0.pdf>
  - **Proposed replacement** (high confidence): Petrobangla's current site only
    hosts FY2022-23+ reports, so swap to JV partner Petronet LNG's own annual
    report, which covers the same feasibility-study fact:
    `<ref>[https://www.petronetlng.in/documents/699827/734537/Annual_Report__2017-18.pdf/475bb8fc-690e-f1f0-e537-fbe7a12f1ac5?t=1720013769072 Annual Report 2017-18], Petronet LNG Limited, August 18, 2018.</ref>`
    — PDF text: "Engineers India Limited has prepared Detailed Feasibility
    Report (DFR)… submitted a commercial proposal to Petrobangla." Backup
    mirror if the petronetlng.in path rots:
    <https://www.bseindia.com/bseplus/annualreport/532522/5325220318.pdf>
- [ ] **[QatarEnergy LNG (N)](https://www.gem.wiki/QatarEnergy_LNG_%28N%29)** —
  Hellenic Shipping News "The five stages of LNG grief", dead with 404-only
  archives and no syndicated copy found:
  <http://www.hellenicshippingnews.com/the-five-stages-of-lng-grief/>
  - **Proposed replacement** (medium-high; split into two refs — the sentence
    bundles two separate deals and no single live source covers both):
    - Petronet/RasGas price cut:
      `<ref>[https://www.enerdata.net/publications/daily-energy-news/rasgas-qatar-agrees-cut-price-lng-sold-petronet-india.html Rasgas (Qatar) agrees to cut price of LNG sold to Petronet (India)], Enerdata, January 4, 2016</ref>`
      — "RasGas has agreed to nearly halve the price of LNG sold to Indian LNG
      importer Petronet LNG… as of 1 January 2016." (Dateline is Jan 2016 —
      when the deal closed — not 2017; the wiki sentence cites it as
      background.)
    - Oversupply framing + PGNiG/Qatargas:
      `<ref>[https://gulfnews.com/business/energy/qatargas-agrees-to-double-lng-supplies-to-poland-1.1993823 Qatargas agrees to double LNG supplies to Poland], Gulf News (Reuters), March 14, 2017</ref>`
      — "a deepening global gas glut offers opportunities to bring in cheap
      LNG from Qatar" + Qatargas doubling PGNiG volumes at favorable pricing;
      publish date confirmed via page metadata.
- [ ] **[QatarEnergy LNG (N)](https://www.gem.wiki/QatarEnergy_LNG_%28N%29)** and
  **[(S)](https://www.gem.wiki/QatarEnergy_LNG_%28S%29)** — uk.reuters.com
  factbox (domain retired, no content archive) — try searching reuters.com for
  the headline "Factbox: Oil majors' investments in countries involved in Qatar
  row":
  <http://uk.reuters.com/article/gulf-qatar-energy/factbox-oil-majors-investments-in-countries-involved-in-qatar-row-idUKL8N1JW0KM>
  - **Proposed replacement** (high confidence): no fetchable copy of the
    Reuters factbox survives anywhere (reuters.com/uk.reuters variants,
    Yahoo syndications, PressReader, Al Jazeera's Reuters piece — all dead,
    JS shells, or missing the ownership breakdown). Instead cite Qatargas's
    own archived corporate-structure page, which itemizes the JV shareholders
    and together names exactly the seven companies in the wiki sentence:
    `<ref name="Reuters">[https://web.archive.org/web/20180104172916/http://www.qatargas.com/english/aboutus/corporate-structure Corporate Structure], Qatargas (via Wayback Machine, archived January 4, 2018).</ref>`
    — applies to the same sentence on **both** (N) and (S). Caveats: primary
    source rather than a news wire, and it describes the pre-2022 structure —
    but so does the wiki sentence itself (QatarEnergy took 100% of Qatargas 1
    in Jan 2022), so the sentence may separately deserve a factual update.

## Note

COVERAGE.md's France row records a dead TradeWinds ref left as-is, but no
TradeWinds URL exists on any French LNG page as of 2026-07-23 (the page has
likely been edited since) — treat it as resolved unless it resurfaces.
