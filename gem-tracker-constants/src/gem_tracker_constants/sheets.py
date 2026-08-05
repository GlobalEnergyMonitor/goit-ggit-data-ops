"""Shared Google Sheets access for GOIT/GGIT notebooks and scripts.

.. deprecated:: 2026-07-31
   ``authorize`` and ``get_sheet`` no longer work anywhere: the ``gem-analysis``
   service account was deleted, so ``GDRIVE_API_CREDENTIALS`` has nothing to
   authenticate as. They are kept only so existing notebooks import rather than
   crash on import. New code should read via the ``gws`` CLI — see
   ``route-lengths/sheets_client.py`` in the data-ops repo for the pattern.

``PIPELINES_SHEET_KEY`` is unaffected and remains the canonical live-backend key.
Release notebooks should still pin their own frozen snapshot key in their
config cell — the keys here are the *live* backends only.
"""

from __future__ import annotations

# Live tracker backend "Pipelines (Gas/Oil/NGL) - main".
PIPELINES_SHEET_KEY = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"

# DELETED 2026-07-31. Kept as a constant only so importers do not break; sharing
# a sheet with this address accomplishes nothing.
SERVICE_ACCOUNT_EMAIL = "gem-analysis@gem-analysis.iam.gserviceaccount.com"

# Env var pygsheets read the service-account JSON from. Dead with the account.
CREDS_ENV_VAR = "GDRIVE_API_CREDENTIALS"


def authorize(creds_env: str = CREDS_ENV_VAR):
    """Return an authorized pygsheets client (service-account via env var)."""
    try:
        import pygsheets
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "pygsheets is required for gem_tracker_constants.sheets — "
            'install with: pip install "gem-tracker-constants[sheets]"'
        ) from exc
    return pygsheets.authorize(service_account_env_var=creds_env)


def get_sheet(key: str, creds_env: str = CREDS_ENV_VAR):
    """Open a spreadsheet by key with the shared service-account auth."""
    return authorize(creds_env).open_by_key(key)


__all__ = [
    "PIPELINES_SHEET_KEY",
    "SERVICE_ACCOUNT_EMAIL",
    "CREDS_ENV_VAR",
    "authorize",
    "get_sheet",
]
