# Human review queue — refs the automated sweep could not settle

Everything else in [COVERAGE.md](COVERAGE.md) is resolved; these are the leftovers
that need a human. Section 1 items are bot-walled or login-walled URLs — opening
them in a normal browser settles each one in seconds. Section 2 items are
confirmed dead with no usable archive — fixing them means choosing a replacement
source that supports the sentence, which is researcher judgment.

For each item: if the article loads and matches the citation, check it off (no
wiki edit needed). If it's gone, tell Claude and the ref gets repaired like any
other. Sections 1–2 compiled 2026-07-23 and fully resolved; section 3 is the
open queue.

**Don't identify a ref by a bare `[n]`.** Any `[n]` in sections 1–2 is a
*scanner* index — the nth `<ref>` inside the Background section, reuses
included, counting from 1. It is **not** the footnote number the wiki renders,
which counts every ref on the page and so starts with the auto-generated
infobox/table refs: Andrés's scanner `[8]` is displayed footnote `[19]`. The
two never match. Identify refs for a human by URL, `<ref name=...>`, and the
sentence they support, and give the rendered footnote number only with the date
it was true (adding or removing any earlier ref renumbers it).

## 1. Quick browser checks (bot-walled — a click settles it)

- [x] ~~**Hazira LNG Terminal** — Reuters (401 to bots)~~ **Reviewed
  2026-07-23: loads fine in a browser** — bot wall only, no wiki edit needed.
- [x] ~~**Haldia FSRU** — S&P Global (bot-walled)~~ **Reviewed 2026-07-23:
  loads fine in a browser** — bot wall only, no wiki edit needed.
- [x] ~~**Dabhol LNG Terminal** — Offshore Technology (Cloudflare-walled)~~
  **Reviewed 2026-07-23: loads fine in a browser** — bot wall only, no wiki
  edit needed.
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
- [x] ~~**Dabhol LNG Terminal** — ICIS, "India's GAIL puts Dabhol LNG
  terminal expansion plan on hold" (Ajoy K Das, Feb 7, 2014)~~
  **Closed 2026-07-23, left as-is (no wiki edit).** Reviewer confirmed dead
  in a browser; the staged Google queries were then run across engines
  (Brave index + WebSearch; Google, Bing, DuckDuckGo, Mojeek, Startpage all
  captcha/JS-block automation) along with Wayback CDX, ICIS's newer
  `/explore/` URL (empty subscriber shell), the LNG World News 2014 archive,
  and searches for pages citing the article ID/slug — every content hit is
  the GEM wiki itself. Truly unrecoverable. The sentence's second ref
  (archived LNG World News, Apr 2016) still covers the ~60% utilisation +
  breakwater/monsoon claims; only "on hold since 2014" and "high LNG prices"
  rest on the dead ref. If a researcher wants full support, an option is a
  retrospective source (2025 breakwater-completion coverage) plus a slight
  softening of the sentence.

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

## 3. Latin America / Caribbean batch (compiled 2026-07-27)

The full batch is complete (revs 1202600–1202616, 1202625, 1202628–1202638,
1202646–1202675) — 21 countries. Both Andrés dead refs have now been recovered;
what remains is one Peru factual question plus dead refs with no usable archive:
two on Mexico, four on Brazil, and four on Argentina/Chile.

### Dead refs on Andrés — both now resolved

Both sat on **Andrés LNG Terminal** and both turned out to be recoverable,
not dead — a reminder that a "404" host and a 200 Wayback capture can each be
misleading.

- [x] ~~**Andrés — the unnamed AES ref, footnote [19] as rendered**
  (`aes.com/energas-and-aes-break-dominican-republics-reliance-oil`, 404).~~
  **Resolved 2026-07-27** (rev 1202625): not gone, just relocated — a Brave
  search surfaced the live copy at
  `aes.com/energy-insights/energas-and-aes-break-dominican-republics-reliance-oil`
  (200, full case-study body). Simple URL swap; the dead Jun 2023 Wayback
  capture had only been nav chrome, which is why it looked unrecoverable.
