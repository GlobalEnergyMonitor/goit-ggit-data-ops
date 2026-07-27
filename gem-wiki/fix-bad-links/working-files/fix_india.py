#!/usr/bin/env python3
"""India background-citation fixes (working file, not committed)."""
import fixlib
import gemwiki as gw

WB = "https://web.archive.org/web/"
ACC = "July 22, 2026"

# giignl.org/wp-content URLs are dead (site moved to Webflow CDN)
G2023_OLD = "https://giignl.org/wp-content/uploads/2023/07/GIIGNL-2023-Annual-Report-July20.pdf"
G2024_OLD = "https://giignl.org/wp-content/uploads/2024/06/GIIGNL-2024-Annual-Report-1.pdf"
G2022_OLD = "https://giignl.org/wp-content/uploads/2022/05/GIIGNL2022_Annual_Report_May5.pdf"

g23 = ("giignl 2023 dead url -> cdn", "GIIGNL-2023-Annual-Report-July20",
       ("swap", G2023_OLD, fixlib.G2023))

fixes = {
    "Chhara LNG Terminal": ("fix background refs: giignl 2023/2024 urls; bnn bloomberg archive swap", [
        g23,
        ("giignl 2024 dead url -> cdn", "GIIGNL-2024-Annual-Report-1.pdf",
         ("swap", G2024_OLD, fixlib.G2024)),
        ("bnnbloomberg article gone -> archive", "india-prepares-to-start-new-lng",
         ("swap", "https://www.bnnbloomberg.ca/india-prepares-to-start-new-lng-import-terminal-as-demand-rises-1.2049097",
          WB + "20240320030520/https://www.bnnbloomberg.ca/india-prepares-to-start-new-lng-import-terminal-as-demand-rises-1.2049097")),
    ]),
    "Crown Kakinada LNG Terminal": ("fix background refs: gasworld + bnn bloomberg archive swaps; giignl 2022 url", [
        ("gasworld dead -> archive", "crown-lng-to-develop-lng-terminal-offshore-india",
         ("swap", "https://www.gasworld.com/crown-lng-to-develop-lng-terminal-offshore-india/2021047.article",
          WB + "20220701043644/https://www.gasworld.com/crown-lng-to-develop-lng-terminal-offshore-india/2021047.article")),
        ("giignl 2022 dead url -> cdn", "GIIGNL2022_Annual_Report_May5",
         ("swap", G2022_OLD, fixlib.G2022)),
        ("bnnbloomberg article gone -> archive", "norway-s-crown-lng-to-spend",
         ("swap", "https://www.bnnbloomberg.ca/norway-s-crown-lng-to-spend-1-billion-on-india-regas-terminal-counting-on-mounting-demand-1.2022315",
          WB + "20240116121213/https://www.bnnbloomberg.ca/norway-s-crown-lng-to-spend-1-billion-on-india-regas-terminal-counting-on-mounting-demand-1.2022315")),
    ]),
    "Dabhol LNG Terminal": ("fix background refs: giignl 2021 standardized; bit.ly to archived original; nasdaq copy to live syndicated reuters; igu 2023 archive swap", [
        ("giignl 2021 wikilink -> standard ref", "PUBLIC AREA/giignl 2021",
         ("full", fixlib.giignl(fixlib.G2021, 2021, name=":0", accessed=ACC))),
        ("bit.ly -> archived lngworldnews original", "bit.ly/2unYSdp",
         ("swap", "http://bit.ly/2unYSdp",
          WB + "20190527083429/https://www.lngworldnews.com/indias-dabhol-terminal-ups-lng-deliveries/")),
        ("dead nasdaq copy -> live shippingtribune syndication", "gail-shuts-ratnagiri",
         ("full", '<ref name=":2">{{Cite news|url=https://www.shippingtribune.com/news/shipping/'
                  'GAIL+shuts+Ratnagiri+LNG+terminal+till+end-Sept,+cuts+imports-+sources'
                  '|title=GAIL shuts Ratnagiri LNG terminal till end-Sept, cuts imports - sources'
                  '|agency=Reuters|work=The Shipping Tribune|access-date=' + ACC + '}}</ref>')),
        ("igu 2023 dead url -> archive", "lng2023-world-lng-report",
         ("swap", "https://www.igu.org/resources/lng2023-world-lng-report/",
          WB + "20250123194142/https://www.igu.org/resources/lng2023-world-lng-report/")),
    ]),
    "Dahej LNG Terminal": ("fix background refs: bit.ly to adb original; lngworldnews archive swap; giignl 2022 standardized + 2023 url", [
        ("bit.ly -> live adb original", "bit.ly/2uEgH7C",
         ("swap", "http://bit.ly/2uEgH7C",
          "https://www.adb.org/projects/documents/dahej-lng-terminal-expansion-project-xarr")),
        ("lngworldnews dead -> archive", "petronet-completes-dahej-lng-terminal-capacity-expansion",
         ("swap", "https://www.lngworldnews.com/petronet-completes-dahej-lng-terminal-capacity-expansion/",
          WB + "20190820133800/https://www.lngworldnews.com/petronet-completes-dahej-lng-terminal-capacity-expansion/")),
        ("giignl 2022 wikilink -> standard ref", "GIIGNL2022 Annual Report May5",
         ("full", fixlib.giignl(fixlib.G2022, 2022, accessed=ACC))),
        g23,
    ]),
    "Dhamra LNG Terminal": ("fix background ref: giignl 2023 url", [g23]),
    "Digha FSRU": ("fix background ref: h-energy project page archive swap", [
        ("henergy east-coast dead -> archive", "east-coast-project",
         ("swap", "http://www.henergy.com/east-coast-project/",
          WB + "20190416070620/http://www.henergy.com:80/east-coast-project/")),
    ]),
    "Ennore LNG Terminal": ("fix background ref: bit.ly to archived india infra monitor page", [
        ("bit.ly -> archived indiainframonitor", "bit.ly/2wyh84D",
         ("swap", "http://bit.ly/2wyh84D",
          WB + "20170903184517/http://indiainframonitor.com:80/projects/report/526914b997725281c497cf4c")),
    ]),
    "Gopalpur LNG Terminal": ("fix background ref: giignl 2023 url", [g23]),
    "H-Energy Kakinada LNG Terminal": ("fix background refs: kallanish + igu 2024 archive swaps; giignl 2023 url", [
        ("kallanish dead (522) -> archive", "kallanishenergy.com/2019/09/13",
         ("swap", "https://www.kallanishenergy.com/2019/09/13/indias-h-energy-to-build-lng-regas-terminal/",
          WB + "20200613070416/https://www.kallanishenergy.com/2019/09/13/indias-h-energy-to-build-lng-regas-terminal/")),
        g23,
        ("igu 2024 dead url -> archive", "2024-world-lng-report",
         ("swap", "https://www.igu.org/resources/2024-world-lng-report/",
          WB + "20250116103105/https://www.igu.org/resources/2024-world-lng-report/")),
    ]),
    "Haldia LNG Terminal": ("fix background refs: bit.ly shortlinks to archived giignl pdf and epmag article", [
        ("bit.ly -> archived giignl q-flex pdf", "bit.ly/2nxJYhG",
         ("swap", "http://bit.ly/2nxJYhG",
          WB + "20160818011142/http://giignl.org/system/files/q-flexq-max_acceptability_database_-_march_.pdf")),
        ("bit.ly -> archived epmag article", "bit.ly/2vV02kc",
         ("swap", "http://bit.ly/2vV02kc",
          WB + "20181116072957/https://www.epmag.com/article/india-lng-demand")),
    ]),
    "Hazira LNG Terminal": ("fix background refs: new indian express + shell.in archive swaps; giignl 2024 url", [
        ("newindianexpress dead -> archive", "shell-completes-acquisition-of-totals",
         ("swap", "http://www.newindianexpress.com/business/2019/jan/09/shell-completes-acquisition-of-totals-26-percent-stake-in-hazira-lng-terminal-1922760.html",
          WB + "20190203062926/http://www.newindianexpress.com/business/2019/jan/09/shell-completes-acquisition-of-totals-26-percent-stake-in-hazira-lng-terminal-1922760.html")),
        ("shell.in page drifted -> archive", "lng-terminal.html",
         ("swap", "https://www.shell.in/shellenergy/shell-energy-india/lng-terminal.html",
          WB + "20241014001313/https://www.shell.in/shellenergy/shell-energy-india/lng-terminal.html")),
        ("giignl 2024 dead url -> cdn", "GIIGNL-2024-Annual-Report-1.pdf",
         ("swap", G2024_OLD, fixlib.G2024)),
    ]),
    "Jafrabad FSRU": ("fix background refs: giignl 2021 standardized; giignl 2023 url", [
        ("giignl 2021 wikilink -> standard ref", "PUBLIC AREA/giignl 2021",
         ("full", fixlib.giignl(fixlib.G2021, 2021, accessed=ACC))),
        g23,
    ]),
    "Jaigarh LNG Terminal": ("fix background refs: h-energy pages + ngsindia archive swaps; giignl 2023 url", [
        ("henergy west-coast dead -> archive", "west-coast-project",
         ("swap", "http://www.henergy.com/west-coast-project/",
          WB + "20250829014314/https://www.henergy.com/west-coast-project/")),
        ("henergy hoegh page dead -> archive (2021 capture with content)", "h-energy-committed-fsru-contract-to-hoegh",
         ("swap", "http://www.henergy.com/media/h-energy-committed-fsru-contract-to-hoegh-2/",
          WB + "20210416033918/http://www.henergy.com/media/h-energy-committed-fsru-contract-to-hoegh-2/")),
        ("ngsindia content gone -> archive", "agp-to-invest-rs-8000-crore",
         ("swap", "https://ngsindia.org/news/agp-to-invest-rs-8000-crore-in-expanding-city-gas-network/",
          WB + "20250916042155/https://ngsindia.org/news/agp-to-invest-rs-8000-crore-in-expanding-city-gas-network/")),
        g23,
    ]),
    "Karaikal FSRU": ("fix background ref: giignl 2023 url", [g23]),
    "Kochi LNG Terminal": ("fix background ref: giignl 2021 standardized", [
        ("giignl 2021 wikilink -> standard ref", "PUBLIC AREA/giignl 2021",
         ("full", fixlib.giignl(fixlib.G2021, 2021, accessed=ACC))),
    ]),
    "Krishna Godavari FSRU": ("fix background ref: lngworldnews archive swap", [
        ("lngworldnews dead -> archive", "india-east-coast-lng-import-terminal-on-fast-track",
         ("swap", "http://www.lngworldnews.com/india-east-coast-lng-import-terminal-on-fast-track/",
          WB + "20160506102400/http://www.lngworldnews.com:80/india-east-coast-lng-import-terminal-on-fast-track/")),
    ]),
    "Kukrahati LNG Terminal": ("fix background refs: h-energy ec pdf archive swap; giignl 2023 url", [
        ("henergy ec pdf dead -> archive", "EC-KUKRAHATI-LNG-TERMINAL",
         ("swap", "http://www.henergy.com/wp-content/uploads/2019/11/EC-KUKRAHATI-LNG-TERMINAL-06.11.2019.pdf",
          WB + "20240420035548/https://www.henergy.com/wp-content/uploads/2019/11/EC-KUKRAHATI-LNG-TERMINAL-06.11.2019.pdf")),
        g23,
    ]),
    "Mundra LNG Terminal": ("fix background refs: giignl 2021 standardized; bloombergquint archive swap", [
        ("giignl 2021 dead url -> standard ref", "giignl_2021_annual_report_apr27",
         ("full", fixlib.giignl(fixlib.G2021, 2021, name=":0", accessed=ACC))),
        ("bloombergquint domain defunct -> archive", "bloombergquint",
         ("swap", "https://www.bloombergquint.com/business/2017/06/20/adani-looks-to-strengthen-group-companies-balancesheet-as-it-starts-carmichael-project",
          WB + "20181005204500/https://www.bloombergquint.com/business/2017/06/20/adani-looks-to-strengthen-group-companies-balancesheet-as-it-starts-carmichael-project")),
    ]),
}

s = gw.session()
diffs = {t: fixlib.build(s, t, fx) for t, (summ, fx) in fixes.items()}

print("\n" + "=" * 70 + "\nSAVING\n")
s = gw.session(login=True)
for t, (summ, fx) in fixes.items():
    fixlib.guarded_save(s, t, *diffs[t], summary=summ)

print("\ncite error check:")
for t in fixes:
    print(f"  {fixlib.cite_errors(s, t)}  {t}")
