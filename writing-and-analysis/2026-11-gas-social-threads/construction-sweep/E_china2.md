# E_china2: Anhui and Guizhou gas pipeline network rows, status "construction"

Checked 2026-11-19. Read-only. Nothing was edited.

## How to read this file

- Tooling was a problem. The built-in web search returned almost nothing useful for these segments. Sogou and Bing blocked or ignored Chinese queries from curl. Baidu worked only through the Chrome browser.
- Most Chinese government pages refused automated fetches. Xiuning gov returned 412 (anti-bot). Chuzhou gov and Hefei gov returned 403. The Anhui DRC page returned 403 (geo block). The Guizhou SASAC page (gzw.guizhou.gov.cn) returned 404. A Wayback copy could not be fetched from here.
- "Snippet-only" below means I read the text on a Baidu results page but did not open the original article. Those claims need a human to open the original before any edit.
- "Opened" means I read the page itself.
- No StartYear1 is filled for any of the 31 rows, so the "start year has passed" test was applied to ConstructionYear and to age.
- Rows I did not check at all are listed at the end. They are marked "not checked".

## Summary of verdicts

- Likely wrong (status or extent): P5636, P4956, P4975, P4583 (probable duplicate), P7526 (umbrella row that double counts)
- Likely wrong, Qiandongnan group, probably commissioned: P4980, P7492, P7513, P7524, P4992
- Needs researcher check: P5616, P4591, P5626, P4580, P4979, P4981, P4982
- Data flags with no status finding: owner "Sonatrach SpA" on P7492, capacity outliers on P4992, P7524, P4980
- Not checked: see end of file

## Anhui Gas Pipeline Network

### P5636 Hefei-Chaohu Gas Transmission Line
- Tracker: construction since 2020. 70 km, DN700, 1.39 bcm/y. Dianbu Town to Huashan. Owner Hefei Heran China Resources Gas (100%). No StartYear1.
- Found: It was put into operation on 13 March 2026. The gate-opening ceremony was at the Dianbu gas station in Feidong County. Pipeline length is given as 76 km, not 70. Investment is given as 6.5 billion yuan. It connects to the PipeChina Su-Wan gas pipeline and feeds the Chaohu–Jiangbei industrial zone trunk line and the Wuhu LNG river terminal. The owner matches the Hefei gas utility (合燃华润燃气).
- Verdict: likely wrong. Status should be operating.
- Suggested change: set status to operating, StartYear1 2026, StartMonth1 3. Change length from 70 to 76 km after checking the original. Add the new source. Capacity 1.39 was not checked.
- Sources (all snippet-only, read on a Baidu results page):
  - Anhui Provincial Development and Reform Commission, 2026-03-17. Gist: "On 13 March the Hefei to Chaohu section of the Huan Chaohu high-pressure line was formally put into gas operation. Pipeline is 76 km long."
  - People's Daily Online, 2026-03-20 (repost of a provincial energy bureau item). Same gist, 76 km.
  - Hefei Heran China Resources Gas WeChat repost, March 2026. Gist: "valve opened at Dianbu station in Feidong, three years of construction, 650 million yuan invested."
  - Baidu Baike entry for the Lujiang–Chizhou line says the ring-city network, Lu-Chi line and He-Chao line were connected one after another. Snippet-only.

### P7526 Huanchaohu High-Pressure Gas Pipeline
- Tracker: construction since 2020. 189 km. No endpoints, no capacity. It lists two sections, He-Chao and Lu-Chao. Owner Hefei Heran China Resources Gas.
- Found: This looks like an umbrella row. The He-Chao section is P5636 (now operating, 76 km). The Lu-Chao section is sibling P7527 (operating 2021, 112 km). 76 + 112 = 188, close to 189. So the row double counts length that two other rows already hold. A Hefei public-resources tender (2025-03-03, snippet-only) names the Lujiang–Chaohu line as a separate project with its own valve chambers.
- Verdict: needs researcher check. It is no longer a construction project in any reading.
- Suggested change: either set it to operating or mixed, or fold it into its two parts so length is not counted twice.
- Sources: same as P5636 (snippet-only). The tracker's own source (hefei.gov.cn/bmts/110159599.html) was not opened.

