import pytest
from pathlib import Path
from voto_capital.loaders.elections import load_elections

DATA_DIR = Path(__file__).parents[2] / "data"


def test_load_elections_returns_list():
    result = load_elections(DATA_DIR / "elections.json")
    assert isinstance(result, list)


def test_load_elections_required_keys():
    result = load_elections(DATA_DIR / "elections.json")
    for entry in result:
        assert "country" in entry
        assert "first_round" in entry
        assert "wing" in entry


def test_load_elections_skips_empty_first_round():
    result = load_elections(DATA_DIR / "elections.json")
    for entry in result:
        assert entry["first_round"] != ""


def test_load_elections_dates_are_timestamps():
    import pandas as pd
    result = load_elections(DATA_DIR / "elections.json")
    for entry in result:
        assert isinstance(entry["first_round"], pd.Timestamp)
        if entry["second_round"] is not None:
            assert isinstance(entry["second_round"], pd.Timestamp)


def test_load_elections_second_round_none_when_empty():
    result = load_elections(DATA_DIR / "elections.json")
    mexico = next(e for e in result if e["country"] == "MEXICO")
    assert mexico["second_round"] is None