- [x] ~~**Andrés — `<ref name=Argus>`, footnote [20] as rendered**
  (`argusmedia.com/en/news/2158007-domrep-converts-oilbased-power-to-gas`, 404).~~
  **Resolved 2026-07-27** (rev 1202638): the researcher supplied a live Argus
  copy of the same article at
  `argusmedia.com/en/news-and-insights/latest-market-news/2123188-domrep-converts-oil-based-power-to-gas-update`
  (200, verified to carry the DomRep/AES/power-to-gas content). The old article
  ID 2158007 was retired; the live path uses ID 2123188 and the `-update` slug.
  Straight URL swap. (The tracker's auto-generated `autoref_9` still cites the
  retired URL with its useless 2024-01-25 error-page capture, but autorefs are
  regenerated and out of scope.)

### Factual question, not a citation question

- [ ] **Peru LNG Terminal** — the sentence listing the project's lenders says
  Banco de Crédito arranged "upwards of $350 million" in local bonds. Its dead
  citation was replaced (rev 1202613) with IJGlobal's project case study, which
  matches every other figure exactly (IFC US$300m, IDB US$400m A-loan +
  US$400m B-loan, K-Exim US$300m, Sace US$250m) but documents a **planned
  US$200 million** BCP local-bond tranche as of Jan 2009, not $350m+. No
  independent source for the $350m figure could be found. Either it reflects a
  later upsizing that needs its own source, or the number wants correcting.

### Mexico batch (compiled 2026-07-27) — dead refs, no archive

Two dead links on the Mexico pages could not be repaired: no Wayback capture
exists and no working relocated/syndicated copy was found. Everything else on
the 17 Mexico pages was fixed (revs 1202628–1202638) or is a live-for-readers
bot-wall left as-is (all `ir.newfortressenergy.com` and `investor.sempra.com`
refs answer an immediate HTTP/2 RST to scripts but load in a browser).

- [ ] **Costa Azul + Vista Pacífico — nasdaq/Reuters "U.S. allows Sempra to
  re-export LNG from Mexico"** (Dec 20 2022;
  `nasdaq.com/articles/u.s.-allows-sempra-to-re-export-lng-from-mexico`, 404 with
  a stray `?utm_source=substack` query). `website=Reuters` in the cite, so this
  is Nasdaq's syndication of a Reuters wire piece. Nasdaq `/articles/` URLs are
  not archived (Wayback has nothing), and the two pages share the same dead ref.
  Needs a live Reuters original or another syndication. Ready-made searches:
  - `"U.S. allows Sempra to re-export LNG from Mexico" Reuters`
  - `Sempra re-export LNG Mexico December 2022 Reuters`
- [ ] **Progreso LNG Terminal — NGV Journal "Korean energy company will build
  LNG terminal in Yucatan"** (Aug 18 2016;
  `ngvjournal.com/s1-news/c7-lng-h2-blends/…-in-yucatan/`, 404). The site
  reorganized and the article was never archived (Wayback has no capture of the
  Yucatan slug). A 2016 niche trade item; low stakes. Ready-made searches:
  - `Korea LNG terminal Progreso Yucatan 2016`
  - `NGV Journal Korean company LNG terminal Yucatan`

### Brazil batch (compiled 2026-07-27) — dead refs, no archive

Four dead links on the Brazil pages could not be repaired: no usable Wayback
capture exists (or only an error-page capture) and no working relocated copy
was found. Everything else on the 25 Brazil pages was fixed (revs 1202646–1202665)
or is a live-for-readers block left as-is — most notably all 20 `epbr.com.br`
refs, which return a Cloudflare 522 gateway-timeout to datacenter IPs (via both
local curl and WebFetch's separate network path) but are a live Brazilian energy
publisher, not down.

- [ ] **Bahia FSRU — Nasdaq/Reuters "Brazil's Petrobras disqualifies
  Excelerate Energy's bid on LNG lease"** (Jun 21 2021;
  `nasdaq.com/articles/brazils-petrobras-disqualifies-excelerate-energys-bid-on-lng-lease-2021-06-21`,
  404). Nasdaq `/articles/` URLs are not archived (Wayback has nothing). Needs a
  live Reuters original or another syndication. Ready-made searches:
  - `Petrobras disqualifies Excelerate Energy LNG lease bid 2021 Reuters`
  - `"Excelerate" Petrobras Bahia LNG lease disqualified June 2021`