### P4583 Eastern North-South Backbone Gas Pipeline (Huaibei–Chuzhou)
- Tracker: construction since 2021. 281 km, 4.66 bcm/y. Lieshan to Laian. Owner Sinopec Wanneng Natural Gas.
- Found: The 281 km, 4.66 bcm/y, Sinopec Wanneng numbers are those of the whole Northeast Anhui (Wandongbei) pipeline, not a Huaibei–Chuzhou line. Baidu Baike (snippet read on the page, entry opened) says the Wandongbei pipeline is 281 km, 46.6 hundred million m3/y, through Chuzhou and Ma'anshan, with Phase I Tianchang–Laian–Fengyang and Phase II Laian–Quanjiao–He County. Sibling P4590 (Phase I, operating 2023, 188 km) and P4591 (Phase II, 179 km) already cover it. The Baidu AI summary also said the "Eastern longitudinal line" for Huaibei–Chuzhou has no public confirmation of gas supply. Huaibei end is not part of Wandongbei.
- Verdict: likely wrong. Probable duplicate.
- Suggested change: researcher to decide whether this row is a duplicate of P4590 plus P4591. If so, remove or merge. If a real Huaibei–Chuzhou line exists, the endpoints, owner and capacity need new sources.
- Sources: Baidu Baike, "皖东北天然气管道", opened 2026-11-19 (undated, Baidu Baike). Gist: "Total length 281 km, 8 districts and counties in Chuzhou and Ma'anshan, design capacity 4.66 bcm/y." Baidu AI answer for the Eastern line (snippet-only, low reliability).

### P4591 Northeast Anhui Natural Gas Pipeline Phase II (Chuzhou–Ma'anshan)
- Tracker: construction since 2022. 179 km, 4.66 bcm/y (this is the whole-line capacity, probably not the Phase II figure). Laian to He County. Sinopec Wanneng. Researcher note Q3 2025: main works done, not yet in operation.
- Found: No commissioning report found. Baidu Baike (opened) lists Phase II as 179 km: the Anhui East branch 151 km plus four connecting lines of 28 km, DN700, 10 MPa. It mentions a Wujiang branch (17.56 km) off the East branch with its own stations, which suggests the East branch is far along. A snippet on the Anhui DRC price notice (2024-08-08) says the short-haul price of 0.20 yuan for the Wandongbei trunk, the Wanbei branch and the Wandong branch starts from the day each section formally carries gas. That implies the East branch was due to carry gas by then. Not opened, so not proof.
- Verdict: needs researcher check. It may already be operating.
- Suggested change: search the Chuzhou and Ma'anshan governments and Sinopec Wanneng for a 通气 notice for the 皖东支线. If found, set to operating and add the date. The 4.66 bcm/y capacity likely belongs to the whole project, not Phase II.
- Sources: Baidu Baike "皖东北天然气管道" (opened). Anhui DRC price notice, 2024-08-08 (snippet-only). Tracker source chuzhou.gov.cn returned 403.

### P5616 Taihe-Yingdong Gas Transmission Trunkline
- Tracker: construction since 2020. 86 km, DN500, 0.65 bcm/y. Taihe to Yingdong. Owner Fuyang Guozhen Gas (100%).
- Found: The tracker's own source (Fuyang Guozhen Gas, 2022-10-01, opened) says the line was restarted on 2020-11-12, and in September 2022 reached full physical connection except the first station. It was approved on 2016-11-09. Length 86 km, 6.3 MPa, DN500, owner Baichuan Energy's Fuyang Guozhen. Length, diameter and owner match. The page does not say gas was commissioned. A Fuyang government item (2026-03, snippet-only) says nine gas transmission trunk lines totaling over 392 km are in operation and Taihe and Yingdong are covered by gas. A Fuyang emergency bureau list (2025-08, snippet-only) shows hazardous chemicals licences for Yingdong-section pipelines, not this line by name.
- Verdict: needs researcher check. Probably operating by now.
- Suggested change: ask Fuyang Guozhen or the Fuyang DRC when the first gas went through. If before 2026, set to operating.
- Sources: Fuyang Guozhen Gas company site, "太和--颍东天然气干线工程如期实现物理连接", 2022-10-01 (opened). Fuyang municipal government item on gas supply, March 2026 (snippet-only).

### P5626 Huizhou-Xiuning Gas Transmission Line
- Tracker: construction. 23.6 km, 0.40 bcm/y. Pipeline finished Dec 2024, stations March 2025, not yet operating (Q3 2025 note). Owner Huaihe Energy Gas Group.
- Found: nothing. The Xiuning gov page returned 412 (anti-bot) and my searches found no commissioning report.
- Verdict: needs researcher check. An 18-month-old finished pipeline is likely in service.
- Suggested change: check Huangshan and Xiuning news and Huaihe Energy Gas for 通气. Set to operating if found.
- Sources: none opened.

