# Status — cite-error fixes (LNG terminal pages)

Living record of what's been fixed and what's left. Regenerate the lists from
`cite_error_results.json` + the `batch*_log.csv` files if they drift (the logs
are the ground truth for batch-mode work; the 13 pilot pages are listed in the
lng-terminals-researcher run record with their revision links).

Last updated: 2026-07-20 — **all 411 flagged pages fixed** (batch phase +
manual queue complete; every page re-verified live at 0 cite errors).

## Summary

| | pages |
|---|---|
| flagged by the 2026-07-20 crawl | 411 (of 842 crawled) |
| **fixed** (live, re-verified 0 cite errors) | **411** — all of them (1,067 definitions restored by the scripted/supervised repairs; 13 manual-queue pages fixed by hand by the user, 2026-07-20) |
| **remaining** | **0** |

Batches so far (each ~50 pages, alphabetical, user-approved per batch):

| run | scope | result | log |
|---|---|---|---|
| pilot (supervised) | Lake Charles + random 10 + 2 gate-rewrite fixes | 13 fixed | run record (lng repo) |
| batch 1 | ACWA → Brunsbüttel LNG | 44 fixed / 4 manual | `batch50_log.csv` |
| batch 2 | Brunsbüttel FSRU → Escobar FSRU | 50 fixed / 0 skips | `batch50b_log.csv` |
| batch 3 | Etinde FLNG → Hitachi LNG | 46 fixed / 4 manual | `batch50c_log.csv` |
| batch 4 | Ichthys FLNG → Mariveles LNG | 47 fixed / 2 manual / 1 no-orphans | `batch50d_log.csv` |
| batch 5 | Marshal Vasilevskiy FSRU → Rovuma FLNG | 95 fixed / 4 manual / 1 empty-def mix | `batch100e_log.csv` |
| empty-def pair (supervised) | Kutubdia (Reliance) FSRU, Moheshkhali Floating LNG | 2 fixed after recipe extension | wiki revs 1197848–1197849 |
| batch 6 | Rovuma LNG → Zhoushan LNG (+ Tamar retry) | 96 fixed / 2 manual / 1 dup-def | `batch100f_log.csv` |
| final page | Zhuhai LNG (didn't fit in batch 6's 99) | 1 fixed | `batch100g_log.csv` |
| manual: Port Arthur (supervised) | 6 spliced + stray `:0` tag after `<references />` deleted (its citation was already inline since a 2026-07-14 edit) | 1 fixed | wiki rev 1197987 |
| manual: Sumed BW FSRU (supervised) | prose was copied from Ain Sokhna FSRU with already-orphaned stubs: 3 defs recovered from that page's history, 3 re-sourced from verified articles (LNG Prime, PGJ, VesselFinder) | 1 fixed | wiki rev 1197992 |
| manual queue by hand (user) | the 13 remaining anchor-mismatch pages (Ain Sokhna → Sengkang), fixed directly on the wiki; re-verified 0 errors each | 13 fixed | wiki history 2026-07-20 |
| manual: Tamar + Mee Laung Gyaing (supervised) | Tamar: malformed duplicate `Oren` def → reuse of the clean def, `:0` uses → reuses of the user's new `:02` def; MLG: `Irr` splice (unblocked by the user's `bloom` hand-fix) | 2 fixed | wiki revs 1197993–1197994 |

## To do

1. **Heads-up to the Data Team** — the tracker-update bot pass (2025-10-16 primarily; March/July 2026 passes show the same pattern) regenerates the Project Details section and destroys `<ref name=X>…</ref>` definitions living there, orphaning the Background-prose reuses. Until fixed, future passes can re-break pages (our repairs re-home definitions at the first prose use, so they should survive).
2. **4 broken DB wiki links** (404s, GEM-DB side, not wiki side): `Penglai_LNG_Terminal_(Huapeike)` (page exists as `Penglai_LNG_Terminal`), `Damietta_FSRU`, `Nan'ao_LNG_Terminal`, `Sierra_Leone_LNG_Terminal` — candidate `wiki`-field fixes for a future lng-terminals Update batch.

