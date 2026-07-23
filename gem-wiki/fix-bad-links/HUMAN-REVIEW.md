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

Update 2026-07-23: replacement candidates were researched, staged as
**Proposed replacement** blocks, content-verified (key phrases quoted from
the live/archived page), and — after the user approved all of them — saved
to the wiki (revs 1198408–1198414). Section 2 is now fully resolved.

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
- [x] ~~**Haldia FSRU** — therisk.global project page redirects to an about
  page~~ **Resolved 2026-07-23** (rev 1198408): replaced with the India
  Seatrade News article ("SMP Kolkata awards 30-year licence for floating LNG
  terminal at Haldia", Sept 8, 2025), which matches every supported fact
  (30-yr SMPK concession, Invenire Petrodyne + Excelerate, Haldia Dock
  Complex, 1.5→3 mtpa, launch H2 2027).
- [x] ~~**Gate LNG Terminal** — Techint case-study PDF, dead and never
  archived~~ **Resolved 2026-07-23** (rev 1198409): replaced with the
  Offshore Technology project page (Dec 14, 2011), which confirms everything
  the sentence bundles (2008 start, Sept 2011 service, Techint/SENER,
  Gasunie+Vopak, ~US$1.1B).
- [x] ~~**Terneuzen FSRU** — dead Nasdaq copy of a Dec 2022 Reuters piece, no
  archive or syndication~~ **Resolved 2026-07-23** (rev 1198410): split into
  two refs — Gasunie's own Dec 12, 2022 press release on the
  Terneuzen-candidate-site sentence, and Euronews (citing Reuters, Dec 9,
  2022) on the Bergermeer ~€500M sentence. Caveat stands: the same dead
  Nasdaq URL also lives in auto-generated `autoref_0` used across Tables 1–5
  — out of this project's Background scope, flagged for awareness.
- [x] ~~**Revithoussa LNG Terminal** — dead DESFA page (`?p=11022`), archived
  captures all resolve to homepage/unrelated pages~~ **Resolved 2026-07-23**
  (rev 1198411): split into two refs, one per fact — archived DEPA Annual
  Report 2006 p. 16 (Wayback) for the 1999 completion, archived DESFA
  "Historical Background" page (Wayback, Apr 2018) for the DEPA-subsidiary
  claim.
- [x] ~~**Kutubdia LNG Terminal (Petronet)** — Petrobangla 2018 annual report
  PDF, dead path and never archived~~ **Resolved 2026-07-23** (rev 1198412):
  Petrobangla's site only hosts FY2022-23+ reports, so swapped to JV partner
  Petronet LNG's Annual Report 2017-18, which covers the same
  feasibility-study fact. Backup mirror if the petronetlng.in path rots:
  <https://www.bseindia.com/bseplus/annualreport/532522/5325220318.pdf>
- [x] ~~**QatarEnergy LNG (N)** — Hellenic Shipping News "The five stages of
  LNG grief", dead with 404-only archives and no syndicated copy~~
  **Resolved 2026-07-23** (rev 1198413): split into two refs — Enerdata
  (Jan 4, 2016) on the Petronet/RasGas price cut, Gulf News (Reuters,
  Mar 14, 2017) on the oversupply framing + PGNiG/Qatargas deal.
- [x] ~~**QatarEnergy LNG (N)** and **(S)** — uk.reuters.com factbox (domain
  retired, no content archive, no surviving syndication)~~
  **Resolved 2026-07-23** (revs 1198413/1198414): replaced on both pages
  (keeping `name="Reuters"`) with Qatargas's archived corporate-structure
  page (Wayback, Jan 2018), which itemizes the JV shareholders and names
  exactly the seven companies in the wiki sentence. Caveats noted at review
  time: primary source rather than a news wire, and it describes the
  pre-2022 structure — but so does the wiki sentence itself, which may
  separately deserve a factual update (QatarEnergy took 100% of Qatargas 1
  in Jan 2022).

## Note

COVERAGE.md's France row records a dead TradeWinds ref left as-is, but no
TradeWinds URL exists on any French LNG page as of 2026-07-23 (the page has
likely been edited since) — treat it as resolved unless it resurfaces.
