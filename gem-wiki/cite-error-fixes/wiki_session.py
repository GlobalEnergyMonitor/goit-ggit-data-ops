"""Authenticated gem.wiki API session. Thin shim over ../gemwiki.py.

This used to carry its own urllib+cookiejar stack, its own keychain lookup and
its own User-Agent. It now delegates all of that to gemwiki, so this folder
inherits the single UA, the shared 5 req/sec throttle (which this stack never
had) and one credential resolver. The class is kept because batch_repair.py and
repair_orphan_refs.py are a completed project's record — repointing them at
gemwiki's own get/post would mean rewriting their response parsing.

Response shape: .call() sends formatversion=1, which is what those two scripts
parse (`data["query"]["pages"].values()`, revision text under `["*"]`).
gemwiki.get/post default to formatversion=2, where `pages` is a list and text
lives under `["content"]` — do not "simplify" this shim by dropping the
formatversion, and prefer gemwiki directly in anything new.

One deliberate behaviour change: gemwiki raises WikiError on an API `error`
response, where the old .call() returned the error dict for the caller to print.
So a failed save now raises instead of printing a non-Success result. That is
the safer default for an edit path; it is the only semantic difference.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gemwiki as gw  # noqa: E402

API = gw.API
UA = gw.USER_AGENT


class WikiSession:
    def __init__(self):
        self.s = gw.session()

    def call(self, **params):
        """POST to the API under formatversion=1. Throttled by gemwiki."""
        params.setdefault("formatversion", "1")
        return gw.post(self.s, **params)

    def login(self):
        """Log in with the shared bot password; returns the username."""
        self.s = gw.session(login=True)
        return self.userinfo()["name"]

    def userinfo(self):
        return self.call(action="query", meta="userinfo",
                         uiprop="rights|groups")["query"]["userinfo"]

    def csrf_token(self):
        return self.call(action="query", meta="tokens")["query"]["tokens"]["csrftoken"]


if __name__ == "__main__":
    s = WikiSession()
    name = s.login()
    ui = s.userinfo()
    rights = set(ui.get("rights", []))
    print(f"logged in as: {name} (id {ui['id']})")
    print(f"groups: {ui.get('groups')}")
    print(f"user-agent: {UA}")
    print(f"throttle: {gw.MAX_CALLS_PER_SECOND}/sec (shared with all gemwiki clients)")
    for r in ["edit", "writeapi"]:
        print(f"right '{r}': {'YES' if r in rights else 'MISSING'}")
