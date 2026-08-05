# Human review queue — refs the automated sweep could not settle

Everything else in [COVERAGE.md](COVERAGE.md) is resolved; these are the leftovers
that need a human. Section 1 items are bot-walled or login-walled URLs — opening
them in a normal browser settles each one in seconds. Section 2 items are
confirmed dead with no usable archive — fixing them means choosing a replacement
source that supports the sentence, which is researcher judgment.

For each item: if the article loads and matches the citation, check it off (no
wiki edit needed). If it's gone, tell Claude and the ref gets repaired like any
other. Sections 1–2 compiled 2026-07-23 and fully resolved; section 3 (Latin
America, compiled 2026-07-27) is fully resolved too. Section 4 (Italy, Spain,
Germany, compiled 2026-07-28) is a different shape from the earlier sections:
most of its items are not dead links at all but *claim-vs-source mismatches* — a
figure or date in the wiki sentence that no reachable source states.

**Sections 5 (United States) and 6 (China) are open.** Section 5's repair work is
finished — all six waves are saved and the US row in COVERAGE.md is marked done —
but its human items remain. Its shape differs again from the earlier sections:
most items are neither dead links nor claim mismatches but *unverifiable-by-script*
pages (bot walls and paywall soft-404s that are almost certainly fine as cited)
plus citations that never carried a URL at all. Read the table at the head of
section 5 first: it says which groups need **no repair** (73 of 112 archive-queue
URLs), so the genuinely open work is much smaller than the item count suggests.

Sections 1–4 are closed. Section 4's *one-way* items — where the sources agreed with
each other and disagreed with the sentence, leaving exactly one direction the
correction could go — were applied on 2026-07-29, half by hand and half by
`fix_prose_isg.py`. The three that were parked that day as claims with *no source
at all* were then searched out and closed the same day by `fix_prose_open3.py`:
two of them turned out to have sources nobody had gone looking for, and the third
had a real source that supported the substance but not the quotation, so the
quotation went. None of the section-4 corrections required a change to the GEM
database; the reasoning is recorded per item.

(Prose is no longer out of reach for the tooling, but it stays deliberately
narrow: `fixlib.build_prose` will rewrite a sentence only where a fix is one-way
in that sense, and only against a quoted snippet that occurs exactly once.
Anything softer than that still belongs on this list.)

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
  negocio que abrirá la planta de YPF" (May 31 2024), which carries the
  Excelerate-leaves-TGS-for-YPF/Petronas narrative the sentence rests on:
  https://www.cronista.com/negocios/gnl-excelerate-se-aleja-de-su-proyecto-con-tgs-y-suena-con-el-negocio-que-abrira-la-planta-de-ypf/
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

## 4. Italy / Spain / Germany (compiled 2026-07-28)

Identify each ref by URL and the sentence it supports, not by a number — see the
warning above.

### 4a. Claim-vs-source mismatches (prose decision, not a link swap)

- [x] ~~**Falconara Marittima LNG Terminal — "The project would cost about $250
  million."**~~ **Resolved by hand 2026-07-29** (rev 1206806) — now €200 million,
  matching the LNG Industry (20 July 2011) replacement ref. The GEM database was
  already right (`Cost` = 200,000,000 EUR, `CostYear` 2011, cited to the same
  article), so the wiki was the lone outlier.
