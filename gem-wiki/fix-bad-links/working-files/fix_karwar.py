#!/usr/bin/env python3
"""Karwar FSRU: replace dead pipelineme ref with the LinkedIn syndicated copy
(reviewer-supplied 2026-07-23) and add shelved-2019 to the closing sentence
(reviewer-stated years: last update 2017 -> shelved 2019, cancelled 2021).

The LinkedIn piece mirrors the original exactly (US$563m in body, US$565m in
headline — same mismatch as the dead pipelineme citation), so the sentence's
$563M figure stands.
"""
import fixlib
import gemwiki as gw

TITLE = "Karwar FSRU"
SUMMARY = ("replace dead pipelineme citation with linkedin copy of the same "
           "article; note shelved year")

LINKEDIN = ("https://www.linkedin.com/pulse/"
            "hyundai-heavy-industries-awarded-us565m-contract-largest-williams")
NEW_REF = ('<ref>[' + LINKEDIN + ' "Hyundai Heavy Industries awarded US$565m '
           'contract for largest FSRU in Asia,"] Paul Williams via LinkedIn, '
           "January 10, 2017</ref>")

OLD_SENT = ("There have been no development updates in over four years, and "
            "the project is presumed to be cancelled as of 2021.")
NEW_SENT = ("There have been no development updates since; the project is "
            "presumed to have been shelved as of 2019 and cancelled as of "
            "2021.")

s = gw.session()
old = gw.page_text(s, TITLE)

ref = fixlib.find_ref(old, "pipelineme")
assert old.count(ref) == 1
assert old.count(OLD_SENT) == 1, "closing sentence changed on live page"
new = old.replace(ref, NEW_REF, 1).replace(OLD_SENT, NEW_SENT, 1)

print("OLD REF:", ref)
print("NEW REF:", NEW_REF)
print("OLD SENT:", OLD_SENT)
print("NEW SENT:", NEW_SENT)

with open("Karwar_FSRU_old.wiki", "w") as f:
    f.write(old)
with open("Karwar_FSRU_new.wiki", "w") as f:
    f.write(new)

s = gw.session(login=True)
fixlib.guarded_save(s, TITLE, old, new, summary=SUMMARY)

s = gw.session()
print("cite errors:", fixlib.cite_errors(s, TITLE))
