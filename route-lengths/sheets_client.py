"""Single auth entry point for everything in route-lengths/.

The gem-analysis service account was deleted (2026-07-31), so
`gem_tracker_constants.sheets.authorize` / `get_sheet` and the
`GDRIVE_API_CREDENTIALS` secret no longer work anywhere in this repo.

Everything here goes through the `gws` CLI instead, which exposes the raw
Sheets v4 API (`spreadsheets batchUpdate`, `values update`, ...) on top of the
work account's own OAuth token. Two profiles, deliberately separated:

  ~/.config/gws-gem         read-only scopes.  Used for every read.
  ~/.config/gws-gem-write   write scopes.      Used only when a write is asked
                            for, and only by sheet_writer.py.

This is a laptop-only design. There is no CI credential and no unattended run
(decided 2026-07-31 -- the routes-repo dispatch trigger was dropped in favour of
running this by hand), which is what makes the interactive-OAuth token usable:
it never has to leave the machine or go into a repo secret.

Requests are passed to gws as JSON on argv, so large payloads must be chunked --
macOS ARG_MAX is 1 MiB for argv plus environ combined. See MAX_ARG_BYTES.
"""

from __future__ import annotations

import json
import os
import subprocess

PIPELINES_SHEET_KEY = '1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek'
GEM_NAMING_SHEET_KEY = '1mtlwSJfWy1gbIwXVgpP3d6CcUEWo2OM0IvPD6yztGXI'

READ_CONFIG_DIR_ENV_VAR = 'ROUTE_LENGTHS_GWS_CONFIG_DIR'
WRITE_CONFIG_DIR_ENV_VAR = 'ROUTE_LENGTHS_GWS_WRITE_CONFIG_DIR'
DEFAULT_READ_CONFIG_DIR = '~/.config/gws-gem'
DEFAULT_WRITE_CONFIG_DIR = '~/.config/gws-gem-write'

# Budget for one --json argument. Well under ARG_MAX so the environment, the
# other flags and a little slack all still fit.
MAX_ARG_BYTES = 400_000


class SheetsError(RuntimeError):
    pass