- [x] ~~**Priolo Augusta LNG Terminal — "$500 million" project cost.**~~
  **Resolved 2026-07-29** (rev 1206816) — now **€400 million**, cited to
  [Informare](https://www.informare.it/news/gennews/2005/20050354.asp), 23 Feb.
  2005: *"un investimento di circa 400 milioni di euro"*, alongside the 8 bcm/y
  capacity that matches GEM's record. The ICIS ref the figure hung on serves
  only a 212-byte Incapsula bot-challenge stub and has no Wayback snapshot, so
  it could never have supported $500m; it is kept anyway, because bot-walled is
  not dead and it still stands behind the 2005 announcement in the same
  sentence. Worth knowing that the number drifts in later reporting —
  MilanoFinanza has €500m in 2009, €450m in Sept. 2012 and €800m in Nov. 2012 —
  so the sentence is now explicitly the announcement-time figure. No database
  change: GEM has no `Cost` for Priolo at all.
- [x] ~~**Priolo Augusta LNG Terminal — Shell's withdrawal dated December 2012.**~~
  **Resolved 2026-07-29** (rev 1206811) — now November 2012. Milano Finanza's
  piece *reporting* the withdrawal is dated 6 Nov. 2012, so December was not
  merely unsupported, it postdated the source; ERG's July 2012 exit brackets it
  from the other side. GEM's `ShelvedYear` (2012) is unaffected by a month move.
- [x] ~~**Gioia Tauro LNG Terminal — €6.8M vs €6.9M** for the Medgas Italia
  29.22% stake.~~ **Resolved by hand 2026-07-29** (rev 1206809) — now €6.9
  million, matching the Staffetta Quotidiana ref already on the page (*"base
  d'asta di poco meno di **6,9 milioni** di euro e rialzi di almeno 100.000
  euro"*). No live source anywhere stated 6.8. Not a database matter: GEM's
  `Cost` field holds the €1bn project cost, not the price of a stake.
- [x] ~~**Oristano FSRU — "methanization of Sardinia … increasing storage capacity
  by approximately ten times".**~~ **Resolved 2026-07-28** (rev 1206803). The LNG
  Prime article is live but subscriber-walled past its two-sentence lead, which
  does not contain the clause; Snam's own 8 Oct 2025 release states both the
  methanization/ten-times clause and the transmission-network/provinces sentence
  word for word and was added alongside. (Verifying that URL needs a trick:
  snam.it is an Adobe AEM single-page app whose static HTML is an empty shell —
  swap `.html` for `.model.json` on the same path to get the rendered body.)
- [x] ~~**Huelva LNG Terminal — "expansions completed in 1992, 2002, 2004, 2006,
  and 2013".**~~ **Resolved by hand 2026-07-29** (rev 1206805) — the unverifiable
  expansion-year list is gone. (Of the five, 2004 and 2006 looked like the same
  fourth-tank project counted twice, and 1992 and 2013 were not found at all.)
  No database impact: GEM carries `ActualStartYear` 1988 and no second or third
  start year, so the disputed years were never in the tracker.
- [x] ~~**El Musel LNG Terminal — "opposition from local political groups"
  clause.**~~ **Resolved 2026-07-29** (rev 1206817) — the Bunkerspot article that
  backed the sentence is dead and its only snapshot is a stub, and the Bunker
  Index substitute covers the gazette approval but not the opposition; two
  sources that cover the opposition were found and the clause now names the
  groups, because the sources do.
  [Europa Press](https://www.europapress.es/asturias/noticia-xsp-lamenta-autorizacion-bunkering-musel-pone-bandeja-legalizacion-regasificadora-20170307132752.html)
  (7 Mar. 2017, the wire original) has Xixón Sí Puede's David Alonso saying the
  Port Authority *"ha puesto en bandeja al Consejo de Ministros la legalización
  de la regasificadora … declarada ilegal por el Tribunal Supremo"*;
  [El Comercio](https://www.elcomercio.es/gijon/201703/08/xixon-puede-creen-paso-20170308000450-v.html)
  (8 Mar. 2017) adds Izquierda Unida and the *"primer paso"* framing. Both are
  independent and both serve the full body — El Comercio's is in its JSON-LD
  even though the rendered page looks walled. The *eleconomista* copy is 403
  behind Akamai with no snapshot and was not needed. No database change: an
  objection by a city council group maps to no GEM field.
- [x] ~~**Tenerife LNG Terminal — Loadstar article dated 12 Nov 2014.**~~
  **Resolved by hand 2026-07-29** (rev 1206810) — the sentence now reads December
  2014, which the article supports for the right reason: 11 Dec 2014 is its
  *publication* date, but the body says "Confirmation came in a letter received
  from the EU on Monday" (8 Dec 2014), so the event itself was in December. An EU
  feasibility-study grant maps to no GEM field, so nothing to change there.
- [x] ~~**Wilhelmshaven FSRU — 2005 capacity given as "8 mtpa".**~~ **Resolved by
  hand 2026-07-29** (rev 1206807) — now 10 bcm/y, per Energy Intelligence. Not a
  database matter: GEM has no record of the 2005 E.ON proposal at all (all three
  Wilhelmshaven records are 2022-vintage), so the figure lived only in Background.
- [x] ~~**Lubmin FSRU — the *Neptune* "arrived at the terminal site" in November
  2022.**~~ **Resolved 2026-07-29** (rev 1206812) — split into its two real legs.
  November now points at **Mukran**, which is what the existing AP ref actually
  says ("arrived off the Baltic Sea port of Mukran"; "due to begin operation in
  nearby Lubmin"), with the reason it stopped there (Lubmin's port is too shallow
  and too small); the **16 December 2022** Lubmin berthing is a new sentence
  carrying Maritime Executive and Offshore Energy. GEM is unaffected — a vessel
  arrival is not a field, and `ActualStartYear` January 2023 is consistent with a
  mid-December berthing.

### 4b. Confirmed dead, no usable archive, no substitute found

- [x] ~~**Gioia Tauro LNG Terminal — `pvp.giustizia.it` auction notice
  (LOTTO UNICO, Oct 2020).**~~ **Resolved 2026-07-28** (rev 1206802) — dropped as
  redundant. The notice is dead and a CDX sweep confirms it was never archived,
  but the first reading of its companion ref was wrong: Staffetta Quotidiana
  (`articolo.aspx?id=345982`) is not headline-only. It serves a full teaser
  paragraph ahead of the subscriber gate, and that teaser carries the 29.22%
  stake, the auction date, the €100,000 minimum increments and the bankruptcy
  docket (262/2018) — everything the dead notice was cited for except the
  amount, which it gives as 6,9 rather than 6,8 (see 4a). Lesson recorded in
  README step 4: read what the companion actually serves, not just its
  `<title>`, before calling redundancy impossible.
- [x] ~~**Brunsbüttel LNG Terminal — the Krebber quote is now unsourced.**~~
  **Resolved 2026-07-29** (rev 1206818) — the quotation is gone and the
  substance behind it is sourced. Its citation had pointed at a Montel URL
  (`/es/story/rwe-expects-lignite-closure-deal-by-year-end/`) about an unrelated
  RWE lignite story with **zero Wayback snapshots**: mismatched when it was laid
  down, not merely rotted. Searching on the quotation's own wording returns
  exactly one page on the indexed web — gem.wiki itself — so it has no
  independent home and could not be cited. What does survive is the occasion it
  came from, RWE's Q3 2020 earnings call:
  [Dow Jones Newswires](https://www.finanznachrichten.de/nachrichten-2020-11/51226518-rwe-will-ueber-lng-terminal-brunsbuettel-nun-erst-2021-entscheiden-015.htm)
  (12 Nov. 2020) has Krebber on the Covid-19 slip, the H1-2021 decision, being
  *"sehr optimistisch"* of getting *"genug Lieferverträge … um das Projekt über
  die Ziellinie zu bringen"*, and all partners still expecting Germany's first
  import terminal;
  [Global LNG Info](https://www.globallnginfo.com/ShowNews.aspx?NewsID=ANTA0ODQ5NTc0ODQ4NDg0ODQ4NTE1MQ==)
  (update of 18 Nov. 2020) corroborates the delay and the H1-2021 FID in
  English. The sentence is now reported speech rather than a quotation, because
  the only verifiable wording is German and putting a back-translation inside
  quotation marks would be inventing a quote — and because the German carries
  supply contracts only, never the "offtake contracts" the old quote claimed.
  Both sources also call him **CFO**, which is the second fix here: Krebber did
  not become CEO until May 2021, so "RWE's CEO" was wrong independently of the
  sourcing. No database change: GEM's `Cost` for Brunsbüttel is an unrelated
  2024 figure, and an executive's remarks map to no field.

### 4c. Quick browser checks

- [x] ~~**Stade LNG Terminal — Bloomberg article** (bot-walled to scripts).~~
  **Checked by hand 2026-07-29** — fine as cited.

## 5. United States (compiled 2026-07-28, rewritten 2026-07-29)

108 pages, 1232 Background refs. **68 pages edited across six waves, 0 cite
errors anywhere** — revs 1206820–1206907 (waves 1–5) and 1206935–1206952
(wave 6, the archive wave, saved 2026-07-29). **Open items below.**

Every ref listed in this section carries its **full URL on its own line**, plus
the page citing it and the sentence it supports. Nothing here needs to be looked
up in `working-files/` or on the wiki — click the URL and the item is settled.
(The `supports:` quote is a text window around the ref, so it often starts or
ends mid-sentence; ellipses mark where.)

The archive wave started from a 118-URL queue and ended with 20 snapshots on 18
pages. What happened to the other 98 is the useful part of this section, because
**73 of them need no repair at all**. Six had already been fixed by waves 1–5
(the queue was built before them), leaving 112 live:

| Disposition | n | No repair needed? | Where |
|---|---|---|---|
| content-validated snapshot, swapped in | 20 | — applied | revs 1206935–1206952 |
| bot-walled (401/403), no archive | 42 | ✅ alive, publisher blocks bots | 5a |
| live 200 — paywall or JS shell | 10 | ✅ alive as cited | 5a |
| only cited by a bot-owned `autoref_*` | 2 | ✅ out of scope | 5f |
| URL-normalization false positive | 1 | ✅ never broken | 5f |
| had a capture, but it is not the document | 16 | ❌ | 5g |
| genuinely dead, no usable archive | 21 | ❌ | 5h |
| | **112** | | |

(20 URLs became 22 ref-fixes because two captures are cited on two pages each —
the Bloomberg Sabine Pass piece and the S&P Bluewater piece.)

The 42 bot walls are the single biggest group and the most important thing not to
mistake for rot: a 401/403 to a script is a publisher refusing automation, not a
dead page.

**A caution that applies to every list below:** don't identify a ref by a bare
`[n]`. That index is the *scanner's* — the nth `<ref>` in Background, reuses
included, counting from 1 — and is not the footnote number a reader sees. Refs
here are identified by URL, page, and the sentence they support.

### 5a. A click settles it — 57 refs, none expected to need repair

Nothing in 5a is known to be broken. Every one of these returns either a bot
wall (401/403) or a live 200 that a script cannot read — a paywall shell, a
JavaScript-rendered page, or a soft 404. A script cannot tell any of them from
rot, and a human with a browser settles each in seconds. **The expected outcome
for almost all of them is "alive, fine as cited."**

#### The 42 bot-walled refs — 401/403 and no Wayback capture

Nothing automated can settle these: the publisher refuses the fetch *and* there
is no archive to fall back on. They are grouped by publisher because that is the
level the behaviour lives at — one spot-check per publisher is worth far more
than that many individual clicks — but every URL is listed in full so you
never have to reconstruct one.

**reuters.com — 22 refs, all 401.** Reuters blocks datacenter traffic
wholesale; every other batch in this project hit the same wall (see the France
and Brazil rows in COVERAGE.md). **One check settles all 22.**

- [ ] **Calcasieu Pass LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/venture-global-lng-can-start-new-units-lng-plant-says-ferc-2023-10-26/?utm_medium=email&_hsmi=281130442&_hsenc=p2ANqtz-_SfdNRl_JvLFI2YuQTXS0urOALTV3Fhx9RNeTVPb2MVDRn9UEIi1XhtXNjwQh2kHYjGWhdkRvsXxlF3DivMel-Jz9Zajh7rXEl40_eEDE94OK7da0&utm_content=281130442&utm_source=hs_email
      supports: “October 2023, FERC approved of a plan for Venture Global to
        turn on three processing trains at the facility while work on repairing
        generation units continued.”

- [ ] **Cameron LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/ferc-grants-five-year-extension-sempras-cameron-lng-project-louisiana-2025-11-24/?utm_source=chatgpt.com
      supports: “In November 2025, Cameron LNG received a five year extension
        from FERC to finish construction on Cameron LNG Phase 2 by 2033.”

- [ ] **Commonwealth LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/caturus-start-construction-major-us-lng-facility-after-securing-975-billion-2026-05-15/
      supports: “…g, procurement, and construction portion of the work. At this
        time, the project was considered to be under construction and expected
        to begin operating in 2030.”

- [ ] **Corpus Christi LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/cheniere-submits-application-build-massive-lng-plant-texas-2026-02-05/?utm_source=chatgpt.com
      supports: “In February 2026, Cheniere submitted an application to FERC to
        build the facility.”

- [ ] **Corpus Christi LNG Terminal** — HTTP 401, archive: unknown (throttled)
      https://www.reuters.com/legal/litigation/us-lng-export-plant-gas-flows-set-hit-16-week-low-despite-expected-return-golden-2026-05-19/?utm_source=chatgpt.com
      supports: “As of May 2026, six of seven trains in the initial phase of
        the expansion project had begun producing LNG.”

- [ ] **Elba Island LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/us-lng-plants-imported-cargoes-during-winter-storm-natural-gas-prices-hit-2026-01-28/
      supports: “Elba Island's LNG import terminal is infrequently used, but it
        is still active, importing LNG as recently as in January 2026 according
        to Reuters.”

- [ ] **Freeport LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/freeport-lng-seeks-approval-demolish-obsolete-import-facilities-texas-2026-04-07/?ref=lngglobal.com
      supports: “In April 2026, Freeport LNG sought approval from FERC to
        demolish its import facility.”

- [ ] **Freeport LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/texas-regulators-fine-freeport-lng-environmental-breaches-2024-04-17/?utm_medium=email&_hsenc=p2ANqtz-86gASwPYno17ELbdWG5mPJT0Vlk8Alf__N5gcoYUFXKi0rmZcIzSWKvsPh62cae426dtzyGjki66s_2lx-A4qCU2bfEmFHO3TwAp0OwQBUJ_3haUk&_hsmi=303478437&utm_content=303478437&utm_source=hs_email
      supports: “2019 and 2021. Emissions exceeding allowable levels included
        carbon monoxide, hydrogen sulfide, nitrogen oxides, sulfur dioxide and
        volatile organic compounds.”

- [ ] **Freeport LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/environment/freeport-lng-nears-end-expansion-that-will-increase-output-2024-08-02/
      supports: “…the "We have safely completed the vast majority of the work
        related to our debottlenecking project and are working to implement the
        benefits of those efforts."”

- [ ] **Kenai LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/marathon-seeks-more-time-build-lng-import-project-alaska-2022-07-11/?utm_medium=email&_hsmi=219790575&_hsenc=p2ANqtz--JgsoMEWWFQa6YXjNmW5EDvZg6CyMUemFbbn1qBY3Z0kwR7lLGG4x5l5USGWxqOcX4Gvn5rrC1f1PkM3teQDndrHVjXjpAs9H6Zmv4K_hDvJqAtCk&utm_content=219790575&utm_source=hs_email
      supports: “Foreland Pipeline Co unit submitted a request to the Federal
        Energy Regulatory Commission (FERC) to extend the end of its
        construction permit from 2022 to 2025.”

- [ ] **Lake Charles LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/article/eqt-lng-lake-charles/eqt-in-deal-with-energy-transfer-louisiana-lake-charles-lng-export-plant-idUSL1N39C136?utm_medium=email&_hsmi=268188599&_hsenc=p2ANqtz-8FHAnaUCqwLwdhpZDiMYqmeQIAv2C_jHzLadPKn9r9bGNkk5tTe0FiBSnGqVa5blcDf-8fsQnJeGwYIFx63RlfYRNUOsHG2SNLUSkmsB-37SRKDJU&utm_content=268188599&utm_source=hs_email
      supports: “…keting (with Gunvor Sinapore Energy as the ultimate buyer)(1
        mtpa, 15 years), and an unnamed US-based company as part of a tolling
        agreement (1 mtpa, 15 years).”

- [ ] **Lake Charles LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/doe-refuses-energy-transfers-rehearing-request-lng-project-2023-06-22/?utm_medium=email&_hsmi=263739822&_hsenc=p2ANqtz-_Y7GYPR8OVmAvoX0spj86FkmIUElwHmTRRtrLvXlNqst3zkTUYLP8h81GezFEiRegnGK-hd76j5uAZqG7epl9yO_6--2EABcs7TnrtwdV9-NEWjZM&utm_content=263739822&utm_source=hs_email
      supports: “…by the sponsor for a second extension of the Lake Charles
        project. According to the company's own filing to DOE, this decision
        could kill the project entirely.”

- [ ] **New Fortress Grand Isle FLNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/article/new-fortress-lng-offshore-terminal-idUSKCN2LS14P
      supports: “New Fortress Energy said that it intended to finance the
        facility itself.”

- [ ] **Plaquemines LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/article/venture-global-lng-excelerate-energ/update-1-venture-global-strikes-20-year-lng-supply-deal-with-excelerate-energy-idUSL4N3583FQ?utm_medium=email&_hsmi=248690210&_hsenc=p2ANqtz-8ftxq7AGVJizuRpktrfhyFK-m6f7s_DpkMUIX8C_2ylimz2_Gh42dtY9kbg-BMP2ERw28WAcMxxdBQ8PzKEs0qmo7udaLdf9WrBin3E10k9mb3B2c&utm_content=248690210&utm_source=hs_email
      supports: “The same month, Venture Global sealed an SPA with Excelerate
        Energy for 0.7 mpta LNG over 20 years.”

- [ ] **Plaquemines LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/venture-global-proposes-larger-expansion-plaquemines-lng-facility-filing-shows-2025-07-15/
      supports: “…acity of the proposed expansion to 24.5 mtpa. This figure
        appears to refer to the peak capacity of the expansion, rather than the
        nominal or nameplate capacity.”

- [ ] **Port Arthur LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/markets/deals/conocophillips-acquire-30-stake-sempras-port-arthur-lng-project-2022-07-14/?utm_medium=email&_hsmi=219790575&_hsenc=p2ANqtz-_1JtkYyvSXhI2oAzCZHVeUKH8x0KBP37vjSwi56CABwKXzYrXHwpznClnjJmQATeuphS69hmTwnwzXrwDY8clGUXLTMd_zEkIhyapfOF8TiKjNHxI&utm_content=219790575&utm_source=hs_email
      supports: “…under which it would acquire 5 mtpa of the fuel produced by
        Phase 1, supplying gas for its share of the output, and take a 30%
        stake in Phase 1 of the project.”

- [ ] **Qilak LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/qilak-lng-alaskas-smaller-gas-project-seeks-role-trumps-asia-push-ceo-says-2025-03-19
      supports: “…ing to a March 2025 Reuters story on the project, the cost is
        now estimated to be between US$4 billion and US$5 billion, and its
        planned start year is now 2033.”

- [ ] **Rio Grande LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/totalenergies-hold-10-interest-rio-grande-lng-train-4-project-2025-09-10/
      supports: “In September 2025, when NextDecade took a positive final
        investment decision on Train 4, TotalEnergies announced it would take a
        10% stake in the train.”

- [ ] **Sabine Pass LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/cheniere-signs-lng-supply-agreement-with-equinor-sabine-pass-expansion-2023-06-21/?utm_medium=email&_hsmi=263739822&_hsenc=p2ANqtz-9k0h4TqkDy01VpjEoWePj7-dAqDKB3hyrPPfBXbXrc0M7v4DfKQnvFOyjyd4RQ3FwC49zJNPt3UtxoodHrpHXvcW0PmLCrgahpgyHqVVFVG6z3LYc&utm_content=263739822&utm_source=hs_email#:~:text=HOUSTON,%20June%2021%20(Reuters),),%20it%20said%20on%20Wednesday
      supports: “=Contracts=== In May 2023, Cheniere entered a sales and
        purchase agreement (SPA) with KOSPO for 0.4 mtpa of LNG delivered on an
        ex-ship basis from 2027 to 2046.”

- [ ] **Sabine Pass LNG Terminal** — HTTP 401, archive: none
      https://www.reuters.com/business/energy/cheniere-signs-lng-supply-deal-with-chinas-enn-2023-06-26/?utm_medium=email&_hsmi=264661723&_hsenc=p2ANqtz-_-CEBGJUgx19IXXASz2HO7QQ-j8-Wv4qmC-jkrIlY6BGxkCJ9AvjsP6O5fBA0emsWPgD7B9XnWjDlzWYMxPRLq8A8KKlM0s4Qk7w5R01t3c1CGFqE&utm_content=264661723&utm_source=hs_email
      supports: “The same month, China's ENN agreed to purchase 1.8 mtpa over
        20 years beginning in 2026, with half of the volume contingent on the
        Sabine Pass expansion.”

- [ ] **Texas LNG Terminal** — HTTP 401, archive: unknown (throttled)
      https://www.reuters.com/business/energy/socgen-confirms-it-pulled-out-texas-lng-project-2023-03-28/?utm_medium=email&_hsmi=252608681&_hsenc=p2ANqtz-9iANiZOAyBitV_qrHzMWsY20636QWDHuJoj3HAumlQv1qcJZHwA8Bu6aTGIRInd3LvxVHx7hWq6mtc5Tpys_LGtBr8qVhOGfUcvsepk85rnA1gQU8&utm_content=252608681&utm_source=hs_email
      supports: “…mmitments, which include ending all LNG financing where the
        project is not aligned with the bank's human rights and environmental,
        social and governance goals."”

- [ ] **Vista Del Sol LNG Terminal** — HTTP 401, archive: none
      http://www.reuters.com/article/exxon-lng-4gas-idUSL127770420070112
      supports: “The project was acquired by 4Gas in January of 2007.”

**businesswire.com — 7 refs, all 403.** Press releases — these effectively
never disappear, and Business Wire keeps them indefinitely at a stable URL.

- [ ] **Alaska LNG Terminal** — HTTP 403, archive: unknown (throttled)
      https://www.businesswire.com/news/home/20260518664708/en/Glenfarne-ConocoPhillips-Sign-North-Slope-Gas-Sales-Precedent-Agreement-for-Alaska-LNG??ref=lngglobal.com
      supports: “Alaska LNG now has agreements with all three major North Slope
        producers: ConocoPhillips, ExxonMobil..., Hilcorp Alaska, as well as
        Great Bear Pantheon LLC...."”

- [ ] **Lake Charles LNG Terminal** — HTTP 403, archive: none
      https://www.businesswire.com/news/home/20250409435078/en/Energy-Transfer-Signs-Agreement-With-MidOcean-Energy-to-Jointly-Develop-Its-Lake-Charles-LNG-Export-Facility?utm_source=substack&utm_medium=email
      supports: “Agreement (HOA) with MidOcean Energy, under which the latter
        would provide 30% of the costs of construction and be entitle to 30%
        offtake of the facility's LNG.”

- [ ] **Texas LNG Terminal** — HTTP 403, archive: none
      https://www.businesswire.com/news/home/20240314777298/en/Glenfarne-Energy-Transition%E2%80%99s-Texas-LNG-Moves-to-Execution-Phase-of-Project-Financing?utm_source=substack&utm_medium=email
      supports: “…elease stating that it "has received sufficient expressions
        of interest from leading project finance banks to move to the execution
        phase of project financing."”

- [ ] **Texas LNG Terminal** — HTTP 403, archive: none
      https://www.businesswire.com/news/home/20240317583952/en/Glenfarne-Energy-Transition%E2%80%99s-Texas-LNG-Announces-LNG-Offtake-Agreement-with-Gunvor-Group?utm_source=substack&utm_medium=email
      supports: “…vor signed a sales and purchase agreement (SPA) with
        Glenfarne for the purchase of 0.5 mtpa LNG from the project on a free-
        on-board basis over a 20-year period.”

- [ ] **Woodside Louisiana LNG Terminal** — HTTP 403, archive: none
      https://www.businesswire.com/news/home/20240529924670/en/Aethon-Energy-to-Acquire-Tellurian-Integrated-Upstream-Assets?utm_source=substack&utm_medium=email
      supports: “As part of the agreement, Aethon committed to purchase 2 mpta
        from the project under a non-binding heads of agreement (HOA).”

- [ ] **Woodside Louisiana LNG Terminal** — HTTP 403, archive: none
      https://www.businesswire.com/news/home/20240628393311/en/Tellurian-Closes-260-Million-Asset-Sale-and-Retires-Senior-Secured-Debt?utm_source=substack&utm_medium=email
      supports: “…a US$260 million sale of its integrated upstream assets to
        Aethon, using proceeds from the sale to retire $230 million of non-
        convertible Senior Secured Notes.”

- [ ] **Woodside Louisiana LNG Terminal** — HTTP 403, archive: none
      https://www.businesswire.com/news/home/20250915769336/en/Full-Steam-Ahead-for-Woodside-Louisiana-LNG?utm_source=substack&utm_medium=email
      supports: “…will have three trains and a total capacity of 16.5 mtpa. The
        second phase will consist of an additional two trains, and bring the
        total capacity to 27.6 mtpa.”

**bizjournals.com — 2 refs, all 403.** American City Business Journals paywall.

- [ ] **Corpus Christi LNG Terminal** — HTTP 403, archive: none
      https://www.bizjournals.com/houston/news/2024/05/06/cheniere-corpus-christi-lng-expansion-q1-earnings.html
      supports: “In May 2024, it was reported that the Stage 3 project was
        nearly a year ahead of schedule.”

- [ ] **Eagle LNG Terminal** — HTTP 403, archive: none
      https://www.bizjournals.com/jacksonville/news/2019/09/24/eagle-lng-gets-the-green-light-on-lng-export.html
      supports: “…latory Commission (FERC) approved of the project's
        environmental impacts. In September 2019, FERC granted authorization
        for construction of the export facility.”

**bit.ly — 1 ref, all 403.**

- [ ] **American LNG Hialeah Terminal** — HTTP 403, archive: unknown (throttled)
      http://bit.ly/2mEJqGg
      supports: “…can LNG's Hialeah terminal is an approved LNG export terminal
        in the US, and has submitted contracts for long-term export of LNG to
        the US Department of Energy.”

**bloomberg.com — 1 ref, all 403.**

- [ ] **Delfin FLNG Terminal** — HTTP 403, archive: none
      https://www.bloomberg.com/news/articles/2025-09-25/delfin-lng-eyes-investment-decision-for-us-project-by-november
      supports: “As of September 2025, the facility was planned to have a
        deepwater port with as many as 3 floating LNG export vessels, and a
        total capacity of 13.2 mtpa.”

**einnews.com — 1 ref, all 403.**

- [ ] **Argent LNG Terminal** — HTTP 403, archive: none
      https://www.einnews.com/pr_news/722271387/argent-lng-selects-worley-as-its-epc-development-partner-for-20-mtpa-lng-facility-in-port-fourchon
      supports: “Also in June 2024, Argent LNG announced that it had selected
        Worley as its engineering, procurement, and construction (EPC)
        contractor for the project.”

**fox4kc.com — 1 ref, all 403.**

- [ ] **Monkey Island LNG Terminal** — HTTP 403, archive: none
      https://fox4kc.com/business/press-releases/accesswire/1071231/monkey-island-lng-signs-major-mou-for-lng-offtake-with-an-international-oil-company-ioc-advancing-billions-u-s-gulf-coast-lng-project/?utm_source=substack&utm_medium=email
      supports: “…estment-grade International Oil Company" which said it would
        purchase, over 20 years, up to 5.2 mtpa of LNG, representing the entire
        first train of the project.”

**maritime.dot.gov — 1 ref, all 403.**

- [ ] **West Delta LNG Deepwater Port Terminal** — HTTP 403, archive: none
      https://www.maritime.dot.gov/ports/deepwater-ports-and-licensing/pending-applications?utm_source=chatgpt.com
      supports: “As of September 2025, West Delta LNG's application was still
        listed as pending on MARAD's site.”
      MARAD's pending-applications index — a live index page, not an article,
        so it may no longer *list* West Delta even though it loads.

**nj.com — 1 ref, all 403.**

- [ ] **Safe Harbor Energy LNG Terminal** — HTTP 403, archive: none
      https://www.nj.com/news/2010/07/nj_firm_withdraws_application.html
      supports: “…though they reserved the right to renew its application for a
        manmade island 19 miles off Sandy Hook, environmentalists say the
        proposal is "dead in the water".”

**offshore-technology.com — 1 ref, all 403.**

- [ ] **Corpus Christi LNG Terminal** — HTTP 403, archive: none
      https://www.offshore-technology.com/news/cheniere-fid-corpus-christi-lng-facility-expansion-texas/?cf-view
      supports: “In June 2025, Cheniere announced a positive final investment
        decision (FID) for its Stage 3 Expansion project.”

**query.nytimes.com — 1 ref, all 403.**

- [ ] **Broadwater FSRU** — HTTP 403, archive: none
      http://query.nytimes.com/gst/fullpage.html?res=9402E3D71E31F932A15750C0A96E9C8B63
      supports: “LNG. Broadwater Energy LLC would have operated the LNG
        facility. The proposed project was approved by the Federal Energy
        Regulatory Commission in March of 2008.”
      A pre-2010 NYT `fullpage.html` permalink. These mostly still resolve for
        a human; if it does not, the article is findable in the NYT archive by
        date.

**spglobal.com — 1 ref, all 403.**

- [ ] **Rio Grande LNG Terminal** — HTTP 403, archive: none
      https://www.spglobal.com/commodity-insights/en/market-insights/latest-news/lng/032422-nextdecade-deal-with-chinese-utility-lifts-rio-grande-lng-commercial-momentum?utm_medium=email&_hsmi=208015075&_hsenc=p2anqtz--67gs3rbksj1bdfks_ld6ns7jwnvpmm-sttcpemyqc58mh3zbkbg5nhqjfdzpvrz0og7ahupxcnqj0ahulr5tgyjdndhbtxn6zzq09lcme1kovgl0&utm_content=208015075&utm_source=hs_email
      supports: “…y Guongdong Energy for the purchase of up to 1.5 mtpa for 20
        years. The heads of agreement calls for the companies to arrange a firm
        sales agreement in Q2 2022.”
      Note the URL's percent-encoded query is lowercased; the path itself is
        intact.

**wdtn.com — 1 ref, all 403.**

- [ ] **Argent LNG Terminal** — HTTP 403, archive: none
      https://www.wdtn.com/business/press-releases/ein-presswire/722276490/argent-lng-announces-long-term-lease-with-greater-lafourche-port-commission-for-development-of-up-to-20-mtpa-facility/
      supports: “…with the Greater Lafourche Port Commission, taking over a
        site that had previously been leased by Energy World for the
        development of [[Fourchon LNG Terminal]].”

**world.einnews.com — 1 ref, all 403.**

- [ ] **Argent LNG Terminal** — HTTP 403, archive: none
      https://world.einnews.com/pr_news/909677503/argent-lng-hits-key-regulatory-milestone-advancing-25-mtpa-gulf-coast-export-project-toward-authorization?ref=lngglobal.com
      supports: “In May 2026, Argent LNG submitted six Resource Reports to
        FERC.”

#### The 10 refs that return a live 200

These resolve. They were flagged only because the fetched body carries no
readable article text — a subscriber wall, a client-rendered shell, or a
shortlink whose target a script would not follow. Confirm the page is the cited
document and tick it off.

- [ ] **Alaska LNG Terminal** — HTTP 200, archive: none
      https://www.wsj.com/articles/u-s-allies-in-asia-snub-natural-gas-from-alaska-project-e54f754a?utm_medium=email&_hsmi=268188599&_hsenc=p2ANqtz--EpducZySxenh82xrulMfqkNk13kT-yRf4FAvB4meBXX8BhkMXuJ9OK48zu98_7HMtGTAEvh27LDLXGkP3aE4eJonnCG6gc-zjfRqcUHAeeG5tHbs&utm_content=268188599&utm_source=hs_email
      supports: “…at Asian countries will have other sources of stable natural-
        gas supplies by 2030, although the gas market is volatile and competing
        projects also carry risks."”
      WSJ paywall.

- [ ] **Annova LNG Terminal** — HTTP 200, archive: none
      https://seekingalpha.com/news/3452513-ferc-moves-closer-approving-exelons-annova-lng-project
      supports: “…orable, claiming that although the project stands to cause
        harm to the local environment, most of it would be reduced through
        Annova's proposed mitigation plan.”
      Seeking Alpha bot wall.

- [ ] **Delfin FLNG Terminal** — HTTP 200, archive: none
      http://bit.ly/2nOu7Lj
      supports: “Delfin FLNG Terminal is a proposed LNG terminal in Louisiana,
        United States.”
      Shortlink resolves fine.

- [ ] **Elba Island LNG Terminal** — HTTP 200, archive: exists
      http://elibrary.ferc.gov/idmws/common/opennat.asp?fileID=9673760
      supports: “…a fourth cryogenic storage tank, and associated facilities.
        The expansion enabled an increase of working gas capacity and an
        increase of the firm sendout rate.”
      FERC eLibrary shell — the live URL returns 200, so it works for a reader;
        only a script cannot read it.
      capture:
      https://web.archive.org/web/20250208141953/http://elibrary.ferc.gov/idmws/common/opennat.asp?fileID=9673760

- [ ] **Elba Island LNG Terminal** — HTTP 200, archive: none
      https://ijglobal.com/data/transaction/48273/eig-facility-upsizing-2019
      IJGlobal subscriber wall. No context recorded by the scanner for this
        one.

- [ ] **Everett Marine Terminal** — HTTP 200, archive: none
      https://subscriber.politicopro.com/article/eenews/2022/12/13/can-new-england-keep-on-the-lights-without-lng-00073587?utm_medium=email&_hsmi=238271930&_hsenc=p2ANqtz--EJbnF899ka81zddC542aVd8LKKhV1KQFXu-Am7WpsNXr1VYHpC9VFVWqWyE-G3rucAN-1z1nOhjWgAow_H7Ea9hWqOehaYMhEtpbkoO0jzGv8-pM&utm_content=238271930&utm_source=hs_email
      supports: “December 2022, Politico Pro reported that the potential
        closure of the facility in 2024, due to economic factors, could
        threaten New England's energy security.”
      Politico Pro subscriber wall.

- [ ] **Golden Pass LNG Terminal** — HTTP 200, archive: none
      https://seekingalpha.com/news/3259917-exxon-conoco-jv-golden-pass-lng-approved-natural-gas-export
      supports: “In April 2017 the terminal was cleared by the Department of
        Energy to begin exporting up to 2.2 Bcf/day of natural gas.”
      Seeking Alpha bot wall.

- [ ] **Lake Charles LNG Terminal** — HTTP 200, archive: none
      https://seekingalpha.com/news/3523505-energy-transfer-shell-release-full-commercial-tender-for-lake-charles-lng
      supports: “…curement, and construction contractors for final bids for the
        proposed Lake Charles LNG export facility. Commercial bids are expected
        to be received in Q2 2020.”
      Seeking Alpha bot wall.

- [ ] **Port Arthur LNG Terminal** — HTTP 200, archive: none
      http://bit.ly/2niBu0B
      supports: “Port Arthur LNG Terminal is a proposed LNG terminal in Texas,
        United States.”
      Shortlink resolves fine, but its target no longer says what the sentence
        claims — this is the "Project Schedule" case in 5e.

- [ ] **Port Arthur LNG Terminal** — HTTP 200, archive: none
      https://seekingalpha.com/news/3473279-sempra-seeks-pipeline-expansion-port-arthur-lng
      supports: “In June of 2019, Sempra Energy asked FERC to approve a
        significant expansion of the associated pipeline that would boost the
        export capacity.”
      Seeking Alpha bot wall.

#### The 5 soft 404s

Each returns **200 with the expected keywords present** and has a Wayback
snapshot, so the likely answer in every case is "alive, behind a paywall or JS
shell." They are listed because a soft 404 is precisely the thing a script
cannot tell from a real page — not because they look dead. (A sixth soft 404,
`bit.ly/2nQXtIO` on Bay Crossing LNG Terminal, was a plain relocation and is
already fixed — rev 1206896.)

- [ ] **Argent LNG Terminal** · **Fourchon LNG Terminal** (one ref, 2 pages) — HTTP 200, archive: exists
      https://www.energyintel.com/0000018c-69e1-d61c-a7cc-79f73f5e0000
      supports: “In December 2023, Fourchon LNG was removed by FERC from the
        pre-filing process due to inactivity.”
      Opaque ID, so the headline cannot be inferred from the URL. Subscription
        site. Cited on both pages for the same claim.
      capture:
      http://web.archive.org/web/20250721180452/https://www.energyintel.com/0000018c-69e1-d61c-a7cc-79f73f5e0000

- [ ] **Calais LNG Terminal** — HTTP 200, archive: exists
      http://www.pressherald.com/2010/12/14/would-be-lng-developer-pulls-plug-on-calais-project/
      supports: “Before dismissal by FERC, Calais LNG had put the project on
        hold, ostensibly due to unstable financial markets.”
      Portland Press Herald, "Would-be LNG developer pulls plug on Calais
        project," 14 Dec 2010. Resolves to itself at 200 with `calais` present
        — almost certainly just the paper's paywall shell.
      capture:
      http://web.archive.org/web/20241014233408/https://www.pressherald.com/2010/12/14/would-be-lng-developer-pulls-plug-on-calais-project/

- [ ] **Cove Point LNG Terminal** — HTTP 200, archive: exists
      https://www.fool.com/investing/2019/12/11/the-next-big-energy-project-dominion-investors-nee.aspx
      supports: “…uced by the US Federal Energy Regulatory Commission, as of
        February 2020 Dominion appeared to have weathered the storm by selling
        off the portion of Cove Point.”
      Motley Fool, 11 Dec 2019.
      capture:
      http://web.archive.org/web/20250916081349/https://www.fool.com/investing/2019/12/11/the-next-big-energy-project-dominion-investors-nee.aspx

- [ ] **Delfin FLNG Terminal** — HTTP 200, archive: exists
      https://www.energyintel.com/0000018d-f137-d813-a5df-f7770c300000?utm_source=substack&utm_medium=email
      supports: “As of February 2024, Deflin FLNG was targeting an FID over the
        coming months.”
      Same publisher, same opaque-ID situation. Note the "Deflin" typo in the
        wiki sentence while you are there.
      capture:
      http://web.archive.org/web/20251121194117/https://www.energyintel.com/0000018d-f137-d813-a5df-f7770c300000?utm_source=substack&utm_medium=email

- [ ] **Jordan Cove LNG Terminal** — HTTP 200, archive: exists
      https://kcby.com/news/local/ferc-says-it-will-deny-all-requests-for-rehearing-of-jordan-cove-lng
      supports: “…xtensive requests on multiple grounds by environmental
        groups, landowners, tribes and state agencies for a rehearing of its
        March 2020 approval for Jordan Cove.”
      KCBY, "FERC says it will deny all requests for rehearing of Jordan Cove."
      capture:
      http://web.archive.org/web/20250722123338/https://kcby.com/news/local/ferc-says-it-will-deny-all-requests-for-rehearing-of-jordan-cove-lng

### 5b. Citations that never had a URL — repaired, but only halfway

Seven refs across 5 pages had their *headline* wrapped in `[[...]]`, MediaWiki's
internal-link syntax. All seven targets were checked against the API and all
seven are missing, so each rendered as a **red link inviting a reader to create a
GEM.wiki page named after a news headline** — worse than an unlinked citation,
because it reads as an internal cross-reference to something that ought to exist
here. The four bracket characters were deleted and nothing else (revs
1206903–1206907), which leaves a complete, valid, unlinked citation: author,
headline, publisher, date, exactly as the citing editor wrote them.

**What is still open is the upgrade to a real link.** Three of the seven have
candidate URLs; four could not be found at all by two independent agents.

**Three with candidate URLs.** Each was arrived at independently by two agents —
one by URL-pattern inference, one by decoding the Google News redirect — which is
good evidence the URL is right but is *not* a content confirmation, because all
three hosts refuse bots. If it loads and matches, the citation can be upgraded
from unlinked to a real external link:

- [ ] **Corpus Christi LNG Terminal** — Harry Weber, "Cheniere reached LNG supply
      deal with New Fortress affiliate over summer: DOE," S&P Global, 14 Dec 2021
      https://www.spglobal.com/energy/en/news-research/latest-news/lng/121421-cheniere-reached-lng-supply-deal-with-new-fortress-affiliate-over-summer-doe

- [ ] **Plaquemines LNG Terminal** — Marcy De Luna, "Venture Global says Shell to
      buy LNG from Louisiana Plaquemines plant," Reuters, 7 Mar 2022
      https://www.reuters.com/business/energy/venture-global-says-shell-buy-lng-louisiana-plaquemines-plant-2022-03-07/

- [ ] **Plaquemines LNG Terminal** — Sergio Chapa, "Venture Global Signs Another
      Pair of LNG Supply Deals With China," BNN Bloomberg, 20 Dec 2021. The cited
      BNN copy is dead (it 301s to the BNN homepage); this is the Bloomberg
      original — hard-walled, and one agent proposed it while the other could not
      confirm it.
      https://www.bloomberg.com/news/articles/2021-12-21/venture-global-signs-another-pair-of-lng-supply-deals-with-china

**Four with no candidate URL.** There is nothing to click here — these need a
search, and the recorded citation string is the whole of what is known:

- [ ] **CP2 LNG Terminal** and **Plaquemines LNG Terminal** — "LNG Global. Venture
      Global LNG Sales and Purchase Agreements with New Fortress Energy. March 16,
      2022." (the same document, cited on both pages). Today's `lngglobal.com` is a
      different site whose sitemap starts in **December 2025**, so the 2022 article
      has no live home and no archive. Supports the New Fortress 1 mtpa / 20-year
      contract on CP2.
- [ ] **Magnolia LNG Terminal** — "S&P Global Newdesk-Vietnam and Eric Yep.
      Vietnam's Delta Offshore Energy backs away from renewing MOU with Magnolia
      LNG. August 11, 2020." No S&P result surfaced for this headline at all,
      unlike the Corpus Christi and Rio Grande ones.
- [ ] **Rio Grande LNG Terminal** — "Weber, Harry. Rio Grande LNG project final
      investment decision delayed to second half of 2022. S&P Global. January 3,
      2022."

### 5c. Claim only partly supported by its new source

- [ ] **Ingleside Energy LNG Terminal** (rev 1206891). Its only Background ref was
      an `abarrelfull.wikidot.com` mirror — a banned source, not a citable one — so
      the claim was re-sourced to Occidental's own 8-K Exhibit 99.1 of 7 Sep 2005:
      https://www.sec.gov/Archives/edgar/data/797468/000079746805000131/exhibit991-20050907.htm
      That document states "Ingleside, Texas LNG Terminal … FERC Approval Granted
      in Late July. $450 Million LNG Receiving Terminal and Related 26-Mile
      Pipeline," which covers the **import terminal** half of the sentence. It does
      **not** cover the second half — "later cancelled and resubmitted as an export
      facility proposal" — for which no live, citable source was found. The citation
      is strictly better than the mirror it replaced, but the export-resubmission
      clause is now visibly unsourced and needs either a source or a trim.

- [ ] **Oregon LNG Terminal** (rev 1206946). The dead Columbia Riverkeeper PDF was
      pointed at its Wayback capture, and the capture is unambiguously the cited
      document — a 406 KB PDF, read with `pdftotext`, addressed to the **U.S. Army
      Corps of Engineers** and subject-lined "Oregon Department of Fish and Wildlife
      comments on Oregon LNG's application for permits under **Clean Water Act
      Section 404**, Rivers and Harbors Act Section 10, and the Marine Protection,
      Research and Sanctuaries Act of 1972 Section 103":
      https://web.archive.org/web/20160304035937/http://columbiariverkeeper.org/wp-content/uploads/2015/02/2015.1.16-ODFW-Corps-OLNG-JPA-final.pdf
      So the link repair is right and was applied. But the sentence it supports says
      Oregon LNG "filed a formal application with the **Federal Energy Regulatory
      Commission (FERC)** in October 2008" — and the document never mentions FERC at
      all; it is about an Army Corps permit application. This is a **pre-existing
      sourcing gap, not link rot**: the citation was already mismatched before it
      died. Either the FERC sentence needs its own source (Oregon LNG's FERC docket
      is CP09-6) or the claim needs rewording to match the Army Corps filing.

### 5d. Currency notes — the source moved on, the sentence didn't

Not link defects; nothing is broken and no edit was made. Flagged because a
researcher checking the citation will see a different number than the wiki gives.

- [ ] **Freeport LNG Terminal** — the wiki says **15 mtpa**; Freeport's live
      overview page now says **17 mtpa**.
      https://freeportlng.com/about/about-overview

- [ ] **Plaquemines LNG Terminal** — the wiki says "The **632**-acre site is
      located on the Mississippi River"; Venture Global's live project page now says
      "The approximately **630** acre site is located on the Mississippi River" (the
      river claim is unaffected). Separately, the wiki still calls Plaquemines "a
      **proposed** LNG terminal" while Venture Global describes it as constructing
      and commissioning — a tracker-status question, not a citation one.
      https://venturegloballng.com/project-plaquemines/

### 5e. Decisions needed, and the last unsettled lookups

**The archive wave itself is closed** (revs 1206935–1206952, 2026-07-29); its
outcome is the table at the top of this section. What is left is one lookup that
never got a straight answer out of archive.org, one source-policy ruling, and one
scope call.

- [ ] **5 URLs are still `THROTTLED`** after four passes (39 → 17 → 13 → 5).
      Throttled is *not* "never archived" and was never recorded as such — the
      2026-07-28 Italy/Spain pass returned "no archive" on all 106 URLs purely from
      throttling, and every one was in fact archived. **4 of the 5 are bot walls
      needing no repair regardless** — they are the four marked "archive:
      unknown (throttled)" in 5a (one `bit.ly` on American LNG Hialeah, one
      `businesswire.com` on Alaska LNG, and two `reuters.com` on Texas LNG and
      Corpus Christi). Only one genuinely depends on the answer, and it also fails
      to connect live (it is listed in 5h as well):
      https://www.ccbiznews.com/news/carlyle-group-out-of-port-corpus-christi-terminal

- [ ] **Two `killajoules.wikidot.com` refs.** Same wikidot-mirror family as the
      banned `abarrelfull.wikidot.com`, but never explicitly named in the ban, so
      they were left alone rather than have the ban extended without asking.
      **Decision needed: treat killajoules as banned too (drop or re-source), or
      leave as-is?** Both return 200, so this is a source-policy question, not a
      link-rot one. (The wikidot slugs really do end mid-word — wikidot truncates
      its own page names.)
      Calhoun LNG Terminal, supporting the KOGAS / LG International / EMS Group MOU:
      http://killajoules.wikidot.com/archive:kogas-lg-international-and-ems-group-join-forces-wit
      Compass Port LNG Terminal, supporting ConocoPhillips's 2006 withdrawal of its
      Deepwater Port Act licence application:
      http://killajoules.wikidot.com/archive:conocophillips-withdraws-application-for-compass-por

- [ ] **The wave-5 "unbracket" class was applied autonomously — flag if unwanted.**
      Stripping `[[...]]` from 7 citation headlines (5b) repairs a rendering defect
      rather than a dead link, which is arguably outside "fix bad links." It was
      judged in-scope because a red link inviting page creation is a worse defect
      than the one being fixed, and because deleting four bracket characters cannot
      change what the citation says. Recorded here because it is a **scope
      extension**, and reverting it is four characters per ref if that call was
      wrong.

**Two items from the previous compilation are now settled, both negatively:**

- **Delfin FLNG Terminal — `delfinlng.com` needed the August 2017 capture.** The
  only capture archive.org holds is **October 2019**, which is the wrong era: the
  sentence describes "an early version … four floating LNG trains … 13 million
  metric tonnes," while both the 2019 capture and the live relocation target
  describe three vessels at 13.2 mtpa. Neither supports the four-train sentence.
  **Needs a source or a rewording, not a link fix.** The dead ref as cited:
  http://www.delfinlng.com/
  The only capture:
  https://web.archive.org/web/20191023163254/http://www.delfinlng.com/
  The live relocation target:
  https://delfinmidstream.com/delfin-lng/

- **Port Arthur LNG Terminal — the "Project Schedule" ref.** `bit.ly/2niBu0B` was
  cited twice with different link text; the identity-sentence copy was relocated
  to Sempra's live project page (rev 1206902). The "Project Schedule" copy,
  supporting "expects to receive FERC approval and DOE non-FTA authorization in
  mid 2018, with operation in 2023," was left on the shortlink pending an archive
  — and archive.org has now confirmed **no capture of that shortlink exists**. The
  shortlink itself still resolves, to https://portarthurlng.com/ — but that page
  has no schedule section and reports FID in March 2023 with Train 1 operating in
  2027, so the claim is both unsourceable and superseded. **Needs a rewrite to
  current facts.**

### 5f. Out of scope, recorded so they aren't re-flagged

- **4 offline/print citations** among the 11 MALFORMED refs — no URL exists to
  repair: BloombergNEF on Main Pass Energy Hub, E&E's Northey on Cameron, and The
  Oregonian's Sickinger ×2 on Oregon LNG.
- **3 pages have no `==Background==` section at all**: New Fortress Wyalusing LNG
  Terminal, OceanWay LNG Terminal, Phillips 66 Beamont Oil Terminal. (The last
  also has "Beamont" for "Beaumont" in its title.)
- **2 pages have a Background section with zero refs** — unsourced prose, a
  different problem from a broken citation: IMTT St. Rose Oil Terminal, Jupiter
  Offshore Loading Terminal (JOLT).
- **91 `REUSE` refs** (`<ref name=x />` markers with no URL of their own) and all
  `autoref_*` refs (bot-generated from the tracker DB into the ownership and
  location tables, overwritten on each sync) are excluded by name, as everywhere
  else in this project.
- **2 dead shortlinks whose only citation is an `autoref_*`.** Both reached the
  archive queue because that queue was seeded from a page-wide URL scan rather
  than from editable refs, and both had a usable snapshot. Not applied: the
  tracker bot rewrites these tables on every sync, so any edit would be reverted.
  The fix belongs in the bot's source data, not here.
  Bienville FSRU (resolves to a Federal Register withdrawal notice):
  http://bit.ly/2mJLxsQ
  Gulf Gateway Deepwater Port LNG Terminal (resolves to Wikipedia):
  http://bit.ly/2ncmf9v
- **1 URL-normalization false positive, never actually broken** — on Elba Island
  LNG Terminal. The scanner's URL extractor ends with `rstrip(".,);")`, which
  stripped the closing parenthesis; the truncated URL 404s, so the ref was flagged
  dead. The URL as actually cited on the page — parenthesis intact — returns
  **200**:
  https://en.wikipedia.org/wiki/Elba_Island_(Georgia)
  Recorded because it is the one defect in this batch that lived in the *tooling*
  rather than on the wiki, and a future pass with the same extractor will re-flag
  it. A repo-wide check found this is the only such case in the US set (one URL
  with unbalanced parentheses out of 465).

### 5g. Had a capture, but the capture is not the document (16)

**A Wayback 200 is not evidence.** Every candidate snapshot in the archive wave
was fetched and read against the sentence citing it before being used; these
16 failed that check and were **not** applied. Each is listed
with its live URL, the capture that was rejected, and why — so a later pass
cannot silently re-accept it. (`working-files/wave6_reject.json` is the
machine-readable copy.) Five distinct failure modes turned up, and the last two
are the reason the check exists at all:

- **capture of a 404 page** — Wayback faithfully archived the publisher's own
  error page.
- **paywall interstitial** — the capture is the "subscribe to continue" shell.
- **JS shell** — the publisher renders client-side, so the capture has no article
  text and never can.
- **a different article at the same URL** — the URL was recycled.
- **domain squat** — `energyportal.eu` is now a Greek sports-betting site, and
  Wayback archived the spam exactly as it found it.

Two of the 16 need **no repair at all** — the live URLs return
200 and FERC eLibrary is simply not archivable — and are recorded only so they
are not re-flagged. One more is a pre-existing weak citation rather than link
rot. Those three are marked; the rest are dead links whose only capture is
unusable, so they belong with 5h in practice.

- [ ] **Annova LNG Terminal** — HTTP 404, archive: exists
      http://bit.ly/2nj7CBz
      supports: “Annova LNG Terminal was a proposed LNG terminal in Texas,
        United States.”
      capture:
      https://web.archive.org/web/20250805023944/http://bit.ly/2nj7CBz
      rejected because: snapshot fetch status 404

- [ ] **Battery Rock LNG Terminal** — HTTP 404, archive: exists
      http://bit.ly/2nxJYhG
      supports: “Battery Rock LNG Terminal was a proposed LNG import terminal
        in Massachusetts, United States.”
      capture:
      https://web.archive.org/web/20250519011309/http://bit.ly/2nxJYhG
      rejected because: snapshot fetch status 404

- [ ] **Corpus Christi LNG Terminal** — HTTP 200, archive: exists
      https://oilandgaswatch.org/facility/828
      supports: “313 value limitation agreements to construct three additional
        expansions, which could include 6 to 24 trains each, and would be
        completed between 2037 and 2041.”
      capture:
      https://web.archive.org/web/20250711154929/https://oilandgaswatch.org/facility/828
      rejected because: 4 KB JS shell ("EIP Oil & Gas Watch"), no article text
        captured

- [ ] **Crown Landing LNG Terminal** — HTTP 200, archive: exists
      https://elibrary.ferc.gov/idmws/File_list.asp?document_id=13985730
      supports: “…al. The company's president cited increasing North American
        shale gas production and its impact on demand for imports as a reason
        for discontinuing the project.”
      capture:
      http://web.archive.org/web/20160306150217/http://elibrary.ferc.gov/idmws/File_list.asp?document_id=13985730
      rejected because: capture is a real FERC docket file list, which cannot
        support the sentence it is cited for (president citing shale gas); pre-
        existing weak citation, not link rot

- **Elba Island LNG Terminal** — HTTP 200, archive: exists
      http://elibrary.ferc.gov/idmws/common/opennat.asp?fileID=11457000
      supports: “…rson had ask FERC to deny the pipeline going through the
        Northern Segment. FERC denied Anderson’s motion for hearing, but said
        that it will review the petition.”
      capture:
      https://web.archive.org/web/20250512045503/http://elibrary.ferc.gov/idmws/common/opennat.asp?fileID=11457000
      rejected because: 17 KB shell (body is the word "eLibrary") AND the live
        url returns 200, so no repair is needed

- **Elba Island LNG Terminal** — HTTP 200, archive: exists
      http://elibrary.ferc.gov/idmws/common/opennat.asp?fileID=11589845
      supports: “…rson had ask FERC to deny the pipeline going through the
        Northern Segment. FERC denied Anderson’s motion for hearing, but said
        that it will review the petition.”
      capture:
      https://web.archive.org/web/20241228042248/http://elibrary.ferc.gov/idmws/common/opennat.asp?fileID=11589845
      rejected because: 17 KB shell (body is the word "eLibrary") AND the live
        url returns 200, so no repair is needed

- [ ] **Floridian LNG Terminal** — HTTP 404, archive: exists
      http://bit.ly/2nOhoIq
      supports: “Floridian LNG Terminal is a proposed LNG terminal in Florida,
        United States.”
      capture:
      https://web.archive.org/web/20250804232646/http://bit.ly/2nOhoIq
      rejected because: snapshot fetch status 403

- [ ] **Jordan Cove LNG Terminal** — no connection, archive: exists
      http://jordancovelng.com/wp-content/uploads/2017/03/JC-Fact-Sheet-Regulatory-Process-FINAL.pdf
      supports: “However, Jordan Cove has announced they plan to refile a new
        formal application with FERC in late 2017.”
      capture:
      https://web.archive.org/web/20190125035648/http://jordancovelng.com/wp-content/uploads/2017/03/JC-Fact-Sheet-Regulatory-Process-FINAL.pdf
      rejected because: snapshot fetch status 404

- [ ] **Magnolia LNG Terminal** — HTTP 404, archive: exists
      https://www.naturalgasintel.com/articles/121852-the-offtake-lng-in-briefcoronavirus
      supports: “…ad resulted in the calling in of administrators
        PriceWaterhouseCoopers to review the company's assets, as well as the
        resignation of four LNG Limited directors.”
      capture:
      https://web.archive.org/web/20250403065454/https://www.naturalgasintel.com/articles/121852-the-offtake-lng-in-briefcoronavirus
      rejected because: snapshot fetch status 404

- [ ] **Main Pass Energy Hub FLNG Terminal** — HTTP 404, archive: exists
      https://www.gasworld.com/global-lng-services-launches-new-solution/2016947.article
      supports: “…ficant progress on its wholly-owned Main Pass Energy Hub™
        (MPEH) LNG export project in the Gulf of Mexico that will eventually
        export as much as 48 MTPA of LNG.”
      capture:
      http://web.archive.org/web/20210622105327/https://www.gasworld.com/global-lng-services-launches-new-solution/2016947.article
      rejected because: capture is a paywall interstitial ("You must be a
        subsciber"); none of Main Pass/MPEH/48/MTPA present

- [ ] **Port Esperanza FSRU** — HTTP 403, archive: exists
      http://www.presstelegram.com/article/ZZ/20070307/NEWS/703079917
      supports: “In 2007, Port Esperanza LNG announced they would begin seeking
        approval for the project in the near future.”
      capture:
      https://web.archive.org/web/20250517035206/http://www.presstelegram.com/article/ZZ/20070307/NEWS/703079917
      rejected because: only 2/12 keywords found; needs reading

- [ ] **Sabine Pass LNG Terminal** — HTTP 200, archive: exists
      https://www.energyportal.eu/news/cheniere-energy-eyes-new-gas-pipeline-to-feed-lng-expansion-2/70190/
      supports: “A fossil gas pipeline is also proposed for the expansion, to
        connect the additional export capacity to US shale gas-producing
        regions.”
      capture:
      https://web.archive.org/web/20250724160434/https://www.energyportal.eu/news/cheniere-energy-eyes-new-gas-pipeline-to-feed-lng-expansion-2/70190/
      rejected because: domain repurposed; capture is a Greek sports-betting
        page, not the Cheniere article

- [ ] **Sparrows Point LNG Terminal** — HTTP 404, archive: exists
      http://www.abc2news.com/news/region/baltimore-county/sparrows-point-lng-terminal-proposal-abandoned
      supports: “When the project was abandoned by AES Corporation, the news
        was publicly welcomed by many opponents of the plan, including US Rep.
        C.A. Dutch Ruppersberger.”
      capture:
      https://web.archive.org/web/20250607173341/http://www.abc2news.com/news/region/baltimore-county/sparrows-point-lng-terminal-proposal-abandoned
      rejected because: snapshot fetch status 404

- [ ] **Texas Gulf Terminals** — HTTP 200, archive: exists
      https://www.regulations.gov/docket?D=MARAD-2018-0114
      supports: “In July 2018 Trifigura applied to the Maritime Administration
        to build the project.”
      capture:
      https://web.archive.org/web/20250223161432/https://www.regulations.gov/docket?D=MARAD-2018-0114
      rejected because: 4.9 KB JS shell; regulations.gov renders client-side
        and is not archivable

- [ ] **Vista Del Sol LNG Terminal** — HTTP 404, archive: exists
      http://www.tradewindsnews.com/lngunlimited/307714/4gas-hoists-for-sale-sign-over-vista-del-sol-site
      supports: “The project was later cancelled, however; in March of 2010
        4Gas announced it was selling the Vista del Sol project site.”
      capture:
      https://web.archive.org/web/20250517053459/http://www.tradewindsnews.com/lngunlimited/307714/4gas-hoists-for-sale-sign-over-vista-del-sol-site
      rejected because: snapshot fetch status 404

- [ ] **Woodside Louisiana LNG Terminal** — HTTP 307, archive: exists
      http://bit.ly/2nOnpVz
      supports: “Woodside Louisiana LNG Terminal, known as Driftwood LNG
        Terminal until October 2024, is a proposed LNG terminal in Louisiana,
        United States.”
      capture:
      https://web.archive.org/web/20241120164918/http://bit.ly/2nOnpVz
      rejected because: snapshot fetch status 403

### 5h. Confirmed dead, no usable archive — need a replacement source (21)

Each of these returns a hard failure live **and** has no Wayback capture that can
be served, so nothing automated can recover them. They are the batch's genuine
residue and the only US items that need research rather than a click.

Four publisher-level facts are worth having before you start: `lngglobal.com` ×2
(today's site is unrelated, its sitemap starts December 2025 — see 5b),
`nasdaq.com` ×3 (article URLs expire by policy, and Nasdaq syndicates Reuters
copy, so the original Reuters piece is usually findable), `tradewindsnews.com`
(hard paywall, no captures) and `bit.ly` ×4 — a dead shortlink with no capture is
unrecoverable in principle, because the target is unknowable.

- [ ] **Alaska LNG Terminal** — HTTP 404, archive: none
      http://www.kpb.us/mayor/lng-project/lng-project-updates/902-alaska-lng-provides-more-details-on-project-construction
      supports: “The combined terminal and pipeline are projected to be the
        most expensive energy project in North American history.”
      Kenai Peninsula Borough mayor's page; the borough site was restructured.

- [ ] **Annova LNG Terminal** — HTTP 404, archive: none
      http://www.rgvforlng.com/brownsville-herald-annova-lng-slightly-moving-project-accommodate-ocelots/
      supports: “G announced their plans to slightly relocate the planned LNG
        to accommodate a wildlife-crossing culvert under Highway 48, a corridor
        used by endangered ocelots.”
      Advocacy site reprinting a Brownsville Herald story; the Herald original
        is the better target.

- [ ] **Annova LNG Terminal** · **Rio Grande LNG Terminal** · **Texas LNG Terminal** (one ref, 3 pages) — HTTP 522, archive: none
      https://www.kallanishenergy.com/2020/03/31/three-lawsuits-filed-against-brownsville-lng-projects/
      supports: “…f Engineers approval of a water permit for the plant and
        pipeline. The plaintiffs argue that the Corps failed to avoid or
        mitigate negative impacts to wetlands.”
      522 Cloudflare gateway timeout, not a 404 — the publisher is alive and
        this may simply recover.

- [ ] **Calcasieu Pass LNG Terminal** — HTTP 404, archive: exists
      https://www.nasdaq.com/articles/u.s.-approves-venture-global-la.-calcasieu-2-lng-plant-commissioning
      supports: “…cember 2021, FERC approved Venture Global LNG to begin
        commissioning liquefaction systems at the second block, having approved
        the first block in November 2021.”
      The CDX index *advertises* a June 2024 capture, but Wayback returns 404
        when it is requested — an indexed capture it cannot serve. Not usable.
      capture:
      https://web.archive.org/web/20240620043700/https://www.nasdaq.com/articles/u.s.-approves-venture-global-la.-calcasieu-2-lng-plant-commissioning

- [ ] **Calhoun LNG Terminal** — HTTP 404, archive: none
      http://www.hvllc.com/news/gulf-coast-lng-partners-lp-press-release-ferc-filing/
      supports: “…a Houston-based partnership formed between Gulf Coast LNG,
        LLC and Haddington Energy Partners II, LP, a private equity fund
        managed by Haddington Ventures, LLC.”
      Haddington Ventures press release. Also see 5e — this page additionally
        cites `killajoules.wikidot.com`.

- [ ] **Cameron LNG Terminal** — HTTP 404, archive: none
      http://cameronlng.com/pdf/Oct_EXT_NL%20final%20(pages).pdf
      supports: “By Fall of 2016 50% of the project's construction had been
        completed.”
      Sempra's own newsletter PDF; the file is gone from cameronlng.com and was
        never captured.

- [ ] **Casotte Landing LNG Terminal** — HTTP 404, archive: none
      https://us.eversheds-sutherland.com/NewsCommentary/Blogs/123823/Development-of-Casotte-Landing-LNG-Terminal-Terminated-by-Chevron
      supports: “In October of 2009, Chevron informed FERC that it stopped
        development of the project due to sufficient existing US regional LNG
        capacity.”
      Law-firm blog post; the firm is alive, so a title search on their site is
        the first thing to try.

- [ ] **CE FLNG Terminal** — no connection, archive: none
      https://www.construction-ic.com/HomePage/Projects?ReturnUrl=%2FProjects%2FOverview%2F195366%3Futm_source%3Dworldconstructionnetwork%26utm_medium%3DReferral%26utm_campaign%3DCE%2BFLNG%252FCE%2B%25E2%2580%2593%2BCambridge%2BEnergy%2BFloating%2BLNG%2B%25E2%2580%2593%2BLouisiana&utm_source=worldconstructionnetwork&utm_medium=Referral&utm_campaign=CE%20FLNG%2FCE%20%E2%80%93%20Cambridge%20Energy%20Floating%20LNG%20%E2%80%93%20Louisiana
      supports: “…of 2012, the Department of Fossil Energy permitted CE FLNG to
        export LNG associated with the proposed project, which would have been
        located in Louisiana, USA.”
      A login redirect (`ReturnUrl=`), so this never was a citable public URL.
        Needs a different source, not a repair.

- [ ] **Commonwealth LNG Terminal** — HTTP 404, archive: none
      https://ieefa.org/articles/ferc-staff-raise-environmental-justice-concerns-review-planned-louisiana-lng-project?utm_source=Inside+Gas&utm_campaign=a354fed1e6-EMAIL_CAMPAIGN_2022_09_15_11_03&utm_medium=email&utm_term=0_5666c2a85c-a354fed1e6-208473805
      supports: “September 2022, a FERC study found that the project would
        result in “disproportionately high and adverse” impacts for nearby
        environmental justice communities.”
      IEEFA is alive and reorganized its URLs; a title search will very likely
        find this.

- [ ] **Corpus Christi LNG Terminal** — HTTP 404, archive: none
      https://www.nasdaq.com/articles/cheniere-to-go-ahead-with-texas-corpus-stage-3-lng-export-plant
      supports: “In June 2022, Cheniere took a positive FID, indicating it will
        move forward with constructing Stage 3.”

- [ ] **CP2 LNG Terminal** · **Corpus Christi LNG Terminal** · **Plaquemines LNG Terminal** (one ref, 3 pages) — no connection, archive: none
      https://money.usnews.com/investing/news/articles/2022-06-22/cheniere-to-sell-lng-to-chevron-until-2042
      supports: “Venture Global announced a sales and purchase agreement with
        Chevron under which it will sell 2 mtpa split between CP2 LNG and its
        [[Plaquemines LNG Terminal]].”
      US News syndicated Reuters copy; the Reuters original is the thing to
        find.

- [ ] **CP2 LNG Terminal** — HTTP 404, archive: none
      https://www.lngglobal.com/venture-global-lng-20-year-supply-deal-with-jera?utm_source=substack&utm_medium=email
      supports: “In April 2023, Venture Global signed a 20-year, 1-mtpa SPA
        with Japan's JERA.”

- [ ] **Downeast LNG Terminal** — HTTP 410, archive: none
      http://bit.ly/2mKtcME
      supports: “…n import project, the project later submitted a new Federal
        Energy Regulatory Commission (FERC) filing in July 2014 as a bi-
        directional (import/export) project.”

- [ ] **Harbor Island (Lone Star) Oil Terminal** — HTTP 404, archive: none
      https://legistarwebproduction.s3.amazonaws.com/uploads/attachment/pdf/468660/CM__Approve_Amendment_to_Lease_Agreement_with_Lone_Star_Ports_Nov_12_2019.pdf
      supports: “…arlyle Group's Lone Star Ports, LLC (“LSP”). The lease was
        for approximately 200 acres of land on the north side of the Corpus
        Christi Ship Channel Inner Basin.”
      A Legistar agenda attachment — the item itself should still exist in the
        city's Legistar portal.

- [ ] **Harbor Island (Lone Star) Oil Terminal** — no connection, archive: unknown (throttled)
      https://www.ccbiznews.com/news/carlyle-group-out-of-port-corpus-christi-terminal
      supports: “In October 2019 the Carlyle group announced that it was
        withdrawing from the project, leaving the Berry group as the sole
        sponsor.”
      The one URL whose archive status is still unknown after four passes (see
        5e). Also fails to connect live.

- [ ] **New Fortress Grand Isle FLNG Terminal** — HTTP 404, archive: none
      https://www.nasdaq.com/articles/new-fortress-seeks-to-build-offshore-louisiana-lng-plant-by-q1-2023
      supports: “…ermits for a new FLNG facility that would use its modular
        "Fast LNG" technology, with the intention of making the unit
        operational by the first quarter of 2023.”

- [ ] **Plaquemines LNG Terminal** — HTTP 404, archive: none
      http://www.nola.com/business/index.ssf/2016/12/plaquemines_natural_gas_projec.html
      supports: “…company is also proposing the construction of two natural gas
        pipelines to connect existing pipelines to the site, including the
        [[Gator Express Gas Pipeline]].”
      The Times-Picayune's old `index.ssf` URL scheme is retired wholesale;
        nola.com's own search is the way in.

- [ ] **Point Comfort LNG Terminal** — no connection, archive: none
      http://bit.ly/2nOmXGR
      supports: “…up LNG, submitted an application to the US Department of
        Energy for long-term authorization to export LNG to free trade
        agreement countries in December of 2016.”

- [ ] **Sabine Pass LNG Terminal** — HTTP 404, archive: none
      https://www.lngglobal.com/cheniere-energy-secures-new-long-term-lng-deal-with-basf-to-support-expansion?utm_source=substack&utm_medium=email
      supports: “LNG on a free-on-board basis, beginning in 2026 and running
        through 2043. The deal is contingent on a positive final investment
        decision (FID) for train seven.”

- [ ] **Strom LNG Terminal** — no connection, archive: none
      http://bit.ly/2nOcHym
      supports: “Strom LNG Terminal is a proposed portable LNG terminal in
        Florida, United States.”

- [ ] **Weaver's Cove LNG Terminal** — HTTP 404, archive: none
      http://www.tradewindsnews.com/lngunlimited/309778/weavers-cove-lng-meets-resistance
      supports: “…e town of Somerset signed town resolutions opposing the
        project and calling on the Federal Energy Regulatory Commission (FERC)
        to deny approvals of the project.”

## 6. China (compiled 2026-07-29)

91 pages, 811 Background refs. The first repair wave is saved (5 pages, revs
1206908–1206912, 0 cite errors); the archive wave is still running, so the China
row in SCOPE.md is deliberately not marked done. Almost everything below comes
from one structural fact: a large share of the Chinese web answers bots with a
JavaScript shell, so an HTTP verdict on these hosts carries much less
information than it does on the Latin web. The items are sorted by what a human
actually has to do, not by what the scanner said.

As in §5, **every ref you have to look at carries its full URL on its own line**
— nothing is truncated and nothing needs to be looked up elsewhere. A `[n]` is
the scanner's index (the nth `<ref>` in Background, reuses included, counting
from 1), **not** the rendered footnote number, so use the page name and URL to
identify a ref, never a bare `[n]`.

### 6a. Refs no script can verify — 11 qcc.com company-registry lookups

One qcc.com ref on each of eleven pages. Every one supports an `Owner:` line in
Project Details, pointing at the corporate-registry entry for the named company.
qcc.com returns HTTP 200 and an identical 23,670-byte response for **any** firm
id, including ones invented on the spot, and the body contains **no Chinese
characters at all** — the company name never appears. So the scanner's `OK` on
ten of these and `BROKEN` on Zhuhai are both noise, and ten of the eleven
independently show up as `STILL_OFF` in the relevance pass for exactly the same
reason: there was never any text to match. **Nothing here is known to be wrong**
— this is a "cannot be checked", not a defect. A human with a browser settles
each in seconds. Recommendation: leave them as cited unless a spot-check shows a
mismatch, and do not let a future sweep "repair" them on the strength of a
verdict that means nothing.

Nine are plain `/firm/<id>` pages:

- [ ] **Chaozhou LNG Terminal (Huaying) [2]**
      https://www.qcc.com/firm/1bbe9d835035b5213147b40bdd3f3a8a.html
- [ ] **Guangdong Dapeng LNG Terminal [17]**
      https://www.qcc.com/firm/150051e6433719f95b82f249fe540fae.html
- [ ] **Jiangmen LNG Terminal [4]**
      https://www.qcc.com/firm/bb5174b7477f250a12f364b3670ce33b.html
- [ ] **Pinghu LNG Terminal [7]**
      https://www.qcc.com/firm/6e5acde4a6f56471ea8d89bbb6cd1719.html
- [ ] **Qidong LNG Terminal [19]**
      https://www.qcc.com/firm/af915a615cdc914eba150bbd6aa37d35.html
- [ ] **Yantai LNG Terminal [15]**
      https://www.qcc.com/firm/bd5675eaa22e2ec3b446924ababe11c9.html
- [ ] **Yueyang LNG Terminal [8]**
      https://www.qcc.com/firm/202f767e3fe93dbdc5051680e2f538e0.html
- [ ] **Zhuhai LNG Terminal [16]** — the one the scanner called `BROKEN` (it
      failed to connect rather than returning the usual shell)
      https://www.qcc.com/firm/4c312c6cb8daa15e07666f7482c50274.html

Two are the same `/firm/` form **wrapped in a login redirect**, whose `back=`
parameter holds the real firm path percent-encoded. Those unwrap mechanically to
the plain `/firm/<id>` form and will be handled with the other unwraps; it
changes the URL's shape, not its verifiability:

- [ ] **Fujian LNG Terminal [9]**
      https://www.qcc.com/weblogin?back=%2Ffirm%2Fc2ee94a792af2ee12f72c1bc82fe66ff.html
- [ ] **Shenzhen Diefu CNOOC LNG Terminal [11]**
      https://www.qcc.com/weblogin?back=%2Ffirm%2Fcf2352bae2e6cb242ccc9d2be07738de.html

And one is not a registry page at all but a **search query** for the company
name (广东阳江海陵湾液化天然气有限责任公司) — so even a working qcc.com would only
give a result list, never a citation. This one arguably needs replacing with the
firm page it finds, independent of the shell problem:

- [ ] **Yangjiang LNG Terminal [3]**
      https://www.qcc.com/web/search?key=%E5%B9%BF%E4%B8%9C%E9%98%B3%E6%B1%9F%E6%B5%B7%E9%99%B5%E6%B9%BE%E6%B6%B2%E5%8C%96%E5%A4%A9%E7%84%B6%E6%B0%94%E6%9C%89%E9%99%90%E8%B4%A3%E4%BB%BB%E5%85%AC%E5%8F%B8

### 6b. Confirmed dead, needing a replacement source

Ready-made searches for each; the recorded Chinese headline is the strongest
query in every case.

- [ ] **Ganyu LNG Terminal [2]** — cited to a **raw IP address**, which no longer
  answers:
  http://117.60.146.119/XXGK/ArticleDetail/61522
  The ref records a real and very specific document: 连云港市赣榆区人民政府-政府信息
  公开--关于同意江苏华电赣榆LNG接收站项目开展前期工作的复函 (Lianyungang Ganyu District
  government, reply approving preliminary work on the Jiangsu Huadian Ganyu LNG
  receiving terminal), dated 2014-07-01. The district government's real site is
  `ganyu.gov.cn`, so this is very likely recoverable.
  - `"关于同意江苏华电赣榆LNG接收站项目开展前期工作的复函"`
  - `site:ganyu.gov.cn 华电赣榆 LNG接收站 复函`
  - `江苏华电赣榆LNG接收站 前期工作 复函 2014`
- [ ] **Rudong LNG Terminal (GCL-Poly) [4]** — the other **raw IP**, also dead:
  http://58.221.238.232/ykgjjkfq/gggs/content/33ed6ab0-88b2-408d-9454-448a0f813059.html
  Title: 公告公示-协鑫汇东江苏如东LNG接收站项目环境影响评价第一次公示--如东县洋口港经济
  开发区 (first public notice of the environmental impact assessment, Yangkou Port
  Economic Development Zone), dated 2020-11-27. It supports the sentence about
  the local government publishing the EIA for comment a second time.
  - `"协鑫汇东江苏如东LNG接收站项目环境影响评价第一次公示"`
  - `site:rudong.gov.cn 协鑫汇东 LNG接收站 环境影响评价 公示`
  - `洋口港经济开发区 协鑫汇东 LNG 环评 公示 2020`
- [ ] **Longkou Nanshan LNG Terminal [2]** — now serves 该文章已不存在 ("this
  article no longer exists"), and **Wayback has no snapshot of it at all**:
  https://k.sina.com.cn/article_2620088113_9c2b5f3102000k2hn.html?from=news&subch=onews
  Unlike most bare external links this one carries a usable headline in its link
  text — 龙口南山LNG接收站项目获得核准 ("Longkou Nanshan LNG terminal project receives
  approval"), Sina, 9 October 2019 — so a replacement can be content-validated
  once found. Supports "As of October 2019, the project is officially permitted."
  - `"龙口南山LNG接收站项目获得核准"`
  - `龙口南山 LNG接收站 核准 2019`
  - `龙口南山 LNG接收站 发改委 核准 山东`

### 6c. Dead *and* mis-cited — the Zhejiang Online migration

Both of these are `zjol`/`thehour` URLs that now redirect to the Tide News front
page. They scanned `OK` because a homepage is a healthy 200; the relevance flag
is what caught them. See 6f before attempting a mechanical fix.

- [ ] **Damaiyu LNG Terminal [5]** — two problems, and the second outlives any
  link repair. The cited URL redirects to `tidenews.com.cn`, so the source is
  gone:
  https://www.thehour.cn/news/492212.html
  But the ref's own recorded title is 省纪委省监委公布两批漠视侵害群众利益问题专项治理
  工作成果 — a provincial discipline-inspection commission notice on misconduct
  governance — while the sentence it supports reads "The construction reportedly
  began in October 2021." **Even if the original article were recovered, its
  headline does not describe a construction start.** This needs a source for the
  October 2021 claim, or the claim trimmed; recovering the URL alone would not
  fix it.
- [ ] **Liuheng LNG Terminal (Sinopec) [3]** — same blanket redirect to the Tide
  News front page. Needs a replacement source for whatever it supported:
  https://zj.zjol.com.cn/news.html?id=1977261

### 6d. Browser checks — pages that exist but are JS-rendered

The scanner cannot read any of these; none is known to be broken.

- [ ] **Shanghai Yangshan LNG Terminal [19]** — `jfdaily.com` serves a
  byte-identical 11,355-byte shell for **every** id, including id=1 and
  id=999999999, with `此文章不存在或已下线` present in all of them. The tell is
  template markup, not a verdict. The ref's recorded headline is detailed and
  plausible (能源保障再升级！上海LNG站线扩建项目码头工程通过交工验收, 11 June 2025),
  so this is very likely fine as cited.
  https://www.jfdaily.com/staticsg/res/html/web/newsDetail.html?id=926813
- [ ] **Chaozhou (Huaying) [4], Weihai [1], Shenzhen [13]** — three
  `finance.eastmoney.com` articles that each return an identical 45,941-byte
  shell. Here the invalid-id probe is *reassuring*: a fabricated eastmoney id
  correctly 404s with 抱歉，您访问的页面不存在或已删除, so the server recognizes all
  three real ids and the articles exist — only their text is rendered in
  JavaScript.
  - Chaozhou LNG Terminal (Huaying) [4]
    http://finance.eastmoney.com/a/202012221746544959.html
  - Weihai LNG Terminal [1]
    http://finance.eastmoney.com/a/202003031404509512.html
  - Shenzhen LNG Terminal [13]
    https://finance.eastmoney.com/a/202401042951015244.html
- [ ] **Sinopec Longkou LNG Terminal [12]** — resolved, listed only so it is not
  re-flagged. A soft-404 recheck matched 资料不存在 on this sina finance bulletin,
  but the probe shows the cited id returns 24,003 bytes against 21,408 for two
  bogus ids and the tell does not reappear. The earlier hit was a transient error
  page; the ref is fine.
  https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?stockid=600028&id=11326983

### 6e. Relevance flags, read individually

The relevance pass ended with 59 `STILL_OFF` refs — no terminal-name keyword
found even after CJK-aware matching. **44 of those 59 are shells** (qcc,
bjx.com.cn, toutiao, bit.ly, 3g.k.sohu and friends) where the scanner saw
essentially no Chinese text, so relevance was never testable, and 5 more are the
dead or shell cases already listed above. The remaining 10 returned real text and
were read one by one. Only one turned out to be drift in the sense the flag
suggests — but three others are **dead in ways that scanned `OK`**, which is the
more useful catch:

**Newly confirmed dead (all scanned `OK`; each is a lone ref on its host, so
there is no wider cluster to sweep):**

- [ ] **Zhejiang Ningbo LNG Terminal [5]** — `cnenergy.org` is **a parked domain
  offered for sale** ("[cnenergy.org] is for sale … 域名 [cnenergy.org] 正在出售中").
  Supports "Phase 2 began construction in June 2018 … an additional 3 mtpa."
  http://www.cnenergy.org/yq/trq/201806/t20180628_590908.html
  - `中海油 宁波 LNG 二期 2018年6月 开工`
  - `浙江宁波LNG接收站 二期 开工 300万吨`
- [ ] **Jiangyin LNG Terminal (Zhongtian Energy) [1]** — redirects to the bare
  Tencent portal (`腾讯网`). Supports the opening identity sentence: a proposed
  2 mtpa terminal in Jiangsu, proposed by Zhongtian Energy, planned for operation
  in 2018.
  http://gu.qq.com/finance/3815533.html
  - `中天能源 江阴 LNG接收站 200万吨 2018`
  - `江阴 中天能源 液化天然气 接收站 拟建`
- [ ] **Shenzhen LNG Terminal [11]** — `zshq.zuiyouliao.com` resolves to a
  **plastics-industry price portal** (`塑料价格-塑料在线-塑料行情`), not the cited
  article. Supports "In September 2022, there was news on the progress of its
  storage tanks."
  https://zshq.zuiyouliao.com/zixun/detail-adb81181a0e94d25bc3e1f87ef706f23.html
  - `深圳 LNG接收站 储罐 2022年9月 进展`
  - `迭福 深圳 LNG 储罐 施工 2022`

**Genuine wrong source (the URL is alive — it is simply not about this project):**

- [ ] **Yantai LNG Terminal (PetroChina) [3]** — `xlxslny.com` is the corporate
  site of 河南心连心深冷能源股份有限公司 (Henan Xinlianxin Deep Cooling Energy),
  a Henan company with no connection to a PetroChina terminal in Yantai,
  Shandong. It is cited for "The delivering capacity is 3 mtpa." No archive can
  fix this; the sentence needs a different source.
  https://www.xlxslny.com/news/160.html

**Confirmed fine — listed so they are not re-flagged:**

- **West Guangdong LNG Terminal [10]** — 广东省人民政府办公厅关于印发广东省能源发展
  “十四五”规划的通知. This is exactly the Guangdong energy Five-Year-Plan document
  the sentence cites it for; it flagged only because a province-wide policy notice
  does not repeat the terminal's name in the text the scanner sampled.
  http://www.gd.gov.cn/zwgk/wjk/qbwj/yfb/content/post_3909371.html
- **Hongmei LNG Terminal [3]** — `jovo.com.cn` group-news page, whose text does
  carry 中国石油与九丰集团东莞LNG接收站 (the PetroChina/Jovo Dongguan terminal, i.e.
  this project). It flagged because the wiki title says "Hongmei" while the
  source says 东莞 (Dongguan).
  https://www.jovo.com.cn/m/News/NewsDetail?nodecode=600400100&id=100000088293674

**Still unjudgeable — bot walls and empty shells, no evidence either way. A
browser settles each:**

- [ ] **Jiangmen LNG Terminal [1]** — `tsbtv.tv`, JS shell
      http://www.tsbtv.tv/xinwen/taishanyaowen/2014-03-26/8908.html
- [ ] **Shanghai Yangshan LNG Terminal [7]** — `eworldship.com`, empty body
      http://www.eworldship.com/html/2019/Exhibition_0402/148145.html
- [ ] **Wenzhou Huagang LNG Terminal [6]** — `zjzhonglan.com`, serves a CAPTCHA
      interstitial (安全防护中)
      http://www.zjzhonglan.com/1732-xm-2022-08-30.html
- [ ] **Chaozhou LNG Terminal (Huafeng) [3]** — `inengyuan.com`, serves an
      interstitial (温馨提示)
      http://www.inengyuan.com/kuaixun/2460.html

### 6f. Traps recorded so they are not "fixed" mechanically

- **Do not rewrite `zjol`/`thehour` URLs onto `tidenews.com.cn` keeping the id.**
  The old hosts blanket-redirect to the front page, and Tide News does expose a
  `tidenews.com.cn/news.html?id=…` form that answers 200 for the same numbers —
  but the numbering was reassigned, so id=1977261 now returns an unrelated piece
  on homestays in Wenling. The rewrite looks like a textbook relocation and
  produces a citation that scans healthy and supports nothing. Only a headline
  check against the old ref's `title=` catches it.
- **The two `webcache.googleusercontent.com` refs cannot be unwrapped to a live
  page.** Google retired its cache, and the URL each one wraps is itself the
  question:
  - Qidong LNG Terminal [16] wraps a URL that **is live** — a clean relocation:
    https://www.js.msa.gov.cn/art/2022/12/7/art_51_1380962.html
  - Tianjin LNG Terminal (Beijing Gas Group) [3] wraps one that **404s**, so it
    needs an archive:
    https://www.ndrc.gov.cn/xxgk/zcfb/tz/202007/t20200731_1235150.html
    Note this ref's `title=` is a copy of the URL rather than a headline, so
    there is nothing to content-validate an archive against beyond the NDRC
    document path itself. (The same NDRC URL is cited unwrapped as ref [4] on the
    same page, where it 404s outright.)

### 6g. Still running

- [ ] **The archive wave.** `wb_fill.py -j3 diag_china.json` is working through
  313 lookups and archive.org is throttling hard (7 of the first 23 responses
  were `THROTTLED`, which must be retried and never read as "no archive"). It
  gates the remaining repair waves: the 9 verified lngworldnews→offshore-energy
  relocations, the translate.google and webcache unwraps, and the bot-walled
  clusters (gas.in-en.com ×19, Reuters ×12, S&P Platts ×5). Nothing is lost on
  interruption — `wb_cache.jsonl` resumes for free.

## Note

COVERAGE.md's France row records a dead TradeWinds ref left as-is, but no
TradeWinds URL exists on any French LNG page as of 2026-07-23 (the page has
likely been edited since) — treat it as resolved unless it resurfaces.