### P4580 Bengbu–Hefei Gas Pipeline
- Tracker: construction since 2020. 103 km, 3.00 bcm/y. Sections I (30.56 km) and II (47.175 km) done, III (22.48 km) under construction as of Q3 2025. Owner Huaihe Energy Gas Group.
- Found: nothing confirmed. A Baidu image-caption on the results page read like a headline that the third section of the Bengbu–Hefei line is now operating, but I could not tie it to an article or date. I am not relying on it. Sections I and II are reported complete. The row is one status for three parts.
- Verdict: needs researcher check. Likely mixed (two sections done).
- Suggested change: if sections I and II are in service, split the row or mark it mixed, and look for the section III date.
- Sources: none opened.

### P4593 Suzhou–Huaibei–Xiao County–Dangshan Gas Pipeline
- Not checked beyond one search that returned nothing. Tracker says 180 km, 0.88 bcm/y, construction since 2023, Anhui Province Natural Gas Development.

### P5622 Taihu-Qianshan Branch
- Not checked. Tracker note says essentially complete, not commissioned (Q3 2025). 40.7 km, 0.19 bcm/y. One Baidu hit for the title "Taihu Qianshan natural gas branch connected to Longrun" was seen but not opened.

### P4582 Chaohu–Jiangbei District Gas Pipeline
- Not checked. Huashan to Baiqiao, 79 km, 2.00 bcm/y. Related to the Huan-Chaohu ring (the He-Chao line ends at Huashan station), so a commissioning check on the Chaohu–Jiangbei trunk is worth doing.

### P4589 Middle North–South Backbone (Suzhou–Huangshan) and P4594 Western North–South Backbone (Bozhou–Chizhou)
- Not checked. Both are multi-segment umbrella rows (700 km and 500 km) with no capacity. Siblings already show operating segments (for example P4595, P4601), so these rows probably mix statuses and may double count.

## Guizhou Gas Pipeline Network

### P4956 Jinsha-Qianxi-Nayong Branch Pipeline
- Tracker: construction since 2023. 146 km, 4.00 bcm/y. Baili Rhododendron to Nayong County. Owner Guizhou Kunlun Natural Gas.
- Found: A NetEase summary of Guizhou Kunlun's 2026 preliminary-work filings (snippet-only, about 2026-11-16) says the Qianxi–Zhijin section is still under construction. The Zhijin–Nayong section and the Hezhang–Weining section were stated in writing in March 2026 to be no longer under construction by Kunlun.
- Verdict: likely wrong on extent.
- Suggested change: shorten the row to the Jinsha–Qianxi–Zhijin part and move Zhijin–Nayong to cancelled or shelved. Check the length split and capacity (4.00 bcm/y looks high for a branch).
- Sources: NetEase subscription article read on a Baidu results page, circa 2026-11-16 (snippet-only). Original not opened.

### P4975 Hezhang-Weining Gas Pipeline
- Tracker: construction. 57.2 km, 1.50 bcm/y. Owner Guizhou Kunlun Natural Gas.
- Found: Same NetEase item (snippet-only). Kunlun says it is no longer building Hezhang–Weining, and the line is being moved to a new implementing company through provincial coordination. So the owner is probably wrong, and it is unclear whether construction began.
- Verdict: likely wrong (owner, and possibly status).
- Suggested change: find the new owner. Move to proposed if no works have started.
- Sources: same as P4956.

### P4979 Tongren City County-to-County Gas Pipeline
- Tracker: construction since 2024. 393 km, 0.83 bcm/y. Yuping to Yanhe. Owner Tongren Energy Investment Group.
- Found: The details match the Tongren DRC reply of 2024-12-11 (snippet-only): seven branch lines, about 400 km, about 830 million m3/y, 1.965 billion yuan, built by Tongren Energy Investment Group, from the Yuping gate station to the Yanhe end station. The company's 2021 page gives 393 km. The 2026 Tongren government work report (2026-02-14, snippet-only) still says "speed up the county-to-county gas project", so the whole project was still under construction in early 2026. Some lines may be done. The Baidu AI answer claimed Yanhe and Sinan had been put into service, but I could not trace that to a source, so I discount it.
- Verdict: needs researcher check. Status is plausible for the project as a whole.
- Suggested change: P4984 (Ala-Wanshan), P4985 (Jiangkou-Sinan) and P4986 (Houba-Yanhe) are likely parts of the same 393 km project. Check for double counting. Check each branch for commissioning.
- Also a lead: Tongren Natural Resources Bureau, 2026-10-20 (snippet-only), approved temporary land for the Fenggang–Dejiang gas pipeline (Dejiang section, phase II). That implies an active Fenggang–Dejiang line in Oct 2026. It may relate to a tracker row such as P4965 (shelved) or P4976 (proposed).
- Sources: Tongren DRC reply, 2024-12-11; Tongren Energy Investment Group "县县通工程项目工作纪实", 2021-12-27; Tongren government work report 2026-02-14. All snippet-only.