- [ ] **Presidente Kennedy FSRU — ABOL Brasil "Polimix planeja iniciar obra de
  US$ 650 milhões em porto no ES"** (`abolbrasil.org.br/posts/polimix-planeja-iniciar-obra-de-us-650-milhoes-em-porto-no-es`,
  404; the only Wayback capture is a 403 error page). Ready-made searches:
  - `Polimix porto Presidente Kennedy US$ 650 milhões`
  - `Polimix terminal GNL Presidente Kennedy Espírito Santo`
- [ ] **Tergás Rio Grande LNG Terminal — SEMA/RS "FEPAM recebe EIA-RIMA para
  obras do terminal de gás e termelétrica em Rio Grande"**
  (`sema.rs.gov.br/fepam-recebe-eia-rima-para-obras-do-terminal-de-gas-e-termeletrica-em-rio-grande-5862c670daf5e`,
  404, never archived). State-government press page; likely reorganized.
  Ready-made searches:
  - `FEPAM EIA-RIMA terminal gás termelétrica Rio Grande`
  - `SEMA RS terminal GNL Rio Grande EIA RIMA`
- [ ] **Terminal Gás Sul FSRU — Itajaí Naval "Autorizada a construção do
  Terminal Gás Sul na Baía da Babitonga"**
  (`itajainaval.com.br/autorizada-a-construcao-do-terminal-gas-sul-na-baia-da-babitonga`,
  times out / never archived). Ready-made searches:
  - `Terminal Gás Sul construção autorizada Baía da Babitonga`
  - `TGS terminal GNL São Francisco do Sul autorização construção`

### Argentina / Chile batch (compiled 2026-07-27) — dead refs, no archive

Four dead links across the Argentina and Chile pages have no usable Wayback
capture and no working relocated copy. Everything else on those pages was fixed
(revs 1202666–1202675) or is a live-for-readers bot-wall/paywall left as-is.

- [ ] **TGS Puerto Galván LNG Terminal — Petrol News "noticia.php?r=46829"**
  (`petrolnews.net/noticia.php?r=46829`, host won't connect; never archived — the
  numeric article ID gives no way to guess the topic). Ready-made searches:
  - `Petrol News TGS Puerto Galván GNL`
  - `TGS Puerto Galván terminal GNL Bahía Blanca`
- [ ] **TGS Puerto Galván LNG Terminal — Financial Post "TGS halts Argentina LNG
  plant as state-run project seeks backers"**
  (`financialpost.com/pmn/business-pmn/tgs-halts-argentina-lng-plant-as-state-run-project-seeks-backers`,
  410 Gone; the only Wayback capture is a 403 error page). It's a Reuters/Bloomberg
  wire piece syndicated by Financial Post — a live original likely exists. Ready-made
  searches:
  - `"TGS halts Argentina LNG plant" state-run project backers`
  - `Transportadora de Gas del Sur halts LNG plant 2024 Reuters`
- [ ] **Talcahuano FSRU — GNL Global "Corte Suprema de Chile obliga a Gasoducto
  del Pacífico…"** (`gnlglobal.com/mercados/america-latina-y-el-caribe/corte-suprema-de-chile-obliga-a-gasoducto-del-pacifico-a-dar-respuesta-fundada-a-gnl-talcahuano-para-no-aceptar-conexion/`,
  404, never archived). Ready-made searches:
  - `Corte Suprema Gasoducto del Pacífico GNL Talcahuano conexión`
  - `GNL Talcahuano Gasoducto del Pacífico fallo Corte Suprema`
- [ ] **Talcahuano FSRU — Canal 9 Bío Bío "GNL Talcahuano irá a la Corte Suprema
  para salvar proyecto…"** (`canal9.cl/programas/noticias/2021/11/19/gnl-talcahuano-ira-a-la-corte-suprema-para-salvar-proyecto-de-gas-natural.shtml`;
  original path 404s, the site moved content to `/episodios/…` which also 404s; never
  archived). Ready-made searches:
  - `GNL Talcahuano Corte Suprema salvar proyecto Canal 9`
  - `GNL Talcahuano recurso Corte Suprema noviembre 2021`

## Note

COVERAGE.md's France row records a dead TradeWinds ref left as-is, but no
TradeWinds URL exists on any French LNG page as of 2026-07-23 (the page has
likely been edited since) — treat it as resolved unless it resurfaces.
