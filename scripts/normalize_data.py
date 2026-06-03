"""
Run once to normalize all raw ETF CSVs to a canonical format and rename them.

Usage:
    uv run python scripts/normalize_data.py

Output:
    - Rewrites each file in data/raw/ with a clean ticker-based name
    - Canonical format: YYYY-MM-DD dates, period decimals, standard column names
    - Updates data/mapping_countries_files.json
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MAPPING_PATH = DATA_DIR / "mapping_countries_files.json"

CANONICAL_COLUMNS = ["Date", "Price", "Open", "High", "Low", "Vol.", "Change %"]

_GERMAN_RENAME = {
    "Datum": "Date",
    "Zuletzt": "Price",
    "Eröffn.": "Open",
    "Hoch": "High",
    "Tief": "Low",
    "+/- %": "Change %",
}


def _detect_locale(df: pd.DataFrame) -> str:
    if "Datum" in df.columns:
        df = df.rename(columns=_GERMAN_RENAME)

    sample_date = str(df["Date"].dropna().iloc[0])

    if "." in sample_date:
        return "de"

    if "/" in sample_date:
        first_parts = df["Date"].dropna().astype(str).str.split("/").str[0].astype(int)
        if (first_parts > 12).any():
            raise ValueError(
                "Dates contain first-part values > 12 — this looks like DD/MM/YYYY, "
                "but only MM/DD/YYYY is supported. Fix the source file."
            )
        # All first parts ≤ 12: format is ambiguous, assuming MM/DD/YYYY (Investing.com default)
        print("  ⚠ date format ambiguous (all first-parts ≤ 12), assuming MM/DD/YYYY")
        return "us"

    raise ValueError(f"Cannot detect date format from sample: {sample_date!r}")


def _parse_german_number(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )


def _to_canonical(df: pd.DataFrame, locale: str) -> pd.DataFrame:
    if "Datum" in df.columns:
        df = df.rename(columns=_GERMAN_RENAME)

    if locale == "de":
        for col in ["Price", "Open", "High", "Low", "Change %"]:
            df[col] = _parse_german_number(df[col])
        df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y").dt.strftime("%Y-%m-%d")
    else:
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y").dt.strftime("%Y-%m-%d")

    return df[CANONICAL_COLUMNS]


def _ticker_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    if stem.startswith("etf_"):
        return stem[4:]
    match = re.match(r"([A-Z]+)", stem)
    if not match:
        raise ValueError(f"Cannot extract ticker from filename: {filename}")
    return match.group(1).lower()


def normalize(src_path: Path) -> Path:
    raw = pd.read_csv(src_path)
    locale = _detect_locale(raw)
    canonical = _to_canonical(raw, locale)

    ticker = _ticker_from_filename(src_path.name)
    target_path = RAW_DIR / f"etf_{ticker}.csv"

    canonical.to_csv(target_path, index=False)

    if src_path != target_path:
        src_path.unlink()
        print(f"  {src_path.name} → {target_path.name}  [{locale}]")
    else:
        print(f"  {target_path.name}  [{locale}]")

    return target_path


def main() -> None:
    with MAPPING_PATH.open() as f:
        mapping: dict[str, list[str]] = json.load(f)

    new_mapping: dict[str, list[str]] = {}
    for country, files in mapping.items():
        print(f"{country}")
        new_mapping[country] = []
        for rel_path in files:
            src = DATA_DIR / rel_path
            target = normalize(src)
            new_mapping[country].append(f"{target.name}")

    with MAPPING_PATH.open("w") as f:
        json.dump(new_mapping, f, indent=2)
    print("\nmapping_countries_files.json updated.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