### Qiandongnan Prefecture group: P4980, P7492, P7513, P7524, P4992, P4981, P4982
- Tracker: all in construction. Years: P4980 Kaili-Huangping (C2024, 52.78 km, 0.01 bcm/y), P7492 Kaili-Danzhai (C2024, 44.6 km), P7513 Kaili-Leishan (C2024, 31.02 km), P7524 Huangping-Shibing (C2024, 29.76 km, 3.67 bcm/y), P4992 Luoxiang-Rongjiang (C2025, 73.53 km, 18.03 bcm/y), P4981 Tianzhu-Liping (103 km, 0.34), P4982 Liping-Congjiang (73 km, 0.34).
- Found:
  - The Qiandongnan prefecture plan for urban gas and gas infrastructure 2024 to 2027 (prefecture government, 2024-09-03, snippet-only) says Kaili–Danzhai and Congjiang (Luoxiang)–Rongjiang were to be built and put into operation in 2024. Kaili–Huangping, Liping–Congjiang (Luoxiang) and others were to be done in 2025. Sandu–Danzhai starts in 2026.
  - A Qiandongnan investment bureau item (2024-10-15, snippet-only) says the county network was 498.04 km in total, with 439.5 km (88.25%) of pipe already laid, including Huangping–Shibing and Kaili–Leishan.
  - A Baidu AI summary dated November 2026 says Danzhai and Leishan have pipelines in place and are awaiting formal urban gas supply. This is AI text, not a source. I treat it as weak.
  - A Qiandongnan DRC reply (2025-07-15, snippet-only) shows Cengong still lacked piped gas, so not all counties are connected.
- Verdict: likely wrong for P4980, P7492, P7513, P7524 and P4992. They are probably built and may be operating. P4981 and P4982 are needs researcher check (no information found).
- Suggested change: search Dongli Energy (黔东南 东力能源) and the Qiandongnan Energy Bureau for 通气 notices on each line. Set operating with the date where found.
- Data flags:
  - P7492 owner is "Sonatrach SpA", an Algerian state firm. That is almost certainly a data error. The tracker sources point to Qiandongnan government documents, so the owner is probably Guizhou Dongli Energy Investment.
  - P4992 capacity 18.03 bcm/y for a 73 km branch is implausible. It may be 18.03 million m3/day or a unit slip. P7524 at 3.67 bcm/y and P4980 at 0.01 bcm/y also look wrong.
  - P7524, P7513 and P7509 have no owner.
- Sources: all snippet-only, as listed. The tracker's gzw.guizhou.gov.cn URL for P4981 and P4982 returned 404 from here.

### P4972 Zheng'an-Weng'an-Fuquan-#45 valve chamber pipeline, P4989 47# valve chamber-Pingtang-Luodian
- Searched PipeChina Guizhou news in Chinese. Nothing found for either. Not verified. P4972 is 275 km, 3.00 bcm/y, owned by PipeChina Guizhou Pipe Network. P4989 is 110 km, owned by PipeChina Southwest Pipeline.

### Not checked
P4593, P5622, P4582, P4589, P4594 (Anhui, only a first pass at most, see above) and P4974 Yangmanshao-Tianzhu, P4983 Qianxinan Phase 2, P4984, P4985, P4986, P7509 Taipan-Jianhe, P7515 Zhenyuan-Yangmanshao. These are open. P7509 (C2021) and P7515 (C2020) are the oldest Guizhou construction rows and the most likely to be built already.

## Suggested order for a human follow-up
1. P5636: apply the commissioning finding after opening the Anhui DRC 2026-03-17 page.
2. P7526 and P4583: decide on duplicates before editing.
3. Qiandongnan group: one Dongli Energy search settles five rows.
4. P4956 and P4975: read the original NetEase item or the Bijie project monitoring list.
5. P5616, P4591, P5626: look for first-gas notices.
