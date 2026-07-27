# Human review queue — refs the automated sweep could not settle

Everything else in [COVERAGE.md](COVERAGE.md) is resolved; these are the leftovers
that need a human. Section 1 items are bot-walled or login-walled URLs — opening
them in a normal browser settles each one in seconds. Section 2 items are
confirmed dead with no usable archive — fixing them means choosing a replacement
source that supports the sentence, which is researcher judgment.

For each item: if the article loads and matches the citation, check it off (no
wiki edit needed). If it's gone, tell Claude and the ref gets repaired like any
other. Sections 1–2 compiled 2026-07-23 and fully resolved; section 3 (Latin
America, compiled 2026-07-27) is now fully resolved too — the whole queue is
clear as of 2026-07-27.

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
1202646–1202675) — 21 countries. A follow-up inline research pass on 2026-07-27
(revs 1202676–1202682) recovered eight of the ten "dead, no archive" refs via
live relocated URLs, wire/syndication copies, or the same article on a live
host. The remaining three — one Peru factual question and two Brazil refs
(Tergás, Terminal Gás Sul) — were resolved by the researcher on 2026-07-27.
**Section 3 is now fully resolved.**

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

- [x] **Peru LNG Terminal** — **Resolved by the researcher 2026-07-27.** For the
  record: the sentence listing the project's lenders said Banco de Crédito
  arranged "upwards of $350 million" in local bonds. Its dead citation was
  replaced (rev 1202613) with IJGlobal's project case study, which matches every
  other figure exactly (IFC US$300m, IDB US$400m A-loan + US$400m B-loan, K-Exim
  US$300m, Sace US$250m) but documents a **planned US$200 million** BCP
  local-bond tranche as of Jan 2009, not $350m+; no independent source for the
  $350m figure was found in the automated pass.

### Mexico batch (compiled 2026-07-27) — dead refs, no archive

Both Mexico dead links were recovered on the 2026-07-27 follow-up pass and are
now resolved (below). Everything else on the 17 Mexico pages was fixed (revs
1202628–1202638) or is a live-for-readers bot-wall left as-is (all
`ir.newfortressenergy.com` and `investor.sempra.com` refs answer an immediate
HTTP/2 RST to scripts but load in a browser).

- [x] ~~**Costa Azul + Vista Pacífico — nasdaq/Reuters "U.S. allows Sempra to
  re-export LNG from Mexico"** (Dec 20 2022)~~ **Resolved 2026-07-27** (revs
  1202676/1202677): the same Reuters wire piece is live at Natural Gas World
  (`naturalgasworld.com/u.s.-permits-sempra-to-re-export-lng-from-mexico-102750`),
  verified to carry the post-Ukraine-invasion re-export framing. Swapped in on
  both pages (`website=Natural Gas World (Reuters)`, `name=":5"` kept).
- [x] ~~**Progreso LNG Terminal — NGV Journal "Korean energy company will build
  LNG terminal in Yucatan"** (Aug 18 2016)~~ **Resolved 2026-07-27** (rev
  1202678): replaced with Offshore Energy's coverage of the same Kogas plan
  (`offshore-energy.biz/kogas-plans-mexico-lng-import-terminal/`, Aug 12 2016),
  which confirms the feasibility-study step the sentence rests on.

### Brazil batch (compiled 2026-07-27) — dead refs, no archive

Two of the four Brazil dead links were recovered on the 2026-07-27 follow-up
pass (below); the other two (Tergás, Terminal Gás Sul) were unrecoverable/
mismatched and were closed by the researcher on 2026-07-27. Everything
else on the 25 Brazil pages was fixed (revs 1202646–1202665) or is a
live-for-readers block left as-is — most notably all 20 `epbr.com.br` refs,
which return a Cloudflare 522 gateway-timeout to datacenter IPs (via both local
curl and WebFetch's separate network path) but are a live Brazilian energy
publisher, not down.

- [x] ~~**Bahia FSRU — Nasdaq/Reuters "Brazil's Petrobras disqualifies
  Excelerate Energy's bid on LNG lease"** (Jun 21 2021)~~ **Resolved 2026-07-27**
  (rev 1202679): replaced with JPT (Journal of Petroleum Technology), "Petrobras
  Disqualifies Excelerate's Bid on LNG Terminal" (Jun 22 2021, reporting Reuters;
  `jpt.spe.org/petrobras-disqualifies-excelerates-bid-on-lng-terminal`), which
  confirms the disqualification and Excelerate being the sole bidder. This was a
  bare `[url text]` link, so the display text and byline were rewritten to
  attribute JPT honestly rather than keep the old Reuters headline.
