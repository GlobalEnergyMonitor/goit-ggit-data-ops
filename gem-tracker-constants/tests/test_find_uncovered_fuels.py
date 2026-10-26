import pytest

from gem_tracker_constants import find_uncovered_fuels


def test_known_fuels_are_covered(capsys):
    assert find_uncovered_fuels(["Gas", "Oil", "NGL", "LPG"]) == []
    assert "all fuel values covered" in capsys.readouterr().out


def test_unknown_fuels_are_reported(capsys):
    out = find_uncovered_fuels(["Gas", "Oil ", "Crude", "Crude"])
    assert out == ["Crude", "Oil "]
    printed = capsys.readouterr().out
    assert "'Oil '" in printed  # repr makes the trailing space visible
    assert "'Crude'" in printed


def test_none_and_nan_are_ignored():
    assert find_uncovered_fuels(["Gas", None], verbose=False) == []


def test_bucket_subset_narrows_coverage():
    # 'Gas' is not in the oil/ngl buckets, so it surfaces when the check is
    # restricted to those.
    assert find_uncovered_fuels(["Gas", "Oil"], buckets=["oil", "ngl"], verbose=False) == ["Gas"]


def test_accepts_dataframe_and_series():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"Fuel": ["Gas", "Mystery juice", float("nan")]})
    assert find_uncovered_fuels(df, verbose=False) == ["Mystery juice"]
    assert find_uncovered_fuels(df["Fuel"], verbose=False) == ["Mystery juice"]


def test_case_and_aliases_are_covered():
    # the gas tab went lowercase in October 2026; coke oven gas is an alias
    assert find_uncovered_fuels(
        ["gas", "gas and hydrogen", "oil", "coke oven gas"], verbose=False
    ) == []


def test_normalize_fuels_rewrites_to_bucket_spelling():
    pd = pytest.importorskip("pandas")
    from gem_tracker_constants import GAS_FUEL_OPTIONS, normalize_fuels

    df = pd.DataFrame({"Fuel": ["gas", " Gas and hydrogen ", "coke oven gas",
                                "oil", "Mystery juice", None]})
    normalize_fuels(df)
    assert df["Fuel"].tolist()[:5] == ["Gas", "Gas and Hydrogen", "Gas", "Oil",
                                        "Mystery juice"]
    assert df["Fuel"].isin(GAS_FUEL_OPTIONS).sum() == 3


def test_aliases_point_at_bucket_entries():
    from gem_tracker_constants import FUEL_ALIASES, FUELS

    entries = {v for bucket in FUELS.values() for v in bucket}
    assert set(FUEL_ALIASES.values()) <= entries
    assert "aliases" not in FUELS
