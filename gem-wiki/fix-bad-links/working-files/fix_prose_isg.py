#!/usr/bin/env python3
"""The one-way prose corrections from the Italy/Spain/Germany sweep.

"One-way" = the cited sources agree with each other and disagree with the
sentence, so there is exactly one direction the fix can go. Everything where
the sentence might be right and the source merely silent stayed in
HUMAN-REVIEW.md.

Two of the four in that class were already fixed by hand before this ran --
Gioia Tauro's EUR 6.8m -> 6.9m (rev 1206809) and Tenerife's November ->
December 2014 (rev 1206810) -- leaving these:

Priolo Augusta. The page says Shell announced its withdrawal in December
2012, but its own citation, Milano Finanza's "Priolo, anche Shell abbandona
il rigassificatore", is dated 6 Nov. 2012. December is not merely unsupported,
it postdates the source reporting the event; ERG's exit the previous July
brackets it from the other side. Only the month moves -- the refs are fine.

Lubmin. The page compresses a two-step arrival into one. Both live sources
agree Neptune reached Mukran on 23 Nov 2022 and only got to Lubmin itself on
16 Dec 2022; the port at Lubmin is too shallow to take the vessel directly,
which is *why* it sat at Mukran. The existing AP/Irish Examiner ref is kept
and stays with the November leg -- it says "arrived off the Baltic Sea port of
Mukran" and "due to begin operation in nearby Lubmin on December 1", so it
supports Mukran and never claimed the vessel was at Lubmin. The December leg
gets two new refs. Checked before writing: ref name=":1" is defined once and
reused nowhere, maritime-executive is not otherwise cited on the page, and the
existing offshore-energy.biz ref points at a different article.
"""
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402

ME = ("https://maritime-executive.com/article/"
      "fsru-arrives-in-germany-port-of-lubmin-to-start-lng-imports")
OE = ("https://www.offshore-energy.biz/"
      "lubmin-lng-terminal-receives-fsru-as-operator-expects-start-up-"
      "by-the-end-of-month/")

LUBMIN_OLD = (
    "In November 2022, TotalEnergies' Neptune FSRU arrived at the terminal "
    "site.")
LUBMIN_NEW = (
    "In November 2022, TotalEnergies' Neptune FSRU arrived at the nearby port "
    "of Mukran, where it was prepared for the final transfer to Lubmin, whose "
    "industrial port is restricted in size and depth.")
LUBMIN_ADD = (
    " The vessel was moved into position at the Lubmin terminal site on "
    "December 16, 2022.<ref>[" + ME + " FSRU Arrives in Germany's Port of "
    "Lubmin to Start LNG Imports], ''The Maritime Executive'', "
    "16 Dec. 2022.</ref><ref>[" + OE + " Lubmin LNG terminal receives FSRU as "
    "operator expects start-up by the end of month], ''Offshore Energy'', "
    "19 Dec. 2022.</ref>")

REF1 = '<ref name=":1">'

fixes = {
    "Priolo Augusta LNG Terminal": (
        "background: shell's withdrawal was announced in november 2012, not "
        "december -- the cited milano finanza piece reporting it is dated "
        "6 nov. 2012", [
            ("december -> november 2012 (source predates the claimed month)",
             "In December 2012, Shell announced",
             "In November 2012, Shell announced"),
        ]),
    "Lubmin FSRU": (
        "background: neptune reached mukran in november 2022 and lubmin "
        "itself on 16 dec 2022 -- both cited sources say so; split the "
        "one-step arrival in two", [
            ("november leg is mukran, not the terminal site",
             LUBMIN_OLD, LUBMIN_NEW),
        ]),
}

# The December sentence is appended after the existing ref rather than being
# part of the swap above, so the two edits stay independently checkable.
EXTRA = ("Lubmin FSRU", "add the 16 dec 2022 lubmin arrival + its two refs")


def lubmin_append(old, new):
    i = new.find(REF1)
    j = new.find("</ref>", i) + len("</ref>")
    if i < 0 or j <= i or new.count(REF1) != 1:
        raise SystemExit("lubmin: ref :1 not found exactly once")
    out = new[:j] + LUBMIN_ADD + new[j:]
    print(f"--- {EXTRA[1]}\n  AFTER: {new[i:j][:120]}...\n  ADD: {LUBMIN_ADD}")
    return old, out


if __name__ == "__main__":
    s = gw.session()
    diffs = {t: fixlib.build_prose(s, t, fx) for t, (summ, fx) in fixes.items()}
    diffs["Lubmin FSRU"] = lubmin_append(*diffs["Lubmin FSRU"])
    import pickle
    pickle.dump(diffs, open("diffs_prose_isg.pkl", "wb"))
    print("\n\nALL DIFFS BUILT OK ->", len(diffs), "pages")
