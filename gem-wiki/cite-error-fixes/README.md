# cite-error-fixes

Repairing orphaned `<ref name=X />` citations across GEM.wiki LNG terminal
pages. A 2026-07-20 crawl of all 842 unique wiki pages linked from the GGIT
LNG terminals database found **411 pages with MediaWiki cite errors**
("Invalid `<ref>` tag; no text was provided for refs named X").

**Root cause:** tracker-update bot passes (the 2025-10-16 "Data Team" pass
primarily; March/July 2026 passes show the same pattern) regenerate the
Project Details section from the tracker DB, destroying the full
`<ref name=X>…</ref>` definitions that lived there while the Background
prose keeps the `<ref name=X />` reuses — now orphaned.

**Fix:** recover each definition from page history and splice it into the
first self-closing use in the current text (the definition then lives in the
prose, so a future regeneration of Project Details can't re-break it).
Since 2026-07-20 (user-approved recipe extension), an empty definition
`<ref name=X></ref>` — a rarer husk the same bot pass leaves behind — is
treated as an orphaned use and repaired the same way; a donor must have a
non-empty body.

Progress + what's left: **[STATUS.md](STATUS.md)**. The narrative record of
the crawl and the supervised pilot lives in the lng-terminals-researcher
repo, `batches/run_records/2026-07-20_wiki-cite-error-crawl.md`.

## Files

- `crawl_cite_errors.py` — audit crawler. Reads a GEM LNG export CSV (from
  the lng-terminals-researcher repo: `gem_query.py --all-fields lng`),
  fetches every unique `wiki` URL, flags rendered `mw-ext-cite-error` spans.
  `python crawl_cite_errors.py <export.csv> cite_error_results.json`
- `wiki_session.py` — authenticated API session (see Auth below).
- `repair_orphan_refs.py` — single-page repair, dry-run by default:
  `python repair_orphan_refs.py "<Page Title>"` writes before/after/diff
  artifacts and a render preview; `--save` submits only after the preview
  shows 0 cite errors. Review the diff before saving.
- `batch_repair.py` — batch driver over the flagged list:
  `python batch_repair.py 50 batch50d_log.csv`. Skips everything already in
  a `batch*_log.csv` or the hardcoded pilot list; per-page gates (donor
  found, prose anchor match, insertions-only splice, 0-error preview);
  5s throttle; re-verifies the live page after each save.
- `cite_error_results.json` / `batch*_log.csv` — crawl results and per-batch
  audit logs (gitignored like all data files in this repo, but they are the
  batch driver's done-list state — keep them in this folder locally).
- `artifacts/` — before/after/diff wikitext from the supervised pilot runs
  (gitignored; regenerable by re-running dry-runs).

## Safety gates (why batch mode is OK here)

Every page must pass, or it's skipped to the manual queue:

1. Donor revision found in history for every orphaned name.
2. The 60 chars of prose before each current use appear in the donor
   revision (exact, or whitespace-normalized — bot passes reflow blank
   lines). A real prose change → `ANCHOR_MISMATCH` → manual queue.
3. The splice is insertions-only by construction (spans computed on the
   original text).
4. `action=parse` preview of the repaired text must render **0** cite errors.
5. Save uses `nocreate` + `basetimestamp`/`starttimestamp` (edit-conflict
   protection) + `maxlag=5`; the live page is re-parsed and must show 0
   errors.

The user approved this workflow batch-wise (50 pages per approval,
2026-07-20) — an agreed exception to the repo's default per-edit approval
rule for wiki writes, scoped to this repair recipe only.

## Auth

`wiki_session.py` reads the **`citation-fixer`** bot password from the macOS
keychain (`security find-generic-password -s gem.wiki-botpassword`; the
account field holds the login name, `-w` prints the secret). This is
deliberately separate from the general-purpose `gem-wiki-api` credential in
`../.env` (see `../README.md`) and independently revocable at
`Special:BotPasswords`. Never print or commit the token.

Edit summary used on every save:
`restore orphaned ref definitions lost in the 2025-10-16 tracker update (fix cite errors)`
