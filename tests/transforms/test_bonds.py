import pandas as pd
import pytest
from pathlib import Path
from voto_capital.transforms.bonds import build_bond_changes

RAW_DIR = Path(__file__).parents[2] / "data" / "raw"


def test_build_bond_changes_returns_dataframe():
    df = build_bond_changes(RAW_DIR)
    assert isinstance(df, pd.DataFrame)


def test_build_bond_changes_columns():
    df = build_bond_changes(RAW_DIR)
    assert set(df.columns) == {"CHILE", "BRAZIL", "COLOMBIA", "MEXICO", "ARGENTINA", "USA"}


def test_build_bond_changes_date_index():
    df = build_bond_changes(RAW_DIR)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "date"


def test_build_bond_changes_sorted():
    df = build_bond_changes(RAW_DIR)
    assert df.index.is_monotonic_increasing


def test_build_bond_changes_values_are_float():
    df = build_bond_changes(RAW_DIR)
    for col in df.columns:
        assert df[col].dtype == float


def test_build_bond_changes_sign_not_inverted():
    # positive change_pct = yield went up (risk premium widened) — must NOT be inverted
    df = build_bond_changes(RAW_DIR)
    # Brazil on 2026-06-03 had raw Change % = 1.79%, stored value must be positive
    assert df.loc["2026-06-03", "BRAZIL"] == pytest.approx(0.0179, abs=1e-4)


def test_build_bond_changes_countries_have_different_start_dates():
    df = build_bond_changes(RAW_DIR)
    # Chile starts 2010, Argentina starts 2017 — rows before Argentina's start must be NaN
    early = df.loc[:"2017-09-01", "ARGENTINA"]
    assert early.isna().all()
