import pytest
import pandas as pd
from pathlib import Path
from voto_capital.loaders.etf import load_etf

DATA_DIR = Path(__file__).parents[2] / "data"


def test_load_etf_returns_dataframe():
    df = load_etf(DATA_DIR / "etf_ech.csv")
    assert isinstance(df, pd.DataFrame)


def test_load_etf_columns():
    df = load_etf(DATA_DIR / "etf_ech.csv")
    assert set(df.columns) >= {"price", "change_pct"}


def test_load_etf_date_index():
    df = load_etf(DATA_DIR / "etf_ech.csv")
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "date"


def test_load_etf_price_is_float():
    df = load_etf(DATA_DIR / "etf_ech.csv")
    assert df["price"].dtype == float


def test_load_etf_change_pct_is_float_decimal():
    df = load_etf(DATA_DIR / "etf_ech.csv")
    assert df["change_pct"].dtype == float
    # values should be in decimal form, not percentage strings
    assert df["change_pct"].abs().max() < 10.0


def test_load_etf_missing_volume_rows_kept():
    # rows with empty Vol. must be retained (not dropped)
    df = load_etf(DATA_DIR / "etf_ech.csv")
    assert len(df) == 1892


def test_load_etf_sorted_ascending():
    df = load_etf(DATA_DIR / "etf_ech.csv")
    assert df.index.is_monotonic_increasing


def test_load_etf_no_duplicate_dates():
    df = load_etf(DATA_DIR / "etf_ech.csv")
    assert not df.index.duplicated().any()
