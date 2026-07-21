"""Authenticated gem.wiki API session using the keychain bot password. Token never printed."""
import http.cookiejar
import json
import subprocess
import urllib.parse
import urllib.request

API = "https://www.gem.wiki/w/api.php"
UA = "GEM-LNG-citation-fixer/1.0 (baird.langenbrunner@globalenergymonitor.org)"


def _keychain_secret():
    return subprocess.run(
        ["security", "find-generic-password", "-s", "gem.wiki-botpassword", "-w"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def _keychain_account():
    out = subprocess.run(
        ["security", "find-generic-password", "-s", "gem.wiki-botpassword"],
        capture_output=True, text=True, check=True,
    ).stdout
    for line in out.splitlines():
        if '"acct"' in line:
            return line.split("=", 1)[1].strip().strip('"')
    raise RuntimeError("no acct field in keychain entry")


class WikiSession:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def call(self, **params):
        params.setdefault("format", "json")
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(API, data=data, headers={"User-Agent": UA})
        with self.opener.open(req, timeout=60) as r:
            return json.load(r)

    def login(self):
        user = _keychain_account()
        pw = _keychain_secret()
        tok = self.call(action="query", meta="tokens", type="login")
        lgtoken = tok["query"]["tokens"]["logintoken"]
        res = self.call(action="login", lgname=user, lgpassword=pw, lgtoken=lgtoken)
        status = res.get("login", {}).get("result")
        if status != "Success":
            raise RuntimeError(f"login failed: {status} ({res.get('login', {}).get('reason', '')})")
        return res["login"]["lgusername"]

    def userinfo(self):
        return self.call(action="query", meta="userinfo", uiprop="rights|groups")[
            "query"]["userinfo"]

    def csrf_token(self):
        return self.call(action="query", meta="tokens")["query"]["tokens"]["csrftoken"]


if __name__ == "__main__":
    s = WikiSession()
    name = s.login()
    ui = s.userinfo()
    rights = set(ui.get("rights", []))
    print(f"logged in as: {name} (id {ui['id']})")
    print(f"groups: {ui.get('groups')}")
    need = ["edit", "writeapi"]
    for r in need:
        print(f"right '{r}': {'YES' if r in rights else 'MISSING'}")
    print(f"createpage right (should be irrelevant, we use nocreate): {'yes' if 'createpage' in rights else 'no'}")
