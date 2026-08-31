# gem-wiki

Queries and edits against [GEM.wiki](https://www.gem.wiki) via the MediaWiki
API (`https://www.gem.wiki/w/api.php`). Houses any wiki work done from this
repo: edit-history digging, cite-error cleanups, batch text fixes, etc.

## Files

- `gemwiki.py` — **the** client for gem.wiki; everything else in this folder
  goes through it, so the User-Agent, the rate limit and the credential lookup
  exist once rather than per tool. Provides the API session (anonymous or
  bot-password login), continuation-aware queries (`page_revisions`,
  `user_contribs`, `recent_changes`, `page_text`, `search`), and `edit_page` /
  `move_page` for writes. `move_page` leaves a redirect at the old title by
  default.

  Every call is throttled to `MAX_CALLS_PER_SECOND` (5/s) by a locked
  module-level gate in `get`/`post`, so the ceiling is process-wide and holds
  even under `scan_parallel.py`'s thread pool. Lower the constant for long
  write runs — 5/s is a read pace. Code that fetches gem.wiki *outside* the API
  helpers (rendered article HTML, say) must call `gemwiki.throttle()` to claim a
  slot in the same ceiling; `cite-error-fixes/crawl_cite_errors.py` is the
  example. Anything new that talks to gem.wiki belongs on this module — do not
  hand-roll a second session, UA or credential path.
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
  Own README + STATUS.md there. Complete — all 411 fixed. Its
  `wiki_session.py` is now a thin shim over `gemwiki.py` (it used to carry its
  own urllib stack, UA and keychain lookup); it keeps `formatversion=1` because
  that is what its two scripts parse.
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

`gemwiki.credentials()` is the single resolver for the whole folder: it reads
`gem-wiki/.env` first, then falls back to a macOS keychain entry (service
`gem.wiki-botpassword`, overridable with `$GEMWIKI_KEYCHAIN_SERVICE`).

**The order matters.** Two bot passwords exist on the account and their grants
differ — verified 2026-08-07:

| store | bot password | grants |
|---|---|---|
| `.env` | `gem-wiki-api` | `edit`, `move`, `move-subpages`, `upload`, `createpage`, … |
| keychain | `citation-fixer` | `edit` only |

`gem-wiki-api` is a strict superset, so `.env` is tried first — preferring the
keychain silently breaks `move_page()` and anything past a plain edit. Neither
grant includes `delete`, `suppressredirect` or `bot` (see "Account rights").

**Still to collapse:** `citation-fixer` is now redundant — nothing needs an
edit-only credential once `cite-error-fixes/` shares this resolver. The tidy end
state is one bot password, stored in the keychain rather than a dotfile, with
`citation-fixer` revoked at `Special:BotPasswords`. Both steps are manual and
outward-facing, so they are deliberately not automated here. GEM's infra admin
separately flagged (2026-08-07) that bot passwords are hard to audit
wiki-side, which is another reason to keep exactly one.

### Cloudflare (2026-08-07 incident is over; the UA token stays)

**Current state (verified 2026-08-11): Under Attack Mode is off.** The API,
rendered article HTML and `/robots.txt` all return 200 with no `cf-mitigated`
header under arbitrary UAs — including `python-requests/…`, which was the
canonical 403 while UAM was on. Whether the admin also removed the
`baird-wiki` WAF bypass rule isn't observable from outside; treat it as
possibly still live and possibly needed again.

**History:** gem.wiki was taken down by a traffic flood in early August 2026
and GEM's infra admin switched the zone to Under Attack Mode (2026-08-07),
which JS-challenges every visitor — all scripted access 403'd with
`cf-mitigated: challenge` before MediaWiki saw the request, regardless of
headers, library (`mwclient` 403'd identically) or a browser-minted
`cf_clearance` cookie, because the challenge fingerprints the TLS handshake.
The fix agreed with the admin was a WAF rule letting UAs carrying the
**`baird-wiki`** token bypass UAM, paired with client-side rate limiting
(~5 req/sec, his number). The rule matched on the bare token, zone-wide, and
was verified live 2026-08-07; UAM was off again by 2026-08-11. The full
diagnostics and bypass verification are in git history (`5621479`, `c3d6349`)
if it ever comes back.

**What stays load-bearing with UAM off:**

- **Keep `baird-wiki` as the leading UA token.** It is the identity GEM's
  admin knows in the firewall logs, and the bypass if UAM returns — if
  scripted access starts 403ing again, check the UA first. The token
  deliberately avoids the word "bot" (Cloudflare scores those more
  suspiciously, and these are attributed, human-supervised edits) and names
  the person so any firewall rule keyed on it stays self-auditing. The
  version and contact address around the token are ordinary MediaWiki
  etiquette, free to change.
- **Keep the 5 req/sec throttle** (`MAX_CALLS_PER_SECOND` in `gemwiki.py`).
  The admin asked for it as part of the arrangement, not as a UAM-era
  measure. Non-API fetches of gem.wiki (rendered HTML scrapes) must still
  call `gemwiki.throttle()` — they spend the same allowance.
- There is exactly **one** UA for the whole repo — `USER_AGENT` in
  `gemwiki.py` (overridable via `$GEMWIKI_USER_AGENT`), which the
  `cite-error-fixes/` scripts import rather than defining their own.
  Per-tool suffixes were dropped 2026-08-07: the admin needs the traffic
  identifiable, not split by tool. Scripts that fetch **external** sites
  (`fix-bad-links/working-files/`) use their own UAs and must not carry this
  token.
- **A second repo shares this exact string.** `pipelines-researcher` fetches
  gem.wiki in `scripts/harvest_wiki_citations.py` and
  `scripts/wiki_alignment.py`, and its `url_verifier.WIKI_UA` is
  byte-identical to `USER_AGENT` here — deliberate (2026-08-10) so both repos
  appear as a single client in GEM's firewall logs. **If you change the
  string here, change it there too.** Its `CLAUDE.md` carries the same
  warning in the other direction. The two repos also share the one
  rate-limit allowance, so don't run wiki passes in both at once.

### Account rights (what the bot password can and can't do)

The bot password inherits the *account's* rights, and the account is in `user` +
`autoconfirmed` only — so `move` and `move-subpages` yes, but **`suppressredirect`,
`delete` and `bot` no**. Consequences worth knowing before planning a run:

- Every move **leaves a redirect** at the old title; `leave_redirect=False` would be
  rejected. Without `delete` the stub can't be cleaned up afterwards either.
- `edit_page` sends `bot=1`, but MediaWiki ignores it without the right, so bulk
  passes show up unflagged in Recent Changes.

Check current rights with `action=query&meta=userinfo&uiprop=groups|rights` rather than
assuming — they are granted per account by the wiki admins.

**API gotcha:** never pass `redirects=0` to `action=query`. MediaWiki treats the mere
*presence* of the parameter as true, so it silently resolves redirects and dedupes the
old titles out of the response — which looks exactly like "the page doesn't exist".
Omit the parameter entirely to inspect redirect stubs.

A bot password is revocable at `Special:BotPasswords` and scoped by its grants.
`gem-wiki-api` is the general-purpose key for scripted/API access from this and other
repos, and is the one this folder now uses everywhere. `citation-fixer` still exists,
edit-only and redundant — see "Auth" for the plan to retire it.

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
