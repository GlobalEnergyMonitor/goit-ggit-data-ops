"""Shared helpers for the GEM.wiki MediaWiki API (https://www.gem.wiki/w/api.php).

This is the one client for gem.wiki in this repo: every other script here goes
through it, so the User-Agent, the 5 req/sec throttle and the credential lookup
live in exactly one place rather than per tool. Code that must fetch gem.wiki
outside the API helpers still shares the rate limit by calling throttle().

Reads are anonymous by default; pass login=True to session() for edits or
higher query limits. Credentials resolve via credentials() — see README.md in
this folder for the credential stores and the account's actual rights.
"""

import os
import subprocess
import threading
import time
from pathlib import Path

import requests

API = "https://www.gem.wiki/w/api.php"

# GEM's infra admin matches the leading token in a Cloudflare WAF rule that
# lets this traffic bypass Under Attack Mode. UAM is off again (2026-08-11),
# but keep "baird-wiki" in any User-Agent that talks to gem.wiki — it's the
# identity in GEM's firewall logs and the bypass if UAM comes back.
# This is the single UA for every gem.wiki client in the repo — the scripts in
# cite-error-fixes/ import it rather than defining their own, so the firewall
# sees one string. The admin only asked that it be identifiable (2026-08-07),
# so the old per-tool suffix is gone; the version and contact address stay as
# ordinary MediaWiki UA etiquette. Verified: the bypass rule matches on the
# "baird-wiki" token alone, so the rest is free to change.
USER_AGENT = os.environ.get(
    "GEMWIKI_USER_AGENT",
    "baird-wiki/1.0 (baird.langenbrunner@globalenergymonitor.org)",
)
ENV_PATH = Path(__file__).resolve().parent / ".env"
# Bot password (Special:BotPasswords) in the login keychain; see credentials().
KEYCHAIN_SERVICE = os.environ.get("GEMWIKI_KEYCHAIN_SERVICE",
                                  "gem.wiki-botpassword")


class WikiError(RuntimeError):
    pass


# ------------------------------------------------------------- throttling --

MAX_CALLS_PER_SECOND = 5.0
_throttle_lock = threading.Lock()
_last_call = 0.0


def _throttle():
    """Hold every API call to MAX_CALLS_PER_SECOND, process-wide.

    Locked because scan_parallel.py drives gemwiki from a thread pool: the
    sessions are per-thread but the ceiling has to be shared, or N workers
    would each get their own N calls/sec.
    """
    global _last_call
    with _throttle_lock:
        interval = 1.0 / MAX_CALLS_PER_SECOND
        wait = _last_call + interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_call = time.monotonic()


def throttle():
    """Claim one slot in the shared rate limit before a hand-rolled request.

    get()/post() already do this, so API callers never need it. It is public for
    code that must fetch gem.wiki outside the API — rendered article HTML, say —
    which the firewall rate-limits just the same. Use it and every gem.wiki
    request in the process shares one 5/sec ceiling, threads included.
    """
    _throttle()


def load_env(path=ENV_PATH):
    """Minimal .env parser (KEY=value lines, # comments)."""
    env = {}
    if not Path(path).exists():
        return env
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip("'\"")
    return env


