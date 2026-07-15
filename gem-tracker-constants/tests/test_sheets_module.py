"""The sheets module must import without pygsheets installed (lazy import)."""

import re

from gem_tracker_constants import sheets


def test_module_imports_without_pygsheets():
    # importing the module itself must never require pygsheets
    assert callable(sheets.authorize)
    assert callable(sheets.get_sheet)


def test_canonical_key_shapes():
    assert re.fullmatch(r"[A-Za-z0-9_-]{40,}", sheets.PIPELINES_SHEET_KEY)
    assert sheets.SERVICE_ACCOUNT_EMAIL.endswith(".iam.gserviceaccount.com")
    assert sheets.CREDS_ENV_VAR == "GDRIVE_API_CREDENTIALS"
