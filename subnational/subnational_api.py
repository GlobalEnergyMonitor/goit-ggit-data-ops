"""Client for GEM's subnational lookup microservice.

Credentials come from the macOS keychain (never printed) — see README.md for
the one-time `security add-generic-password` call. The keychain item stores the
app URL in its account field and the API key as the secret, so one lookup gets
both.

Two endpoints, both batched:

    lookup(points)  coordinates -> the GEM subnational code they fall in
    check(points)   (code, coordinates) -> does the point sit inside that code

Both take an iterable of dicts and return one result dict per input point, in
order, with any `id` echoed back. Unmatched points come back with
`{"error": "not found"}` rather than raising.
"""
import json
import subprocess
import time
import urllib.error
import urllib.request

KEYCHAIN_SERVICE = "gem-subnational-api"
CHUNK_SIZE = 500
MAX_RETRIES = 4


def _keychain(service=KEYCHAIN_SERVICE):
    """Return (app_url, api_key) from the keychain item's account + secret."""
    out = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-g"],
        capture_output=True, text=True, check=True,
    )
    account = None
    for line in out.stdout.splitlines():
        if line.strip().startswith('"acct"'):
            account = line.split("=", 1)[1].strip().strip('"')
    key = None
    for line in out.stderr.splitlines():          # -g prints the secret on stderr
        if line.startswith("password:"):
            key = line.split(":", 1)[1].strip().strip('"')
    if not account or not key:
        raise RuntimeError(
            f"keychain item '{service}' is missing an account (app URL) or password "
            "(API key) — see subnational/README.md"
        )
    return account.rstrip("/"), key


def _post(path, payload, base_url=None, api_key=None):
    if base_url is None or api_key is None:
        base_url, api_key = _keychain()
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-API-Key": api_key},
        method="POST",
    )
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            # 429/5xx are worth retrying; a 4xx is a bad request, surface it.
            if e.code not in (429, 500, 502, 503, 504) or attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"{e.code} from {path}: {e.read()[:500].decode()}") from e
        except urllib.error.URLError:
            if attempt == MAX_RETRIES - 1:
                raise
        time.sleep(2 ** attempt)


def _batched(points, path, required):
    points = [dict(p) for p in points]
    for i, p in enumerate(points):
        missing = required - p.keys()
        if missing:
            raise ValueError(f"point {i} is missing {sorted(missing)}: {p}")
    results = []
    for start in range(0, len(points), CHUNK_SIZE):
        chunk = points[start:start + CHUNK_SIZE]
        out = _post(path, chunk)
        if len(out) != len(chunk):
            raise RuntimeError(
                f"service returned {len(out)} results for {len(chunk)} points — "
                "the response is positional, so this would misalign the join"
            )
        results.extend(out)
    return results


def lookup(points):
    """Coordinates -> subnational code. Each point: {lat, long, id (optional)}.

    Points inside a boundary come back with `contains_coordinates: true`. Points
    within 1 km of one get the nearest boundary with `contains_coordinates:
    false` and a `distance_m` — treat those as needing review, not as answers.
    Anything further out comes back as `{"error": "not found"}`.
    """
    return _batched(points, "/api/subnational-lookup/", {"lat", "long"})


def check(points):
    """Verify a known code against coordinates.

    Each point: {subnational_code, lat, long, id (optional)}. Results carry
    `is_in_subnational_boundary`; an unknown code comes back as a validation
    error dict for that position instead.
    """
    return _batched(points, "/api/subnational-check/",
                    {"subnational_code", "lat", "long"})


if __name__ == "__main__":
    # Smoke test — London should resolve to England.
    print(lookup([{"id": "london", "lat": 51.5, "long": -0.12},
                  {"id": "mid-atlantic", "lat": 0, "long": -30}]))
