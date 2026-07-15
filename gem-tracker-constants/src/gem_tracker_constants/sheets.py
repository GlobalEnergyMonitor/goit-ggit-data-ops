"""Shared Google Sheets access for GOIT/GGIT notebooks and scripts.

Canonical live-sheet keys plus the pygsheets auth boilerplate that release
and cycle notebooks otherwise re-declare inline (and drift out of sync).

Requires pygsheets (``pip install "gem-tracker-constants[sheets]"``) and the
``GDRIVE_API_CREDENTIALS`` env var holding the service-account credentials.
Release notebooks should still pin their own frozen snapshot key in their
config cell — the keys here are the *live* backends only.
"""

from __future__ import annotations

# Live tracker backend "Pipelines (Gas/Oil/NGL) - main".
PIPELINES_SHEET_KEY = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"

# Share sheets with this account (viewer is enough for read-only notebooks).
SERVICE_ACCOUNT_EMAIL = "gem-analysis@gem-analysis.iam.gserviceaccount.com"

# Env var pygsheets reads the service-account JSON from.
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