## Fixed (411)


- ACWA LNG Terminal
- AMIGO FLNG Terminal
- Abadi LNG Terminal
- Acajutla FSRU
- Ace Gas Nigeria FLNG Terminal
- Adriatic LNG Terminal
- Ahlone LNG Terminal
- Ain Sokhna FSRU (by hand)
- Al-Faw FSRU Terminal
- Alaska LNG Terminal
- Alexandroupolis FSRU
- American LNG Titusville Terminal
- Amurang FSRU
- Andes Energy Terminal (by hand)
- Andrés LNG Terminal
- Angola LNG Terminal
- Annova LNG Terminal
- Antigua Power LNG Terminal
- Arctic LNG 1 Terminal
- Arctic LNG 2 Terminal
- Arctic LNG 3 Terminal
- Argent LNG Terminal
- Argentina LNG Terminal
- Argo FSRU
- Arkhangelsk LNG Terminal
- Aruba LNG Terminal
- Arzew-Bethioua LNG Terminal
- Atimonan LNG Terminal (by hand)
- Atlantic LNG Terminal
- Australasia Probolinggo FSRU
- BPCL Mangalore LNG Terminal
- Bac Lieu LNG Terminal
- Bahia Blanca GasPort FSRU
- Bahia FSRU
- Bahrain Hidd FLNG Terminal
- Bar LNG Terminal
- Batam LNG Terminal
- Batangas Clean Energy LNG Terminal (by hand)
- Ben Tre FSRU
- Benin FSRU
- BirAllah LNG Hub
- Black Sea LNG Terminal
- Blue Marlin Offshore Port
- Bontang LNG Terminal
- Botum Sakor LNG Terminal
- Brass LNG Terminal
- Brunei LNG Terminal
- Brunnsviksholme LNG Terminal
- Brunsbüttel FSRU
- Brunsbüttel LNG Terminal
- Buenaventura FSRU
- CE FLNG Terminal
- CP2 LNG Terminal
- Ca Na LNG Terminal
- Cai Mep LNG Terminal
- Calcasieu Pass LNG Terminal
- Cameron LNG Terminal
- Cameroon LNG Terminal
- Cap Lopez FLNG Terminal
- Cartagena FSRU (Colombia)
- Cat Hai FSRU
- Chan May LNG Terminal
- Chana LNG Terminal
- Chaozhou LNG Terminal (Huaying)
- Chernomorsky LNG Terminal
- Chhara LNG Terminal
- Chuanbi Island LNG Terminal
- Clifton Pier LNG Terminal
- Coatzacoalcos II LNG Terminal
- Coatzacoalcos LNG Terminal (CFE)
- Commonwealth LNG Terminal
- Constanta LNG Terminal
- Coral North FLNG Terminal
- Coral South FLNG Terminal
- Corpus Christi LNG Terminal
- Cosan FSRU
- Costa Azul LNG Terminal
- Costa Norte LNG Terminal
- Cove Point LNG Terminal
- Crown Kakinada LNG Terminal
- Cyprus FSRU
- Cyprus LNG Terminal
- Dabhol LNG Terminal
- Dahej LNG Terminal
- Damietta SEGAS LNG Terminal
- Delfin FLNG Terminal
- Delimara FSRU
- Dhamra LNG Terminal
- Dioriga FSRU
- Dislub Maranhão FSRU
- Djibouti FLNG Terminal
- Dua FLNG Terminal
- Dua Malaysia LNG Terminal
- Dunkirk LNG Terminal
- Eagle LNG Terminal
- Eemshaven FSRU
- Egyptian LNG Terminal
- Elba Island LNG Terminal
- Ennore LNG Terminal
- Escobar FSRU
- Etinde FLNG Terminal
- Etki FSRU
- FGEN Batangas FSRU
- Far East LNG Terminal (by hand)
- Filipinas LNG Gateway Project FSRU (by hand)
- Firebird LNG Terminal
- Fortuna FLNG Terminal
- Fos Cavaou LNG Terminal
- Fourchon LNG Terminal
- Freeport LNG Terminal
- Fujairah LNG Terminal
- Fujian LNG Terminal
- G2 LNG Terminal
- Galveston Bay LNG Terminal
- Gate LNG Terminal
- Gato Negro Manzanillo LNG Terminal
- Geramar FSRU
- Gibbstown Deepwater Port LNG Terminal
- Gioia Tauro LNG Terminal
- Golar Nigeria FLNG Terminal
- Golden Pass LNG Terminal
- Gopalpur LNG Terminal
- Gorgon LNG Terminal
- Gorontalo FSRU (by hand)
- Grain LNG Terminal
- Gran Canaria LNG Terminal
- Grand Isle Deepwater Port Terminal
- Grangemouth FSRU
- Grassy Point LNG Terminal
- Greater Tortue Ahmeyim FLNG Terminal
- Gresik LNG Terminal
- Guanabara Bay FSRU
- Guangdong Dapeng LNG Terminal
- Guangzhou Nansha LNG Terminal
- Guinea LNG Terminal
- Gulf LNG Terminal
- Gulf of Saros FSRU
- Gulf of Thailand FSRU
- Gulfstream LNG Terminal
- Gwangyang LNG Terminal (by hand)
- H-Energy Kakinada LNG Terminal
- HIGAS LNG Terminal
- Hai Lang LNG Terminal
- Hamina LNG Terminal
- Hammerfest LNG Snohvit Terminal
- Harbor Island (Lone Star) Oil Terminal
- Hibiki LNG Terminal
- Hidrovias do Brasil FSRU
- Himeji LNG Terminal
- Hitachi LNG Terminal
- Huizhou LNG Terminal
- Ichthys FLNG Terminal
- Ilo LNG Terminal
- Imetame LNG Terminal
- Incheon LNG Terminal (by hand)
- Inkoo FSRU
- Iran NIOC LNG Terminal
- Itacoatiara FSRU
- Itaqui FSRU
- Ivory Coast FSRU
- Jafrabad FSRU
- Jaigarh LNG Terminal
- Jambelí FSRU
- Jawa Satu FSRU
- Jebel Ali FLNG Terminal
- Jiangyin LNG Terminal (Zhongtian Energy)
- Jieyang LNG Terminal (PetroChina)
- Joetsu LNG Terminal
- Jordan Cove LNG Terminal
- KOGAS Dangjin LNG Terminal
- Kanbauk FSRU
- Kara LNG Terminal
- Karaikal FSRU
- Karimun Island LNG Terminal
- Kawagoe LNG Terminal
- Kenai LNG Terminal
- Khanh Hoa LNG Terminal
- Khor Al-Zubair FSRU
- Klaipeda FSRU
- Kollsnes LNG Terminal
- Krishna Godavari FSRU
- Krishnapatnam FSRU
- Krk FSRU
- Ksi Lisims FLNG Terminal
- Kukrahati LNG Terminal
- Kulevi LNG Terminal
- Kutubdia (Reliance) FSRU
- LNG Alliance Mangalore FSRU
- LNG Easy Floating LNG Terminal
- LNG Yakutia Terminal (by hand)
- Lakach Field FLNG Terminal
- Lake Charles LNG Terminal
- Le Havre FSRU
- Liuheng LNG Terminal (Zhejiang Energy)
- Long Son LNG Terminal
- Louisiana Offshore Oil Port
- Lubmin FSRU
- Lubmin RWE FSRU
- Lysekil LNG Terminal
- MCV LNG Terminal
- Madura FLNG Terminal
- Magnolia LNG Terminal
- Main Pass Energy Hub FLNG Terminal
- Malaysia LNG Terminal Train 9
- Manzanillo (Dominican Republic) LNG Terminal
- Map Ta Phut LNG Terminal 2
- Mariveles LNG Terminal
- Marshal Vasilevskiy FSRU
- Matarbari GE LNG Terminal
- Matola FSRU
- Mauritius FSRU
- Mee Laung Gyaing FSRU (bloom by hand; Irr spliced)
- Mejillones LNG Terminal
- Mina Al-Ahmadi LNG Terminal
- Moheshkhali Floating LNG Terminal
- Mombasa LNG Terminal
- Montego Bay LNG Terminal
- Montoir LNG Terminal
- Morocco FSRU
- Mowi LNG Terminal
- Mozambique LNG Terminal
- Mugardos LNG Terminal
- Mui Ke Ga FSRU
- Mukran FSRU
- Mumbai FSRU
- Mundra LNG Terminal
- NOLA Oil Terminal
- Nador FSRU
- NewMed FLNG Terminal
- New Fortress Altamira LNG Terminal
- New Fortress Banda LNG Terminal
- New Fortress Barcarena FSRU
- New Fortress Grand Isle FLNG Terminal
- New Fortress Wyalusing LNG Terminal
- NextDecade Cork FSRU
- Nghi Son LNG Terminal
- Nigeria LNG Terminal
- Niihama LNG Terminal
- Nimofast Antonina LNG Terminal
- Nopetro LNG Terminal
- Northeast Asia LNG Hub Terminal
- Northeast Gateway FSRU
- Northern Territory LNG Terminal
- Northern Vietnam LNG Terminal
- Obsky LNG Terminal
- Ohgishima LNG Terminal
- Old Harbour FSRU
- Olokola LNG Terminal
- Oman Qalhat LNG Terminal
- POSCO Dangjin LNG Terminal
- Pagbilao Grande Island LNG Terminal
- Pakistan State Oil LNG Terminal
- Paldiski FSRU
- Paldiski LNG Terminal
- Palu LNG Terminal
- Paraná FSRU
- Payra FSRU
- Payra LNG Terminal
- Pecém FSRU
- Pechora LNG Terminal
- Penco Lirquén FSRU
- Penn LNG Terminal
- Penuelas LNG Terminal
- Pertamina Bangladesh FSRU
- Peru LNG Terminal
- Philippines LNG Terminal
- Pichilingue LNG Terminal
- Pilot Cork FSRU
- Pinghu LNG Terminal
- Plaquemines LNG Terminal
- Plaquemines Oil Terminal
- Pluto LNG Terminal
- Pointe LNG Terminal
- Polish Baltic Sea Coast FSRU
- Port Arthur LNG Terminal
- Pori LNG Terminal
- Port Meridian FSRU
- Port Phillip Bay FSRU
- Port of Vlora FSRU
- Porto Empedocle LNG Terminal
- Porto Norte Fluminense FSRU
- Porto do Açu FSRU
- Portovaya LNG Terminal
- Portovesme FSRU
- Prelude FLNG Terminal
- Presidente Kennedy FSRU
- Project Venezuela LNG Terminal
- Puerto Sandino FSRU
- Puerto de la Luz LNG Terminal
- Punta Europa LNG Terminal
- Pyeongtaek LNG Terminal (by hand)
- Qatar North Field LNG Terminal
- Qidong LNG Terminal
- Qilak LNG Terminal
- Quang Nam LNG Terminal
- Quanzhou LNG Terminal
- Quezon LNG Terminal
- Quintero LNG Terminal
- Rakhine LNG Terminal
- Rauma LNG Terminal
- Revithoussa LNG Terminal (by hand)
- Richards Bay Transnet FSRU
- Riga FSRU
- Rio Grande LNG Terminal
- Risavika LNG Terminal
- Riverside LNG Terminal
- Rostock LNG Terminal
- Rovuma FLNG Terminal
- Rovuma LNG Terminal
- Rudong LNG Terminal (PetroChina)
- Ruwais LNG Terminal
- São Marcos Bay FSRU
- SLNG 2 LNG Terminal
- Sabine Pass LNG Terminal
- Safe Harbor Energy LNG Terminal
- Saguaro Energía LNG Terminal
- Sakhalin II LNG Terminal
- Saldanha Bay FSRU
- Salina Cruz LNG Terminal (CFE)
- Salina Cruz LNG Terminal (Pilot/GFI)
- San Juan LNG Terminal
- Sea Port Oil Terminal (SPOT)
- Sengkang LNG Terminal (by hand)
- Sepetiba Bay FSRU
- Sergipe FSRU
- Shannon FSRU
- Sharjah FSRU
- Sheikh Sabah LNG Terminal
- Shenzhen Diefu CNOOC LNG Terminal
- Shtokman LNG Terminal
- Sinolam LNG Terminal
- Skulte LNG Terminal
- Soma Port LNG Terminal
- Son My LNG Terminal
- Songkhla FSRU
- Sorong LNG Terminal
- South East LNG Terminal
- South Hook LNG Terminal
- South West FSRU
- Stade FSRU
- Stade LNG Terminal
- Suape FSRU
- Sudan Red Sea LNG Terminal
- Sulawesi-Maluku LNG Cluster
- Sumed BW FSRU
- Summit FSRU
- Summit Matarbari FSRU
- Sunrise FLNG Terminal
- Surat Thani FSRU
- Sycar Venezuela FLNG Terminal
- TGNL São Luis FSRU
- Tabangao FSRU
- Tabeer LNG Terminal
- Taimyr LNG Terminal
- Talcahuano FSRU
- Tallinn LNG Terminal
- Tamar FLNG Terminal (dup-def + orphans)
- Tambey LNG Terminal
- Tangguh LNG Terminal
- Tangshan LNG Terminal (PetroChina)
- Teesside GasPort FSRU
- Telfers FSRU
- Teluk Lamong LNG Terminal
- Tema FSRU
- Tenerife LNG Terminal
- Tepor Macaé FSRU
- Terminal Gás Sul FSRU
- Terneuzen FSRU
- Texas Crude Offshore Loading Terminal
- Texas GulfLink Deepwater Port
- Texas LNG Terminal
- Thai Binh FSRU
- Thessaloniki FSRU
- Thi Vai LNG Terminal
- Thilawa LNG Terminal
- Thrace FSRU
- Tianjin LNG Terminal (Beijing Gas Group)
- Tien Giang LNG Terminal
- Tien Lang FSRU
- Tiga FLNG Terminal
- Tiga Malaysia LNG Terminal
- Tornio Manga LNG Terminal
- Toscana FSRU
- Transoceanic Nigeria FLNG Terminal
- UTM Offshore FLNG Terminal
- Ulsan LNG Terminal
- Ust Luga LNG Terminal
- Valentina LNG Terminal
- Venezuela Offshore LNG Terminal
- Vires FSRU
- Vista Pacifico LNG Terminal
- Vung Ang LNG Terminal
- Vysotsk LNG Terminal
- Walvis Bay LNG Terminal
- Wenzhou LNG Terminal
- West Papua FLNG Terminal
- Woodside Louisiana LNG Terminal
- Woodside Probolinggo LNG Terminal
- Yakutia LNG Project
- Yamal LNG Terminal
- Yancheng LNG Terminal
- Yangjiang LNG Terminal
- Yantai LNG Terminal
- Yemen LNG Terminal
- Zeebrugge LNG Terminal
- Zeeland Energy FSRU
- Zhangzhou LNG Terminal
- Zhangzhou LNG Terminal (China Energy Reserve)
- Zhoushan LNG Terminal
- Zhuhai LNG Terminal
- Świnoujście Polskie LNG Terminal

## Remaining (0)

None — every scriptable page has been attempted; see the manual queue above.