def _keychain_credentials(service=KEYCHAIN_SERVICE):
    """(user, password) from the macOS keychain, or None if absent/unavailable.

    Never returns or logs the secret anywhere but the caller's hands.
    """
    cmd = ["security", "find-generic-password", "-s", service]
    try:
        password = subprocess.run(cmd + ["-w"], capture_output=True, text=True,
                                  check=True).stdout.strip()
        meta = subprocess.run(cmd, capture_output=True, text=True,
                              check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None  # no such entry, or not macOS
    for line in meta.splitlines():
        if '"acct"' in line:
            user = line.split("=", 1)[1].strip().strip('"')
            if user and password:
                return user, password
    return None


def credentials():
    """(username, bot password) for the wiki account — one resolver for the repo.

    gem-wiki/.env first, then the macOS keychain (service KEYCHAIN_SERVICE).

    The order is deliberate and load-bearing. Both stores hold a bot password
    from Special:BotPasswords on the same account, but with *different grants*
    (verified 2026-08-07):

        .env      "gem-wiki-api"    edit + move + move-subpages + upload + ...
        keychain  "citation-fixer"  edit only

    ".env" is a strict superset, so preferring the keychain would silently break
    move_page() and anything else beyond a plain edit. Neither grant includes
    delete, suppressredirect or bot — see README.md "Account rights".

    The two credentials should collapse into one: put the broader secret in the
    keychain (better than a dotfile) and revoke the redundant "citation-fixer"
    grant. Until then this resolver keeps the working one in front.
    """
    env = load_env()
    user, password = env.get("GEMWIKI_USERNAME"), env.get("GEMWIKI_BOT_PASSWORD")
    if user and password:
        return user, password
    creds = _keychain_credentials()
    if creds:
        return creds
    raise WikiError(
        f"no wiki credentials: GEMWIKI_USERNAME / GEMWIKI_BOT_PASSWORD not set "
        f"in {ENV_PATH} and keychain service {KEYCHAIN_SERVICE!r} not found"
    )


def session(login=False):
    """A requests.Session for the API; logs in with the bot password if asked.

    Every gem.wiki client in the repo builds its session here, so the UA,
    the throttle and the credential lookup are shared rather than per-tool.
    """
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    if login:
        user, password = credentials()
        token = get(s, action="query", meta="tokens", type="login")[
            "query"]["tokens"]["logintoken"]
        result = post(s, action="login", lgname=user, lgpassword=password,
                      lgtoken=token)["login"]
        if result.get("result") != "Success":
            raise WikiError(f"login failed: {result}")
    return s


def _check(data):
    if "error" in data:
        raise WikiError(f"{data['error'].get('code')}: {data['error'].get('info')}")
    for warning in data.get("warnings", {}).values():
        print(f"API warning: {warning}")
    return data


def get(s, **params):
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    _throttle()
    r = s.get(API, params=params, timeout=60)
    r.raise_for_status()
    return _check(r.json())


def post(s, **data):
    data.setdefault("format", "json")
    data.setdefault("formatversion", "2")
    _throttle()
    r = s.post(API, data=data, timeout=60)
    r.raise_for_status()
    return _check(r.json())


def query_all(s, result_key, **params):
    """Yield items from a list=/prop= query, following API continuation."""
    params = {"action": "query", **params}
    while True:
        data = get(s, **params)
        query = data.get("query", {})
        chunk = query.get(result_key)
        if chunk is None:  # prop=revisions nests under pages
            pages = query.get("pages", [])
            if not pages:
                return
            page = pages[0]
            if page.get("missing"):
                raise WikiError(f"page not found: {page.get('title')}")
            chunk = page.get(result_key, [])
        yield from chunk
        if "continue" not in data:
            return
        params.update(data["continue"])


# ---------------------------------------------------------------- queries --

REV_PROPS = "ids|timestamp|user|comment|size|flags|tags"


def page_revisions(s, title, limit="max", start=None, end=None):
    """Full edit history of one page, newest first."""
    return query_all(
        s, "revisions", titles=title, prop="revisions",
        rvprop=REV_PROPS, rvlimit=limit, rvstart=start, rvend=end,
    )


def user_contribs(s, user, limit="max", start=None, end=None):
    """All edits by one user across the wiki, newest first."""
    return query_all(
        s, "usercontribs", list="usercontribs", ucuser=user,
        ucprop="ids|title|timestamp|comment|size|sizediff|flags|tags",
        uclimit=limit, ucstart=start, ucend=end,
    )


def recent_changes(s, limit="max", start=None, end=None, namespace=None):
    """Site-wide recent changes (edits + new pages), newest first."""
    return query_all(
        s, "recentchanges", list="recentchanges",
        rcprop="ids|title|timestamp|user|comment|sizes|flags|tags",
        rctype="edit|new", rclimit=limit, rcstart=start, rcend=end,
        rcnamespace=namespace,
    )


def page_text(s, title):
    """Current wikitext of a page."""
    data = get(s, action="query", titles=title, prop="revisions",
               rvprop="content", rvslots="main")
    page = data["query"]["pages"][0]
    if page.get("missing"):
        raise WikiError(f"page not found: {title}")
    return page["revisions"][0]["slots"]["main"]["content"]


def search(s, text, limit=50, namespace=0):
    """Full-text search; yields dicts with title/snippet/timestamp."""
    return query_all(
        s, "search", list="search", srsearch=text,
        srlimit=limit, srnamespace=namespace,
    )


# ------------------------------------------------------------------ edits --

def csrf_token(s):
    return get(s, action="query", meta="tokens")["query"]["tokens"]["csrftoken"]


def edit_page(s, title, text=None, summary="", minor=False, bot=True,
              appendtext=None, prependtext=None):
    """Save an edit. Session must be logged in. Exactly one of text /
    appendtext / prependtext must be given."""
    if sum(x is not None for x in (text, appendtext, prependtext)) != 1:
        raise ValueError("pass exactly one of text / appendtext / prependtext")
    data = dict(action="edit", title=title, summary=summary,
                token=csrf_token(s))
    if text is not None:
        data["text"] = text
    if appendtext is not None:
        data["appendtext"] = appendtext
    if prependtext is not None:
        data["prependtext"] = prependtext
    if minor:
        data["minor"] = "1"
    if bot:
        data["bot"] = "1"
    result = post(s, **data)
    if result.get("edit", {}).get("result") != "Success":
        raise WikiError(f"edit failed: {result}")
    return result["edit"]


def move_page(s, old, new, reason="", movetalk=True, movesubpages=True,
              leave_redirect=True):
    """Rename a page. Session must be logged in.

    A redirect is left at the old title by default — drop it only when you are
    sure nothing links to the old name (`noredirect` also needs the suppressredirect
    right). Returns the API's move dict: {"from": ..., "to": ..., "reason": ...}.
    """
    data = {"action": "move", "from": old, "to": new, "reason": reason,
            "token": csrf_token(s)}
    if movetalk:
        data["movetalk"] = "1"
    if movesubpages:
        data["movesubpages"] = "1"
    if not leave_redirect:
        data["noredirect"] = "1"
    result = post(s, **data)
    if "move" not in result:
        raise WikiError(f"move failed: {result}")
    return result["move"]
