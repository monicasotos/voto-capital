import pandas as pd
import pytest
from pathlib import Path
from voto_capital.transforms.etf import read_raw_etf, raw_to_clean_filename, is_raw_etf_file

RAW_DIR = Path(__file__).parents[2] / "data" / "raw"
ARGT_RAW = RAW_DIR / "ARGT ETF Stock Price History.csv"


def test_read_raw_etf_returns_dataframe():
    df = read_raw_etf(ARGT_RAW)
    assert isinstance(df, pd.DataFrame)


def test_read_raw_etf_columns():
    df = read_raw_etf(ARGT_RAW)
    assert list(df.columns) == ["Price", "Open", "High", "Low", "Vol.", "Change %"]


def test_read_raw_etf_date_index():
    df = read_raw_etf(ARGT_RAW)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "Date"


def test_read_raw_etf_sorted_ascending():
    df = read_raw_etf(ARGT_RAW)
    assert df.index.is_monotonic_increasing


def test_read_raw_etf_price_is_float():
    df = read_raw_etf(ARGT_RAW)
    assert df["Price"].dtype == float


def test_raw_to_clean_filename():
    assert raw_to_clean_filename(Path("ARGT ETF Stock Price History.csv")) == "etf_argt.csv"
    assert raw_to_clean_filename(Path("ECH ETF Stock Price History.csv")) == "etf_ech.csv"


def test_is_raw_etf_file_true():
    assert is_raw_etf_file(Path("ARGT ETF Stock Price History.csv"))


def test_is_raw_etf_file_false_for_fx():
    assert not is_raw_etf_file(Path("USD_CLP Historical Data.csv"))
