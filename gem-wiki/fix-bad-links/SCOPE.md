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
LNG export (`python3 ../../../gem-db-ops/gem_query.py --all-fields lng -o
gem_lng.csv`) and sweep the union. That check found Oristano FSRU and Taranto
LNG Terminal (Italy) plus five pages missed by "done" batches — Vlora
(Albania), Cong Thanh / Dung Quat / Hiep Phuoc (Vietnam), Summit Matarbari
(Bangladesh) — all picked up in the 2026-07-28 batch.

Counts below are gem.wiki pages, deduped from a 2026-07-28 export (1,274 unit
rows → 838 distinct pages). Researchers are initials — this repo is public.

## Totals

| | Countries | Pages |
|---|--:|--:|
| In scope | 111 | 838 |
| Swept | 43 | 250 |
| **Remaining** | **68** | **588** |

Remaining pages by researcher: A.K. 111 · A.M. 109 · R.B. 109 · M.D. 98 ·
I.S. 85 · A.T. 54 · W.H. 22 · G.C. 0 · N.B. 0.

## Not in the assignments sheet

Three countries have GEM LNG terminals but no owner in the sheet — unassigned,
still in scope for link repair:

| Country | Pages |
|---|--:|
| New Zealand | 1 |
| Puerto Rico | 3 |
| Sierra Leone | 1 |

## By researcher

### N.B. — 13/13 countries swept (67 of 67 pages)

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

### A.M. — 7/26 countries swept (58 of 167 pages)

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

### W.H. — 2/5 countries swept (40 of 62 pages)

| Country | Pages | Swept | Notes |
|---|--:|---|---|
| Bangladesh | 12 | ✅ 2026-07-22 | Summit Matarbari added 2026-07-28 (uncategorized) |
| India | 28 | ✅ 2026-07-22 | |
| Iran | 7 | ❌ | |
| Pakistan | 11 | ❌ | |
| Sri Lanka | 4 | ❌ | |

### A.K. — 0/13 countries swept (0 of 111 pages)

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

### A.T. — 0/21 countries swept (0 of 54 pages)

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

### I.S. — 0/7 countries swept (0 of 85 pages)

| Country | Pages | Swept |
|---|--:|---|
| Australia | 28 | ❌ |
| Canada | 36 | ❌ |
| Papua New Guinea | 7 | ❌ |
| Republic of the Congo | 3 | ❌ |
| Senegal | 3 | ❌ |
| South Africa | 7 | ❌ |
| Tanzania | 1 | ❌ |

### M.D. — 0/3 countries swept (0 of 98 pages)

| Country | Pages | Swept |
|---|--:|---|
| China | 90 | ❌ |
| Hong Kong | 1 | ❌ |
| Taiwan | 7 | ❌ |

### R.B. — 0/2 countries swept (0 of 109 pages)

| Country | Pages | Swept |
|---|--:|---|
| Turkmenistan | 1 | ❌ |
| United States | 108 | ❌ |
