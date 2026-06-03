import pandas as pd
from pathlib import Path

RAW_FILE_MAP = {
    "CHILE": "USD_CLP Historical Data.csv",
    "BRAZIL": "USD_BRL Historical Data.csv",
    "COLOMBIA": "USD_COP Historical Data.csv",
    "MEXICO": "USD_MXN Historical Data.csv",
    "ARGENTINA": "USD_ARS Historical Data.csv"
}


def _parse_raw_fx(path: Path | str) -> pd.Series:
    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        usecols=["Date", "Change %"],
    )
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df["change_pct"] = df["Change %"].str.rstrip("%").astype(float) / 100.0
    df = df.set_index("Date").sort_index()
    # invert: positive = local currency appreciated vs USD
    return -df["change_pct"]


def build_fx_changes(raw_dir: Path | str) -> pd.DataFrame:
    raw_dir = Path(raw_dir)
    df = pd.DataFrame({
        country: _parse_raw_fx(raw_dir / filename)
        for country, filename in RAW_FILE_MAP.items()
    })
    df.index.name = "date"
    return df.sort_index()


if __name__ == "__main__":
    import sys

    raw_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/fx_changes.csv")
    result = build_fx_changes(raw_dir)
    result.to_csv(out_path)
    print(f"Written {len(result)} rows to {out_path}")
