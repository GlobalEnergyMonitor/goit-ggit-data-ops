"""Guarded-save the Italy / Spain / Germany Background-ref repairs.

  python3 save_isg.py italy spain germany

Each fix_<country>.py pickles only {title: (old, new)}, so the edit summaries
are re-imported from the module rather than read back out of the pickle.
"""
import importlib
import pickle
import sys

sys.path[:0] = [".", "../.."]
import fixlib  # noqa: E402
import gemwiki as gw  # noqa: E402


def main(countries):
    s = gw.session(login=True)
    bad = 0
    for country in countries:
        mod = importlib.import_module(f"fix_{country}")
        diffs = pickle.load(open(f"diffs_{country}.pkl", "rb"))
        print(f"\n{'=' * 70}\n{country.upper()}  ({len(diffs)} pages)\n{'=' * 70}")
        saved = {}
        for t, (summ, _fx) in mod.fixes.items():
            old, new = diffs[t]
            saved[t] = fixlib.guarded_save(s, t, old, new, summary=summ)
        print(f"--- {country}: cite errors (must be 0)")
        for t in mod.fixes:
            if saved[t] is None:
                print(f"  ABORTED  {t}")
                bad += 1
                continue
            n = fixlib.cite_errors(s, t)
            print(f"  {n:2d}  {t}")
            if n:
                bad += 1
    print("\nALL CLEAN" if not bad else f"\n{bad} PAGES NEED ATTENTION")


if __name__ == "__main__":
    main(sys.argv[1:])