- [x] ~~**Presidente Kennedy FSRU — ABOL Brasil "Polimix planeja iniciar obra de
  US$ 650 milhões em porto no ES"**~~ **Resolved 2026-07-27** (rev 1202680): not
  gone, just relocated — the same article is live at
  `abolbrasil.org.br/noticias/noticias/polimix-planeja-iniciar-obra-de-us-650-milhoes-em-porto-no-es`
  (identical title/date). Straight URL swap; the `/posts/` path was retired.
- [x] **Tergás Rio Grande LNG Terminal — SEMA/RS "FEPAM recebe EIA-RIMA…"** —
  **Resolved by the researcher 2026-07-27.** For the record: sema.rs.gov.br was
  404 + never archived + not relocated (all `estado.rs.gov.br` slug variants
  404). The one live candidate — tnpetroleo, "Rio Grande sediará primeiro
  terminal de GNL on-shore do Brasil" (Dec 17 2008) — was on-topic but stated a
  **>US$1.2 billion** projected investment vs the wiki sentence's "in 2009 an
  R$3 billion investment was allegedly projected", so the automated pass left it
  for a figure-reconciliation call rather than swap in a mismatched number.
- [x] **Terminal Gás Sul FSRU — Itajaí Naval "Autorizada a construção…"** —
  **Resolved by the researcher 2026-07-27.** For the record: itajainaval timed
  out / never archived, and no clean source for the specific Nov-2021 ANP
  *construction* authorization surfaced — the live candidates (megawhat, ndmais)
  both cover a *later, different* event (the Jan 31 2024 ANP authorization to
  *import* 15M m³/day, published in the DOU). The sentence's core "construction
  began Nov 2021" fact is separately carried by a live co-ref (oec-eng.com,
  "Tenenge starts construction…", Nov 17 2021).

### Argentina / Chile batch (compiled 2026-07-27) — dead refs, no archive

All four Argentina/Chile dead links were recovered on the 2026-07-27 follow-up
pass and are now resolved (below). Everything else on those pages was fixed
(revs 1202666–1202675) or is a live-for-readers bot-wall/paywall left as-is.

- [x] ~~**TGS Puerto Galván LNG Terminal — Petrol News "noticia.php?r=46829"**~~
  **Resolved 2026-07-27** (rev 1202681, `name=":2"`): the same story is live at
  El Cronista, "GNL: Excelerate se aleja de su proyecto con TGS y sueña con el
  negocio que abrirá la planta de YPF" (May 31 2024;
  `cronista.com/negocios/gnl-excelerate-se-aleja-de-su-proyecto-con-tgs-…`),
  which carries the Excelerate-leaves-TGS-for-YPF/Petronas narrative the
  sentence rests on.
- [x] ~~**TGS Puerto Galván LNG Terminal — Financial Post "TGS halts Argentina
  LNG plant as state-run project seeks backers"**~~ **Resolved 2026-07-27** (rev
  1202681): replaced with Bloomberg Línea's official copy of the same wire piece
  (May 8 2024;
  `bloomberglinea.com/latinoamerica/argentina/tgs-paraliza-proyecto-de-gnl-en-argentina-mientras-ypf-busca-patrocinadores/`).
- [x] ~~**Talcahuano FSRU — GNL Global "Corte Suprema de Chile obliga a Gasoducto
  del Pacífico…"**~~ **Resolved 2026-07-27** (rev 1202682): not gone, just
  relocated — the same article is live at
  `gnlglobal.com/corte-suprema-de-chile-obliga-a-gasoducto-del-pacifico-a-dar-respuesta-fundada-a-gnl-talcahuano-para-no-aceptar-conexion/`
  (the `/mercados/america-latina-y-el-caribe/` path prefix was dropped). Straight
  URL swap, same title/date.
- [x] ~~**Talcahuano FSRU — Canal 9 Bío Bío "GNL Talcahuano irá a la Corte
  Suprema para salvar proyecto…"**~~ **Resolved 2026-07-27** (rev 1202682):
  canal9.cl 404s, but OLCA syndicated the same Canal 9 article verbatim (same
  title/date, credits Canal 9;`olca.cl/articulo/nota.php?id=109072`). Swapped in
  as `website=Canal 9 Bío Bío Televisión (vía OLCA)`.

## Note

COVERAGE.md's France row records a dead TradeWinds ref left as-is, but no
TradeWinds URL exists on any French LNG page as of 2026-07-23 (the page has
likely been edited since) — treat it as resolved unless it resurfaces.
