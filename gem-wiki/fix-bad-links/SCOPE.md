# Full scope — every LNG country, swept vs not swept

`COVERAGE.md` records what each completed batch *did*. This file is the
denominator: **every country in the LNG update assignments sheet**, whether or
not a batch has reached it, so the remaining work is visible at a glance.

**Scope rule (set 2026-07-28, replaces the old queue rule).** Scope is *all*
countries in the assignments sheet, independent of that sheet's `Complete?`
column. `Complete?` tracks the researcher's **data** update; it says nothing
about whether the wiki Background citations still resolve. Earlier batches
queued only `Complete? = FALSE` countries, which is why Italy, Spain and
Germany went unswept for months despite being among the largest European
page counts.

**Page universe = GEM DB export ∪ wiki category.** Enumerating
`Category:LNG Terminals in <Country>` alone under-counts: a page can exist with
no category. Cross-check the category list against the `Wiki` column of a fresh
LNG export (`python3 ../../../../gem-db-ops/gem_query.py --all-fields lng -o
gem_lng.csv`) and sweep the union. That check found Oristano FSRU and Taranto
LNG Terminal (Italy) plus five pages missed by "done" batches — Vlora
(Albania), Cong Thanh / Dung Quat / Hiep Phuoc (Vietnam), Summit Matarbari
(Bangladesh) — all picked up in the 2026-07-28 batch.

Counts below are gem.wiki pages, deduped from a 2026-07-29 export (1,274 unit
rows → 843 distinct pages). Researchers are initials — this repo is public.

**Read the assignments sheet with `gws-gem`, not the Drive MCP connector.** The
connector served a stale copy on 2026-07-29 — rows 113–115 came back empty
while `gws sheets +read --spreadsheet <key> --range 'A:G'` returned them
populated minutes later. That staleness is what makes a "missing from the
sheet" finding untrustworthy.

## Totals

| | Countries | Pages |
|---|--:|--:|
| In scope | 114 | 844 |
| Swept | 44 | 358 |
| **Remaining** | **70** | **486** |

Remaining pages by researcher: A.V. 111 · A.L. 109 · M.Z. 99 ·
I.M. 86 · A.M. 55 · W.A. 22 · R.R. 1 · G.C. 0 · N.F. 0 · unassigned 3.

China's count is 91, not the export's 90: the union with the wiki category adds
one page the export's `Wiki` column misses. Counts here are export-derived, so
other rows may be short by the same kind of gap until a batch reaches them.

## Sheet vs database — reconciled 2026-07-29

The assignments sheet now covers the LNG database exactly: **114 countries on
both sides, nothing missing in either direction.** New Zealand, Puerto Rico and
Sierra Leone — previously flagged here as absent — were added as rows 113–115,
appended below the sorted block with Region/Subregion left blank, so they sort
to the bottom rather than into their regions.

One country in the sheet still has **no researcher**:

| Country | Pages | Researcher |
|---|--:|---|
| Puerto Rico | 3 | *(blank in the sheet)* |

## By researcher

### N.F. — 13/13 countries swept (67 of 67 pages)

| Country | Pages | Swept | Notes |
|---|--:|---|---|
| Albania | 3 | ✅ 2026-07-21 | Vlora added 2026-07-28 (uncategorized) |
| Belgium | 1 | ✅ 2026-07-21 | |
| Croatia | 2 | ✅ 2026-07-21 | |
| France | 7 | ✅ 2026-07-21 | |
| Germany | 12 | ✅ 2026-07-28 | |
| Gibraltar | 1 | ✅ 2026-07-21 | |
| Greece | 6 | ✅ 2026-07-21 | |
| Italy | 18 | ✅ 2026-07-28 | 16 in the wiki category + Oristano FSRU and Taranto LNG Terminal, uncategorized |
| Malta | 1 | ✅ 2026-07-21 | |
| Montenegro | 1 | ✅ 2026-07-21 | |
| Netherlands | 4 | ✅ 2026-07-21 | |
| Portugal | 1 | ✅ 2026-07-21 | |
| Spain | 10 | ✅ 2026-07-28 | |

### G.C. — 21/21 countries swept (85 of 85 pages)

| Country | Pages | Swept |
|---|--:|---|
| Antigua and Barbuda | 1 | ✅ 2026-07-27 |
| Argentina | 6 | ✅ 2026-07-27 |
| Aruba | 1 | ✅ 2026-07-27 |
| Bahamas | 3 | ✅ 2026-07-27 |
| Brazil | 25 | ✅ 2026-07-27 |
| Chile | 6 | ✅ 2026-07-27 |
| Dominican Republic | 3 | ✅ 2026-07-27 |
| Ecuador | 2 | ✅ 2026-07-27 |
| El Salvador | 2 | ✅ 2026-07-27 |
| Guyana | 1 | ✅ 2026-07-27 |
| Haiti | 1 | ✅ 2026-07-27 |
| Honduras | 1 | ✅ 2026-07-27 |
| Jamaica | 2 | ✅ 2026-07-27 |
| Mexico | 17 | ✅ 2026-07-27 |
| Nicaragua | 1 | ✅ 2026-07-27 |
| Panama | 3 | ✅ 2026-07-27 |
| Peru | 2 | ✅ 2026-07-27 |
| Suriname | 2 | ✅ 2026-07-27 |
| Trinidad and Tobago | 1 | ✅ 2026-07-27 |
| Uruguay | 1 | ✅ 2026-07-27 |
| Venezuela | 4 | ✅ 2026-07-27 |

