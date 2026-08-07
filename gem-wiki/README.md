# gem-wiki

Queries and edits against [GEM.wiki](https://www.gem.wiki) via the MediaWiki
API (`https://www.gem.wiki/w/api.php`). Houses any wiki work done from this
repo: edit-history digging, cite-error cleanups, batch text fixes, etc.

## Files

- `gemwiki.py` — shared helpers: API session (anonymous or bot-password
  login), continuation-aware queries (`page_revisions`, `user_contribs`,
  `recent_changes`, `page_text`, `search`), and `edit_page` / `move_page`
  for writes. `move_page` leaves a redirect at the old title by default.
  Every call is throttled to `MAX_CALLS_PER_SECOND` (5/s) by a locked
  module-level gate in `get`/`post`, so the ceiling is process-wide and
  holds even under `scan_parallel.py`'s thread pool. Lower the constant for
  long write runs — 5/s is a read pace.
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

### Cloudflare managed challenge (blocking all scripted access as of 2026-08-07)

Every gem.wiki path — `/w/api.php`, article HTML, even `/robots.txt` — returns
**HTTP 403 with `cf-mitigated: challenge`** and a "Just a moment…" Turnstile page.
It is **not** an auth problem: it fires before MediaWiki sees the request, so no
bot password helps. Diagnostics, so nobody re-runs them:

- A full browser header set (UA, `Sec-CH-UA`, `Sec-Fetch-*`, …) still 403s — the
  challenge fingerprints the **TLS handshake** and requires JS, so header spoofing
  cannot work, and neither can `requests`/`urllib`/`curl`.
- A fresh browser-minted `cf_clearance` cookie **also** 403s from `curl`, so on this
  zone the cookie is bound to the TLS fingerprint as well as IP + User-Agent. Carrying
  the cookie into a normal HTTP client is a dead end.
- Anthropic's WebFetch (different IPs) is blocked too → zone-wide setting, not IP
  reputation. `globalenergymonitor.org` is unaffected → gem.wiki's zone specifically.
- It is new: `fix-bad-links/` was saving edits through this same tooling on 2026-07-28.

**The fix is a Cloudflare config change on the gem.wiki zone**, most likely Bot Fight
Mode (or a "block AI bots" toggle) having been switched on — those break every
non-browser client, MediaWiki API bots included. Cleanest repair is a WAF **Skip**
custom rule scoped to the API rather than opening the whole site, e.g.
`http.request.uri.path eq "/w/api.php" and http.request.headers["x-gem-api-key"][0] eq "<secret>"`
→ *Skip → all remaining custom rules + Bot Fight Mode*. Until that lands, wiki writes
have to be done by hand in a browser.

A bot password is revocable on the same page and scoped by its grants.
`gem-wiki-api` is the general-purpose key for scripted/API access from this
and other repos; the terminals-researcher bot password remains separate and
independently revocable.

## Rules

- **Never commit `.env`** (the repo-wide gitignore already excludes it).
- **Wiki edits are the user's call, per edit** — same policy as Google
  Sheets in this repo: preview exactly what would change (page, old text,
  new text, edit summary) and get explicit approval before calling
  `edit_page` or `move_page` (for a move: page, old title, new title,
  summary). Read-only queries are always fine.
  **Standing exception (2026-07-21): `fix-bad-links/` runs autonomously** —
  per-edit approval doesn't scale to a sweep of hundreds of refs, and the
  edits are narrow (a `<ref>` span, never prose) and machine-gated (the save
  aborts if the page moved under it, and refuses to leave a cite error
  behind). It still escalates for anything needing a real browser, and
  anything unsettled goes to `HUMAN-REVIEW.md` rather than being guessed at.
- One-off analysis outputs (CSVs etc.) are gitignored like everywhere else
  in the repo; keep durable findings in a committed markdown note here if
  they're worth keeping.
