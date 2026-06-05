import pandas as pd
import pytest
from pathlib import Path
from voto_capital.transforms.fx import _parse_raw_fx, build_fx_changes

RAW_DIR = Path(__file__).parents[2] / "data" / "raw"


def test_parse_raw_fx_returns_series():
    result = _parse_raw_fx(RAW_DIR / "USD_CLP Historical Data.csv")
    assert isinstance(result, pd.Series)


def test_parse_raw_fx_date_index():
    result = _parse_raw_fx(RAW_DIR / "USD_CLP Historical Data.csv")
    assert isinstance(result.index, pd.DatetimeIndex)


def test_parse_raw_fx_values_are_float():
    result = _parse_raw_fx(RAW_DIR / "USD_CLP Historical Data.csv")
    assert result.dtype == float


def test_parse_raw_fx_sorted_ascending():
    result = _parse_raw_fx(RAW_DIR / "USD_CLP Historical Data.csv")
    assert result.index.is_monotonic_increasing


def test_parse_raw_fx_sign_inverted():
    # USD/CLP raw on 2026-06-02 was -0.35% (dollar fell = peso gained)
    # after inversion, stored value should be positive: +0.0035
    result = _parse_raw_fx(RAW_DIR / "USD_CLP Historical Data.csv")
    assert abs(result.loc["2026-06-02"] - 0.0035) < 1e-6


def test_parse_raw_fx_cop_no_error():
    # COP prices have thousands separators like "3,590.79" — must not crash
    result = _parse_raw_fx(RAW_DIR / "USD_COP Historical Data.csv")
    assert not result.empty


def test_build_fx_changes_returns_dataframe():
    df = build_fx_changes(RAW_DIR)
    assert isinstance(df, pd.DataFrame)


def test_build_fx_changes_columns():
    df = build_fx_changes(RAW_DIR)
    assert set(df.columns) == {"CHILE", "BRAZIL", "COLOMBIA", "MEXICO", "ARGENTINA"}


def test_build_fx_changes_date_index():
    df = build_fx_changes(RAW_DIR)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "date"


def test_build_fx_changes_sorted():
    df = build_fx_changes(RAW_DIR)
    assert df.index.is_monotonic_increasing


def test_colombia_max_single_day_move():
    # claim "peso increased >7% in a single day" is NOT supported by data:
    # max appreciation is 3.39% (2022-05-30), max depreciation is 6.23% (2020-03-09, COVID)
    df = build_fx_changes(RAW_DIR)
    assert df["COLOMBIA"].max() < 0.07
    assert df["COLOMBIA"].min() > -0.07