### A.L. — 7/26 countries swept (58 of 167 pages)

| Country | Pages | Swept | Notes |
|---|--:|---|---|
| Algeria | 2 | ❌ | |
| Bahrain | 1 | ❌ | |
| Brunei | 1 | ❌ | |
| Cambodia | 2 | ❌ | |
| Colombia | 12 | ❌ | |
| Egypt | 5 | ❌ | |
| Georgia | 1 | ❌ | |
| Indonesia | 25 | ❌ | |
| Kuwait | 2 | ✅ 2026-07-21 | reassigned to B.L. |
| Libya | 1 | ❌ | |
| Malaysia | 14 | ❌ | |
| Morocco | 3 | ❌ | |
| Myanmar | 7 | ❌ | |
| Oman | 2 | ❌ | |
| Philippines | 15 | ❌ | |
| Qatar | 3 | ✅ 2026-07-21 | reassigned to B.L. |
| Singapore | 3 | ✅ 2026-07-21 | reassigned to B.L. |
| South Korea | 14 | ❌ | |
| Sudan | 1 | ❌ | |
| Thailand | 7 | ✅ 2026-07-21 | reassigned to B.L. |
| Timor-Leste | 1 | ❌ | |
| Türkiye | 5 | ✅ 2026-07-21 | reassigned to B.L. |
| United Arab Emirates | 6 | ✅ 2026-07-21 | reassigned to B.L. |
| Vietnam | 32 | ✅ 2026-07-21 | reassigned to B.L.; 3 uncategorized pages added 2026-07-28 |
| Western Sahara | 1 | ❌ | |
| Yemen | 1 | ❌ | |

### W.A. — 2/5 countries swept (40 of 62 pages)

| Country | Pages | Swept | Notes |
|---|--:|---|---|
| Bangladesh | 12 | ✅ 2026-07-22 | Summit Matarbari added 2026-07-28 (uncategorized) |
| India | 28 | ✅ 2026-07-22 | |
| Iran | 7 | ❌ | |
| Pakistan | 11 | ❌ | |
| Sri Lanka | 4 | ❌ | |

### A.V. — 0/13 countries swept (0 of 111 pages)

| Country | Pages | Swept |
|---|--:|---|
| Estonia | 3 | ❌ |
| Finland | 6 | ❌ |
| Ireland | 5 | ❌ |
| Japan | 42 | ❌ |
| Latvia | 2 | ❌ |
| Lithuania | 2 | ❌ |
| Norway | 6 | ❌ |
| Poland | 2 | ❌ |
| Romania | 2 | ❌ |
| Russia | 25 | ❌ |
| Sweden | 4 | ❌ |
| Ukraine | 2 | ❌ |
| United Kingdom | 10 | ❌ |

### A.M. — 0/22 countries swept (0 of 55 pages)

| Country | Pages | Swept |
|---|--:|---|
| Angola | 2 | ❌ |
| Benin | 2 | ❌ |
| Botswana | 1 | ❌ |
| Cameroon | 3 | ❌ |
| Côte d'Ivoire | 1 | ❌ |
| Cyprus | 3 | ❌ |
| Djibouti | 1 | ❌ |
| Equatorial Guinea | 3 | ❌ |
| Gabon | 2 | ❌ |
| Ghana | 1 | ❌ |
| Guinea | 1 | ❌ |
| Iraq | 2 | ❌ |
| Israel | 4 | ❌ |
| Jordan | 2 | ❌ |
| Kenya | 1 | ❌ |
| Lebanon | 4 | ❌ |
| Mauritania | 3 | ❌ |
| Mauritius | 1 | ❌ |
| Mozambique | 7 | ❌ |
| Namibia | 1 | ❌ |
| Nigeria | 9 | ❌ |
| Sierra Leone | 1 | ❌ |

### I.M. — 0/8 countries swept (0 of 86 pages)

| Country | Pages | Swept |
|---|--:|---|
| Australia | 28 | ❌ |
| Canada | 36 | ❌ |
| New Zealand | 1 | ❌ |
| Papua New Guinea | 7 | ❌ |
| Republic of the Congo | 3 | ❌ |
| Senegal | 3 | ❌ |
| South Africa | 7 | ❌ |
| Tanzania | 1 | ❌ |

### M.Z. — 0/3 countries swept (0 of 99 pages)

| Country | Pages | Swept |
|---|--:|---|
| China | 91 | 🚧 2026-07-28 — swept (811 refs); first repair wave saved (5 pages, revs 1206908–1206912, 0 cite errors). Diagnosis complete and human-review items written up (HUMAN-REVIEW.md §6); archive wave running |
| Hong Kong | 1 | ❌ |
| Taiwan | 7 | ❌ |

### R.R. — 1/2 countries swept (108 of 109 pages)

| Country | Pages | Swept |
|---|--:|---|
| Turkmenistan | 1 | ❌ |
| United States | 108 | ✅ 2026-07-29 — 6 repair waves saved (68 pages, 99 saves, revs 1206820–1206907 + 1206935–1206952, 0 cite errors). Repair work complete; human items in [HUMAN-REVIEW.md](HUMAN-REVIEW.md) §5 — but 73 of the 112 archive-queue URLs need **no** repair (42 bot walls, 10 live paywalls/shells), so the open work is 21 dead URLs needing sources + 2 decisions |