class GwsBackend:
    """Sheets v4 access by shelling out to the gws CLI."""

    def __init__(self, config_dir=None, allow_write=False):
        self.allow_write = allow_write
        env_var = WRITE_CONFIG_DIR_ENV_VAR if allow_write else READ_CONFIG_DIR_ENV_VAR
        default = DEFAULT_WRITE_CONFIG_DIR if allow_write else DEFAULT_READ_CONFIG_DIR
        self.config_dir = os.path.expanduser(
            config_dir or os.environ.get(env_var) or default
        )
        if not os.path.isdir(self.config_dir):
            raise SheetsError(
                f'gws config dir not found: {self.config_dir}\n'
                f'Expected the profile set up by the '
                f'{"gws-gem-write" if allow_write else "gws-gem"} shell wrapper.'
            )

    # -- plumbing ---------------------------------------------------------

    def _env(self):
        env = dict(os.environ)
        env['GOOGLE_WORKSPACE_CLI_CONFIG_DIR'] = self.config_dir
        env['GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND'] = 'file'
        return env

    def _run(self, argv, what):
        proc = subprocess.run(
            ['gws', 'sheets'] + argv + ['--format', 'json'],
            capture_output=True, text=True, env=self._env(),
        )
        if proc.returncode != 0:
            raise SheetsError(
                f'{what} failed (exit {proc.returncode}): '
                f'{proc.stderr.strip() or proc.stdout.strip()}'
            )
        try:
            body = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise SheetsError(
                f'{what}: gws returned non-JSON: {proc.stdout[:400]!r}'
            ) from exc
        # gws reports API errors as JSON on stdout with an "error" key and still
        # exits 0, so the body has to be checked even on a clean return code.
        if isinstance(body, dict) and 'error' in body:
            raise SheetsError(f'{what}: Sheets API error: {body["error"]}')
        return body

    def _call(self, op, params, body=None, dry_run=False, what=None):
        argv = op + ['--params', json.dumps(params)]
        if body is not None:
            payload = json.dumps(body)
            if len(payload.encode()) > MAX_ARG_BYTES:
                raise SheetsError(
                    f'request body is {len(payload.encode()):,} bytes, over the '
                    f'{MAX_ARG_BYTES:,} argv budget -- chunk it before calling'
                )
            argv += ['--json', payload]
        if dry_run:
            argv += ['--dry-run']
        return self._run(argv, what or ' '.join(op))

    def _require_write(self):
        if not self.allow_write:
            raise SheetsError(
                'This backend is read-only. Get a write backend with '
                'get_backend(require_write=True), which uses the gws-gem-write '
                'profile.'
            )

    # -- reads ------------------------------------------------------------

    def get_metadata(self, sheet_key, fields):
        return self._call(
            ['spreadsheets', 'get'],
            {'spreadsheetId': sheet_key, 'fields': fields},
            what='spreadsheets get',
        )

    def read(self, sheet_key, a1_range, render='FORMATTED_VALUE'):
        body = self.batch_get(sheet_key, [a1_range], render=render)
        return body[0]

    def batch_get(self, sheet_key, a1_ranges, render='FORMATTED_VALUE'):
        """Read several ranges at once. Returns a list of `values` lists."""
        body = self._call(
            ['spreadsheets', 'values', 'batchGet'],
            {'spreadsheetId': sheet_key,
             'ranges': list(a1_ranges),
             'valueRenderOption': render},
            what='values batchGet',
        )
        return [vr.get('values', []) for vr in body.get('valueRanges', [])]

    # -- writes -----------------------------------------------------------

    def batch_update(self, sheet_key, requests, dry_run=False):
        self._require_write()
        if not requests:
            return {}
        return self._call(
            ['spreadsheets', 'batchUpdate'],
            {'spreadsheetId': sheet_key},
            {'requests': list(requests)},
            dry_run=dry_run,
            what='spreadsheets batchUpdate',
        )

    def values_update(self, sheet_key, a1_range, values,
                      value_input_option='RAW', dry_run=False):
        self._require_write()
        return self._call(
            ['spreadsheets', 'values', 'update'],
            {'spreadsheetId': sheet_key,
             'range': a1_range,
             'valueInputOption': value_input_option},
            {'values': values},
            dry_run=dry_run,
            what=f'values update {a1_range}',
        )

    def values_clear(self, sheet_key, a1_range, dry_run=False):
        self._require_write()
        return self._call(
            ['spreadsheets', 'values', 'clear'],
            {'spreadsheetId': sheet_key, 'range': a1_range},
            {},
            dry_run=dry_run,
            what=f'values clear {a1_range}',
        )


def get_backend(require_write=False):
    """Read backend by default; the write profile only when asked for."""
    return GwsBackend(allow_write=require_write)


def read_range(sheet_key, a1_range, backend=None):
    """Return the raw `values` list for an A1 range."""
    return (backend or get_backend()).read(sheet_key, a1_range)


def read_table(sheet_key, tab, header_row=1, last_column='ZZ', backend=None):
    """Read a tab into (header, rows), mimicking pygsheets get_as_df(start=...).

    header_row is 1-indexed and matches the sheet's own row numbering, so the
    notebook's `start='A3'` becomes header_row=3. Rows are right-padded to the
    header width; trailing all-empty rows are dropped.
    """
    values = read_range(sheet_key, f"'{tab}'!A{header_row}:{last_column}", backend=backend)
    if not values:
        raise SheetsError(f'{tab!r} returned no values at row {header_row}')
    header = [str(h).strip() for h in values[0]]
    width = len(header)
    rows = []
    for raw in values[1:]:
        row = (list(raw) + [''] * width)[:width]
        if any(str(cell).strip() for cell in row):
            rows.append(row)
    return header, rows


def read_dataframe(sheet_key, tab, header_row=1, last_column='ZZ', backend=None):
    """read_table as a DataFrame. Imported lazily so this module stays cheap."""
    import pandas as pd

    header, rows = read_table(
        sheet_key, tab, header_row=header_row, last_column=last_column, backend=backend
    )
    return pd.DataFrame(rows, columns=header)
