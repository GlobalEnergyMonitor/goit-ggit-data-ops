# gem-wiki

Queries and edits against [GEM.wiki](https://www.gem.wiki) via the MediaWiki
API (`https://www.gem.wiki/w/api.php`). Houses any wiki work done from this
repo: edit-history digging, cite-error cleanups, batch text fixes, etc.

## Files

- `gemwiki.py` — shared helpers: API session (anonymous or bot-password
  login), continuation-aware queries (`page_revisions`, `user_contribs`,
  `recent_changes`, `page_text`, `search`), and `edit_page` for writes.
- `wiki_query.py` — read-only CLI for quick lookups:

  ```
  python wiki_query.py history "Trans Mountain Pipeline"   # who edited when
  python wiki_query.py contribs SomeUsername               # a user's edits
  python wiki_query.py recent --limit 100                  # site-wide changes
  python wiki_query.py search "cite error"
  ```

- `.env.example` → copy to `.env` (gitignored) for credentials.
- `cite-error-fixes/` — repair of orphaned `<ref name=X />` citations across
  the LNG terminal pages (411 flagged by the 2026-07-20 crawl; root cause:
  tracker-update bot passes destroying ref definitions in Project Details).
  Own README + STATUS.md there; uses its own keychain credential
  (`citation-fixer`), not this folder's `.env`. Complete — all 411 fixed.
- `fix-bad-links/` — the other half of the same problem: the LNG terminal
  pages' **Background citations**, checked link by link and repaired
  (relocate → content-validated archive → drop as redundant → re-source).
  Ongoing, country by country. `SCOPE.md` is the denominator — every country
  in the LNG update assignments sheet, swept or not; `COVERAGE.md` is what
  each batch did; `HUMAN-REVIEW.md` collects what the tooling can't settle,
  mostly claim-vs-source mismatches that need a prose decision. Its own
  README carries the workflow and the accumulated gotchas.

## Auth

Reads are anonymous — no credentials needed. Edits (and the higher `max`
query limits) need a **bot password**: log into gem.wiki with your own
account, go to `Special:BotPasswords`, create one named `gem-wiki-api` with
the grants listed in `.env.example`, and put the resulting
`<YourWikiUsername>@gem-wiki-api` username + generated password in
`gem-wiki/.env`. Edits made this way are attributed to your wiki account.

A bot password is revocable on the same page and scoped by its grants.
`gem-wiki-api` is the general-purpose key for scripted/API access from this
and other repos; the terminals-researcher bot password remains separate and
independently revocable.

## Rules

- **Never commit `.env`** (the repo-wide gitignore already excludes it).
- **Wiki edits are the user's call, per edit** — same policy as Google
  Sheets in this repo: preview exactly what would change (page, old text,
  new text, edit summary) and get explicit approval before calling
  `edit_page`. Read-only queries are always fine.
  **Standing exception (2026-07-21): `fix-bad-links/` runs autonomously** —
  per-edit approval doesn't scale to a sweep of hundreds of refs, and the
  edits are narrow (a `<ref>` span, never prose) and machine-gated (the save
  aborts if the page moved under it, and refuses to leave a cite error
  behind). It still escalates for anything needing a real browser, and
  anything unsettled goes to `HUMAN-REVIEW.md` rather than being guessed at.
- One-off analysis outputs (CSVs etc.) are gitignored like everywhere else
  in the repo; keep durable findings in a committed markdown note here if
  they're worth keeping.
