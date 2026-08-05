# route-lengths

Computes pipeline lengths and per-country splits from normalized route geometry,
for three backend tabs of **Pipelines (Gas/Oil/NGL) - main**:

| tab | what it gets |
|--|--|
| `Length estimates by pipeline` | one geodetic length per ProjectID |
| `Country ratios by pipeline` | length and fraction per country per pipeline |
| `Country dictionary` | the region/alias definitions the other two look up |

Moved here from `releases/estimate-length/` and rewritten as a module plus a thin
notebook. It replaces the old export-to-`.xlsx`-and-paste-by-hand step: it writes
both tabs itself, preserving their formulas, banding and filter ranges.

It is **triggered by hand** — there is no cron and no routes-repo dispatch
(decided 2026-07-31). That is what keeps the whole thing on one laptop with no
CI credential.

## Layout

```
route_lengths.py        the calculation: lengths, country split, reconciliation
prepare_boundaries.py   builds the boundary layer; owns the dictionary change set
sheets_client.py        the single auth entry point for all Google Sheets access
sheet_writer.py         writes all three tabs, preserving their structure
boundaries.json         committed: source versions, DOIs, SHA-256s
boundaries-attribution.csv  committed: every polygon → GEM entity, and why
estimate-length.ipynb   thin wrapper for interactive runs
```

The boundary layer itself (`boundaries-*.gpkg`) is a build artifact and is
gitignored. Rebuild it locally, or fetch the prepped copy from the "Automation
inputs" folder on the work Drive.

## Running it

```bash
pip install -r requirements.txt

# occasionally: rebuild the boundary layer (~5 s)
python prepare_boundaries.py

# preview / apply the Country dictionary change set (needs per-edit approval)
python prepare_boundaries.py --emit-dictionary-diff
python prepare_boundaries.py --apply-dictionary-diff --validate-write
python prepare_boundaries.py --apply-dictionary-diff

# compute and report, writing nothing (~1 min)
python route_lengths.py --out-dir /tmp/lengths

# same, but also build the write plan and validate every API request locally
python route_lengths.py --validate-write

# do it for real
python route_lengths.py --write
```

`route_lengths.py` defaults to `--dry-run`: it prints a reconciliation report and
the write plan, and exits non-zero if anything looks wrong. `--write` refuses to
run at all if the reconciliation report found problems, and re-reads the sheet
afterwards to confirm the row extents, the banded range and the formula block all
line up.

Useful flags: `--keep-note` leaves the length tab's A1 stamp alone;
`--fill-formulas new-rows` limits the formula fill to rows the write adds.

## How attribution works

Every EEZ polygon resolves to a GEM entity by four ordered rules. All 328 resolve;
if that ever stops being true the build fails loudly rather than dropping
kilometres on the floor.

| rule | resolves |
|--|--|
| the polygon's `UNION` name matches a `Country dictionary` row | 257 |
| it matches that row's `EEZNamesIfDifferent` alias | 17 |
| `ISO_TER1` is a GEM alpha-3 | 37 |
| `ISO_SOV1` is a GEM alpha-3 (falls back to the sovereign) | 17 |

The first two rules carry far more than they used to: the 2026-08-03 dictionary
change set added 37 named joint/disputed rows and repointed 7 stale aliases, so
polygons that used to fall through to rule (b) — and be credited silently to
whichever ISO party came first — now resolve by name.

Five GEM entities have no EEZ polygon of their own and are cut out of their
parent's geometry using Natural Earth: Hong Kong and Macao (from China), Åland
(Finland), British Indian Ocean Territory (UK), Kosovo (Serbia). The Joint
Petroleum Development Area has no geometry in any source, correctly — the Timor
Sea JPDA lapsed in 2019.

**Region comes from geography, not sovereignty.** An entity with its own
dictionary row uses that row; anything else takes the region of the physically
nearest country. This is why the Canary Islands need no special case any more,
and it is what GEM already does for Réunion and Mayotte (Africa) and New
Caledonia and French Polynesia (Oceania) — all of which sovereignty-inheritance
gets wrong. Named joint areas are never collapsed to one party.

## Reading the reconciliation report

Two numbers can be non-zero and mean opposite things:

- **`unattributed_km`** — route length outside every boundary polygon. Should be
  ~0 (it currently is, for all 5,233 routes). Anything large is a hole in the
  boundary layer.
- **`overlap_km`** — length counted twice because a named joint area overlaps a
  claimant's own polygon. Expected under the default `--overlap-policy keep`;
  currently 50 pipelines, nearly all slivers. It dilutes a claimant's share
  inside that zone, since fractions are normalised by the clipped total.

## What a write actually does

The two tabs are not plain value dumps, so the writer sizes the grid first and
only then fills it:

1. `insertDimension` / `deleteDimension` so the grid matches the new row count
   (`inheritFromBefore: true`, so formats follow)
2. on the ratios tab, `copyPaste` with `PASTE_FORMULA` from row 2 to fill the 28
   formula columns G:AH — never retyped, so the relative row references follow
3. resize the banded range and the saved filter views, which otherwise keep
   pointing at whatever extent they were saved at
4. `values.update` the pasted columns (A:B on lengths, A:F on ratios), chunked at
   1,000 rows because `gws` takes request bodies on argv and ARG_MAX is 1 MiB
5. re-read and verify

Column X on the ratios tab holds a broken `INDEX(#REF!, …)` in *every* row. It is
pre-existing and left alone; the fill propagates it unchanged rather than
introducing anything new.

## Auth

The `gem-analysis` service account was deleted on 2026-07-31, so
`gem_tracker_constants.sheets` and `GDRIVE_API_CREDENTIALS` no longer work
anywhere. Everything here goes through the `gws` CLI, which exposes the raw
Sheets v4 API on the work account's own OAuth token:

| | profile | scopes |
|--|--|--|
| reads | `~/.config/gws-gem` | read-only |
| writes | `~/.config/gws-gem-write` | write |

No service account, no repo secret, no CI credential — which is only safe
*because* runs are manual. The `gws-gem-write` refresh token carries
Drive/Gmail/Calendar scope for the whole work account and must never go into a
GitHub secret, especially with these repos public.

## Writing the `Country dictionary`

`--apply-dictionary-diff` applies the change set to a third tab. That tab is
grouped by Region/SubRegion and alphabetical within group — *not* sorted by name —
and three rows carry manual cell formatting, so rows are moved with
insert/`deleteDimension` rather than by rewriting the grid, and the formatting
travels with the row. New rows are placed inside the correct block; a row whose
region is corrected is moved to rejoin its block, resolving the cheapest split
first so one misfiled row does not drag its whole neighbourhood with it.

Before sending anything it replays the entire request sequence against a local
copy of the live rows and refuses to write unless the result matches the expected
table exactly — an off-by-one in a positional insert would otherwise shift every
row below it silently.

Applied 2026-08-03: 37 rows added, 10 deleted, 2 moved, 7 aliases repointed,
Canary Islands cleaned, and `Disputed (Iran, United Arab Emirates)` corrected
from Europe / Southern Europe to Asia / Western Asia. It still needs explicit
per-edit approval every time — it is not covered by the two-tab write carve-out.
