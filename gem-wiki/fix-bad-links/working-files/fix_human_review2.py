#!/usr/bin/env python3
"""Human-review round 2 (2026-07-23): apply the user-approved Section 2
replacement proposals from HUMAN-REVIEW.md. Two pages need a ref *inserted*
mid-paragraph (ref splits), so this uses a custom op list per page instead of
fixlib.build's two actions; build/save semantics are otherwise identical."""
import re
import sys

import fixlib
import gemwiki as gw

HALDIA_NEW = (
    "<ref>[https://indiaseatradenews.com/smp-kolkata-awards-30-year-licence-"
    "for-floating-lng-terminal-at-haldia/ SMP Kolkata awards 30-year licence "
    "for floating LNG terminal at Haldia], India Seatrade News, "
    "September 8, 2025</ref>")

GATE_NEW = (
    "<ref>[https://www.offshore-technology.com/projects/gate-lng-terminal/ "
    "Gate LNG Terminal], Offshore Technology, Dec. 14, 2011</ref>")

TERNEUZEN_GASUNIE = (
    "<ref>[https://www.gasunie.nl/en/news/gasunie-investigates-options-for-"
    "increasing-lng-imports-in-the-netherlands Gasunie investigates options "
    "for increasing LNG imports in the Netherlands], Gasunie, "
    "December 12, 2022</ref>")
TERNEUZEN_EURONEWS = (
    "<ref>[https://www.euronews.com/next/2022/12/09/netherlands-gas-storage "
    "Netherlands to spend up to $548 million to fill gas storage for next "
    "winter], Euronews (citing Reuters), December 9, 2022</ref>")

REVITHOUSSA_DEPA = (
    "<ref>[https://web.archive.org/web/20110721080341/http://www.depa.gr/"
    "files/downloadables/brochures/AnnualReport2006.pdf DEPA Annual Report "
    "2006 (PDF), p. 16], DEPA S.A., 2007 (Wayback Machine capture)</ref>")
REVITHOUSSA_DESFA = (
    "<ref>[https://web.archive.org/web/20180416151130/http://www.desfa.gr/"
    "en/company/historical-background Historical Background], DESFA S.A., "
    "April 16, 2018 (Wayback Machine capture)</ref>")

KUTUBDIA_NEW = (
    "<ref>[https://www.petronetlng.in/documents/699827/734537/"
    "Annual_Report__2017-18.pdf/475bb8fc-690e-f1f0-e537-fbe7a12f1ac5"
    "?t=1720013769072 Annual Report 2017-18], Petronet LNG Limited, "
    "August 18, 2018.</ref>")

QATAR_ENERDATA = (
    "<ref>[https://www.enerdata.net/publications/daily-energy-news/rasgas-"
    "qatar-agrees-cut-price-lng-sold-petronet-india.html Rasgas (Qatar) "
    "agrees to cut price of LNG sold to Petronet (India)], Enerdata, "
    "January 4, 2016</ref>")
QATAR_GULFNEWS = (
    "<ref>[https://gulfnews.com/business/energy/qatargas-agrees-to-double-"
    "lng-supplies-to-poland-1.1993823 Qatargas agrees to double LNG supplies "
    "to Poland], Gulf News (Reuters), March 14, 2017</ref>")
QATAR_FACTBOX = (
    '<ref name="Reuters">[https://web.archive.org/web/20180104172916/'
    "http://www.qatargas.com/english/aboutus/corporate-structure Corporate "
    "Structure], Qatargas (via Wayback Machine, archived January 4, "
    "2018).</ref>")

# ops: ("ref", marker, new_ref_text)      replace the unique non-autoref ref
#      ("insert", anchor, ref_text)       insert ref_text right after anchor
fixes = {
    "Haldia FSRU": ("replace dead therisk.global ref with india seatrade news", [
        ("ref", "therisk.global", HALDIA_NEW),
    ]),
    "Gate LNG Terminal": ("replace dead techint case-study pdf with offshore technology", [
        ("ref", "techint-ingenieria", GATE_NEW),
    ]),
    "Terneuzen FSRU": ("replace dead nasdaq ref; split into gasunie + euronews sources", [
        ("insert", "another possible floating LNG terminal site.",
         TERNEUZEN_GASUNIE),
        ("ref", "nasdaq.com/articles/dutch-grid-operator", TERNEUZEN_EURONEWS),
    ]),
    "Revithoussa LNG Terminal": ("replace dead desfa ref with archived depa + desfa sources", [
        ("ref", "desfa.gr/?p=11022", REVITHOUSSA_DEPA + REVITHOUSSA_DESFA),
    ]),
    "Kutubdia LNG Terminal (Petronet)": ("replace dead petrobangla pdf with petronet lng annual report", [
        ("ref", "1263_upload_0.pdf", KUTUBDIA_NEW),
    ]),
    "QatarEnergy LNG (N)": ("replace dead hellenic + uk.reuters refs with live/archived sources", [
        ("insert", "renegotiated price cuts with RasGas.", QATAR_ENERDATA),
        ("ref", "hellenicshippingnews.com/the-five-stages", QATAR_GULFNEWS),
        ("ref", "uk.reuters.com/article/gulf-qatar-energy", QATAR_FACTBOX),
    ]),
    "QatarEnergy LNG (S)": ("replace dead uk.reuters factbox with archived qatargas structure page", [
        ("ref", "uk.reuters.com/article/gulf-qatar-energy", QATAR_FACTBOX),
    ]),
}


def build(s, title, ops):
    slug = re.sub(r"[ \-()]", "_", title).replace("__", "_").strip("_")
    old = gw.page_text(s, title)
    new = old
    print("=" * 70)
    print(f"PAGE: {title}  ({len(ops)} ops)")
    for kind, needle, payload in ops:
        if kind == "ref":
            ref = fixlib.find_ref(new, needle)
            if new.count(ref) != 1:
                raise SystemExit(f"ref text not unique: {needle!r}")
            new = new.replace(ref, payload, 1)
            print(f"\n--- replace ref @ {needle!r}\n  OLD: {ref[:400]}\n  NEW: {payload[:400]}")
        elif kind == "insert":
            if new.count(needle) != 1:
                raise SystemExit(
                    f"insert anchor not unique ({new.count(needle)}): {needle!r}")
            new = new.replace(needle, needle + payload, 1)
            print(f"\n--- insert after {needle!r}\n  NEW: {payload[:400]}")
        else:
            raise SystemExit(f"unknown op {kind!r}")
    with open(f"{slug}_old.wiki", "w") as f:
        f.write(old)
    with open(f"{slug}_new.wiki", "w") as f:
        f.write(new)
    print()
    return old, new


if __name__ == "__main__":
    save = "--save" in sys.argv
    s = gw.session()
    diffs = {t: build(s, t, ops) for t, (summ, ops) in fixes.items()}
    if not save:
        print("dry run only; rerun with --save to write to the wiki")
        sys.exit(0)
    s = gw.session(login=True)
    for t, (summ, ops) in fixes.items():
        fixlib.guarded_save(s, t, *diffs[t], summary=summ)
    s = gw.session()
    for t in fixes:
        print(f"cite errors {t}: {fixlib.cite_errors(s, t)}")
