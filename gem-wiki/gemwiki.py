"""Shared helpers for the GEM.wiki MediaWiki API (https://www.gem.wiki/w/api.php).

Reads are anonymous by default; pass login=True to session() for edits or
higher query limits. Credentials come from gem-wiki/.env (bot password from
Special:BotPasswords) — see README.md in this folder.
"""

from pathlib import Path

import requests

API = "https://www.gem.wiki/w/api.php"
USER_AGENT = (
    "goit-ggit-data-ops/gem-wiki "
    "(baird.langenbrunner@globalenergymonitor.org)"
)
ENV_PATH = Path(__file__).resolve().parent / ".env"


class WikiError(RuntimeError):
    pass


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


def session(login=False):
    """A requests.Session for the API; logs in with the bot password if asked."""
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    if login:
        env = load_env()
        user = env.get("GEMWIKI_USERNAME")
        password = env.get("GEMWIKI_BOT_PASSWORD")
        if not (user and password):
            raise WikiError(
                f"GEMWIKI_USERNAME / GEMWIKI_BOT_PASSWORD not set in {ENV_PATH}"
            )
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
    r = s.get(API, params=params, timeout=60)
    r.raise_for_status()
    return _check(r.json())


def post(s, **data):
    data.setdefault("format", "json")
    data.setdefault("formatversion", "2")
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
