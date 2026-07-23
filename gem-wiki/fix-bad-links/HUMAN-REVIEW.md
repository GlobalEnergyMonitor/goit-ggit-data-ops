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
- [ ] **[Dabhol](https://www.gem.wiki/Dabhol_LNG_Terminal)** /
  **[Hazira](https://www.gem.wiki/Hazira_LNG_Terminal)** /
  **[AMNS Suvali](https://www.gem.wiki/AMNS_Suvali_LNG_Terminal)** — Argus
  AMNS-Suvali article (a Dec 2024 Wayback snapshot confirms the content, but the
  live URL flipped from 403 to 404 for bots in July 2026 — check whether the
  article still exists for humans):
  <https://www.argusmedia.com/en/news-and-insights/latest-market-news/2639678-india-s-amns-in-talks-to-build-suvali-lng-terminal>
- [ ] **[Dhamra LNG Terminal](https://www.gem.wiki/Dhamra_LNG_Terminal)** —
  Argus (blocks bots, never archived — genuinely unknown whether alive):
  <https://www.argusmedia.com/en/news/2095088-indias-odisha-state-extends-covid19-lockdown>
- [ ] **[Kutubdia (Reliance) FSRU](https://www.gem.wiki/Kutubdia_%28Reliance%29_FSRU)**
  — S&P Global Platts (bot-walled, no content archive; headline matches):
  <https://www.spglobal.com/platts/en/market-insights/latest-news/natural-gas/101918-bangladesh-terminates-fsru-talks-with-indias-reliance-power>
- [ ] **[Jaigarh LNG Terminal](https://www.gem.wiki/Jaigarh_LNG_Terminal)** —
  the cited Hellenic Shipping News copy is dead; it reprinted an S&P Global
  Platts piece ("India LNG buyers spoilt for choice as China woes create problem
  of plenty") that is bot-walled — search spglobal.com for the original:
  <https://www.hellenicshippingnews.com/india-lng-buyers-spoilt-for-choice-as-china-woes-create-problem-of-plenty/>
- [ ] **[Mina Al-Ahmadi LNG Terminal](https://www.gem.wiki/Mina_Al-Ahmadi_LNG_Terminal)**
  — the cited Google-cache copy is dead; the Energy Institute original
  ("FSRUs – the great game changer") is 403 to bots and Wayback only has 404
  captures — try it in a browser, or the EI site search:
  <https://www.energyinst.org/documents/5092>
- [ ] **[Dabhol LNG Terminal](https://www.gem.wiki/Dabhol_LNG_Terminal)** —
  ICIS, "India's GAIL puts Dabhol LNG terminal expansion plan on hold" (Feb
  2014). The live URL serves an empty page shell (likely a login wall), it was
  never archived, and no syndicated copy exists — needs an ICIS
  subscription/browser check:
  <https://www.icis.com/resources/news/2014/02/07/9751104/india-s-gail-puts-dabhol-lng-terminal-expansion-plan-on-hold/>

## 2. Dead refs needing a replacement source (researcher judgment)

- [ ] **[Karwar FSRU](https://www.gem.wiki/Karwar_FSRU)** — pipelineme.com is
  gone and this is the page's **only** Background citation (highest priority):
  <https://www.pipelineme.com/news/international-news/2017/01/hyundai-heavy-industries-wins-563-contract-to-build-asia-s-largest-fsru-in-karnataka/>
- [ ] **[Kukrahati LNG Terminal](https://www.gem.wiki/Kukrahati_LNG_Terminal)** —
  environmentclearance.nic.in risk-assessment PDF, unreachable and never archived:
  <https://environmentclearance.nic.in/writereaddata/online/RiskAssessment/08032019F0QCTPH6RiskAssessment.pdf>
- [ ] **[Haldia FSRU](https://www.gem.wiki/Haldia_FSRU)** — therisk.global
  project page now redirects to an about page:
  <https://therisk.global/energy/haldia-fsru-project/>
- [ ] **[Gate LNG Terminal](https://www.gem.wiki/Gate_LNG_Terminal)** — Techint
  case-study PDF, dead and never archived:
  <http://www.techint-ingenieria.com/sites/default/files/upload/publications/files/Project%20Cse%20Study%20Gate.pdf>
- [ ] **[Terneuzen FSRU](https://www.gem.wiki/Terneuzen_FSRU)** — dead Nasdaq
  copy of a Dec 2022 Reuters piece (Gasunie eyeing Terneuzen), no archive or
  other syndication found:
  <https://www.nasdaq.com/articles/dutch-grid-operator-gasunie-looking-at-terneuzen-for-new-lng-capacity>
- [ ] **[Revithoussa LNG Terminal](https://www.gem.wiki/Revithoussa_LNG_Terminal)**
  — dead DESFA page; live DESFA pages don't confirm the 1999/DEPA claims it
  supported: <http://www.desfa.gr/?p=11022&lang=en>
- [ ] **[Kutubdia LNG Terminal (Petronet)](https://www.gem.wiki/Kutubdia_LNG_Terminal_%28Petronet%29)**
  — Petrobangla 2018 annual report PDF, dead path and never archived (the
  report may have moved elsewhere on petrobangla.org.bd):
  <https://petrobangla.org.bd/admin/attachment/webtable/1263_upload_0.pdf>
- [ ] **[QatarEnergy LNG (N)](https://www.gem.wiki/QatarEnergy_LNG_%28N%29)** —
  Hellenic Shipping News "The five stages of LNG grief", dead with 404-only
  archives and no syndicated copy found:
  <http://www.hellenicshippingnews.com/the-five-stages-of-lng-grief/>
- [ ] **[QatarEnergy LNG (N)](https://www.gem.wiki/QatarEnergy_LNG_%28N%29)** and
  **[(S)](https://www.gem.wiki/QatarEnergy_LNG_%28S%29)** — uk.reuters.com
  factbox (domain retired, no content archive) — try searching reuters.com for
  the headline "Factbox: Oil majors' investments in countries involved in Qatar
  row":
  <http://uk.reuters.com/article/gulf-qatar-energy/factbox-oil-majors-investments-in-countries-involved-in-qatar-row-idUKL8N1JW0KM>

## Note

COVERAGE.md's France row records a dead TradeWinds ref left as-is, but no
TradeWinds URL exists on any French LNG page as of 2026-07-23 (the page has
likely been edited since) — treat it as resolved unless it resurfaces.
